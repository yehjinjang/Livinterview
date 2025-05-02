import asyncio
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage

from chatbot_core.memory.session_memory import memory
from chatbot_core.chains import (
    check_completion_chain,
    controlnet_chain,
    question_check_chain,
    summary_chain,
    extract_structure_chain,
    check_agreement_chain,
    furniture_warning_chain
)
from chatbot_core.prompts import chat_prompt, summary_prompt, system_prompt, furniture_warning_prompt
from chatbot_core.logic.common import count_unique_furniture_mentions
from pathlib import Path

from langchain.chains import LLMChain

def save_prompt_to_txt(prompt: str, filename: str = "controlnet_prompt.txt"):
    save_path = Path(__file__).parent / filename
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(prompt)

async def stream_fixed_message(text: str, delay: float = 0.03):
    for chunk in text:
        yield chunk
        await asyncio.sleep(delay)

async def stream_initialize_response(image_url: str):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        temperature=0.5,
        callbacks=[callback]
    )

    messages = [
        system_prompt,
        HumanMessage(
            content=[
                {"type": "text", "text": "이 방의 구조, 벽지, 바닥, 창문 위치를 설명하고 어울리는 인테리어를 제안해줘."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )
    ]

    task = asyncio.create_task(llm.ainvoke(messages))

    full_response = ""
    async for token in callback.aiter():
        yield token
        full_response += token

    await task

    structure_desc = extract_structure_chain.run({"response": full_response}).strip()
    memory.chat_memory.add_ai_message(f"[방 구조] {structure_desc}")

    yield "__END__STREAM__"

async def stream_response(user_input: str, history: str, prompt_template=chat_prompt):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0.5, callbacks=[callback])
    chain = prompt_template | llm
    task = asyncio.create_task(chain.ainvoke({"user_input": user_input, "history": history}))

    full_response = ""
    async for token in callback.aiter():
        yield token
        full_response += token

    await task
    memory.chat_memory.add_ai_message(full_response)
    yield "__END__STREAM__"

async def stream_summary(conversation: str):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0.3, callbacks=[callback])
    chain = summary_prompt | llm
    task = asyncio.create_task(chain.ainvoke({"conversation": conversation}))

    summary = ""
    async for token in callback.aiter():
        summary += token
        yield token

    await task
    memory.chat_memory.add_ai_message(summary)
    existing = [m.content for m in memory.chat_memory.messages]
    if "SUMMARY_PENDING_CONFIRMATION" not in existing:
        memory.chat_memory.add_ai_message("SUMMARY_PENDING_CONFIRMATION")

    yield "__END__STREAM__"

async def run_initial_prompt(image_url: str):
    async for token in stream_initialize_response(image_url):
        yield token

async def run_user_turn(user_input: str):
    memory.chat_memory.add_user_message(user_input)
    ai_messages = [m.content for m in memory.chat_memory.messages if m.type == "ai"]

    if ai_messages and ai_messages[-1] == "SUMMARY_PENDING_CONFIRMATION":
        last_summary = ai_messages[-2] if len(ai_messages) >= 2 else ""
        result = check_agreement_chain.run(gpt_response=last_summary, text=user_input).strip().upper()
        memory.chat_memory.messages = [
            m for m in memory.chat_memory.messages if m.content != "SUMMARY_PENDING_CONFIRMATION"
        ]

        if result == "YES":
            prompt_text = controlnet_chain.run(summary=last_summary).strip().strip('"')
            final_prompt = prompt_text + " Do not change the room’s layout, dimensions, wallpaper color, floor material, or the positions of the windows and doors, as they are fixed based on the uploaded image."
            save_prompt_to_txt(final_prompt)
            async for chunk in stream_fixed_message("좋아! 이대로 방을 꾸며볼게. 잠시 기다려줘."):
                yield chunk
            yield "__END__STREAM__"
            return
        else:
            async for chunk in stream_fixed_message("바꾸고 싶거나 더 필요한 가구가 있을까?"):
                yield chunk
            yield "__END__STREAM__"
            return

    structure_context = next(
        (m.content.replace("[방 구조]", "").strip() for m in memory.chat_memory.messages if m.content.startswith("[방 구조]")),
        ""
    )

    dynamic_chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt.content + f"\n\n참고로, 이 방은 다음과 같아: {structure_context}"),
        ("human", """
지금까지 사용자와 나눈 대화야:

{history}

이제 사용자가 이렇게 말했어:
"{user_input}"

맥락을 반영해서 자연스럽게 반말로 답변해줘.
""")
    ])

    full_conversation = "\n".join(
        m.content for m in memory.chat_memory.messages
        if m.type in ("human", "ai") and not m.content.startswith("[가구 경고]")
    )
    only_user_conversation = "\n".join(
        m.content for m in memory.chat_memory.messages
        if m.type == "human" and not m.content.startswith("[가구 경고]")
    )

    if check_completion_chain.run(text=user_input).strip().upper() == "YES":
        async for token in stream_summary(full_conversation):
            if token != "__END__STREAM__":
                yield token
        return
    
    already_warned = any("[가구 경고]" in m.content for m in memory.chat_memory.messages)

    if not already_warned and count_unique_furniture_mentions(only_user_conversation) == 6:
        warning = furniture_warning_chain.run({"conversation": full_conversation}).strip()
        memory.chat_memory.add_ai_message(f"[가구 경고] {warning}")
        async for chunk in stream_fixed_message(warning):
            yield chunk
        yield "__END__STREAM__"
        return

    if question_check_chain.run(text=user_input).strip().upper() == "YES":
        async for token in stream_response(user_input, full_conversation, prompt_template=dynamic_chat_prompt):
            if token != "__END__STREAM__":
                yield token
        return

    async for token in stream_response(user_input, full_conversation, prompt_template=dynamic_chat_prompt):
        if token != "__END__STREAM__":
            yield token
