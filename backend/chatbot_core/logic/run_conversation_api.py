import asyncio
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages import SystemMessage, HumanMessage

from chatbot_core.memory.session_memory import memory
from chatbot_core.chains import (
    extract_proposal_chain,
    check_agreement_chain,
    check_completion_chain,
    check_prompt_chain,
    controlnet_chain,
    followup_chain,
    furniture_warning_chain,
    question_check_chain,
    summary_chain
)
from chatbot_core.prompts import chat_prompt, summary_prompt
from chatbot_core.logic.common import count_unique_furniture_mentions

from pathlib import Path

def save_prompt_to_txt(prompt: str, filename: str = "controlnet_prompt.txt"):
    save_path = Path(__file__).parent / filename
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(prompt)

async def stream_initialize_response(image_url: str):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(
        model="gpt-4o",
        streaming=True,
        temperature=0.5,
        callbacks=[callback]
    )
    
    chain = chat_prompt | llm

    user_input = "이 방의 벽지 색, 바닥 톤, 구조, 창문 위치를 설명하고 어울리는 인테리어를 제안해줘."
    history = f"사용자가 방 사진을 올렸어. 사진 URL은 {image_url} 이야."

    task = asyncio.create_task(chain.ainvoke({
        "user_input": user_input,
        "history": history
    }))

    full_response = ""
    async for token in callback.aiter():
        yield token
        full_response += token

    await task

    memory.chat_memory.clear()
    memory.chat_memory.add_user_message("이 방 어떻게 꾸미면 좋을까? (이미지 포함)")
    memory.chat_memory.add_ai_message(full_response)

    yield "__END__STREAM__"


async def stream_response(user_input: str, history: str):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0.5, callbacks=[callback])
    chain = chat_prompt | llm
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

    # 중복 방지: 이미 있으면 추가 안 함
    memory.chat_memory.add_ai_message(summary)
    existing = [m.content for m in memory.chat_memory.messages]
    if "SUMMARY_PENDING_CONFIRMATION" not in existing:
        memory.chat_memory.add_ai_message("SUMMARY_PENDING_CONFIRMATION")

    yield "__END__STREAM__"


async def stream_followup(conversation: str):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(model="gpt-4o", streaming=True, temperature=0.3, callbacks=[callback])
    chain = followup_chain.prompt | llm
    task = asyncio.create_task(chain.ainvoke({"conversation": conversation}))

    followup = ""
    async for token in callback.aiter():
        followup += token
        yield token

    await task
    yield "__END__STREAM__"


async def run_initial_prompt(image_url: str):
    async for token in stream_initialize_response(image_url):
        yield token


async def run_user_turn(user_input: str):
    memory.chat_memory.add_user_message(user_input)

    ai_messages = [m.content for m in memory.chat_memory.messages if m.type == "ai"]

    # 요약 동의 여부 확인 흐름
    if ai_messages and ai_messages[-1] == "SUMMARY_PENDING_CONFIRMATION":
        last_summary = ai_messages[-2] if len(ai_messages) >= 2 else ""
        result = check_agreement_chain.run(gpt_response=last_summary, text=user_input).strip().upper()

        # 요약 후 상태 초기화 (이 부분 추가!)
        memory.chat_memory.messages = [
            m for m in memory.chat_memory.messages
            if m.content != "SUMMARY_PENDING_CONFIRMATION"
        ]

        if result == "YES":
            prompt_text = controlnet_chain.run(summary=last_summary).strip().strip('"')
            final_prompt = prompt_text + " Do not change the room’s layout, dimensions, wallpaper color, floor material, or the positions of the windows and doors, as they are fixed based on the uploaded image."
            
            # 프롬프트 txt로 저장
            save_prompt_to_txt(final_prompt)

            yield "좋아! 이대로 방을 꾸며볼게. 잠시 기다려줘."
            return
        else:
            yield "그럼 바꾸고 싶은 부분이 있을까?"
            return

    last_ai_response = ai_messages[-1] if ai_messages else ""
    proposals = extract_proposal_chain.run(response=last_ai_response)
    extracted = [p.strip() for p in proposals.split("\n") if p.strip()]

    matched = []
    for p in extracted:
        result = check_agreement_chain.run(gpt_response=p, text=user_input).strip().upper()
        if result == "YES":
            matched.append(p)

    approved_contents = []
    if matched:
        approved_contents.append(". ".join(matched) + ".")

    history = memory.load_memory_variables({})["chat_history"]
    full_conversation = "\n".join(approved_contents + [str(m.content) for m in history])

    if check_completion_chain.run(text=user_input).strip().upper() == "YES":
        if check_prompt_chain.run(conversation=full_conversation).strip().upper() == "YES":
            async for token in stream_summary(full_conversation):
                if token != "__END__STREAM__":
                    yield token
            return
        else:
            async for token in stream_followup(full_conversation):
                if token != "__END__STREAM__":
                    yield token
            return

    if count_unique_furniture_mentions(full_conversation) >= 6:
        warning = furniture_warning_chain.run(conversation=full_conversation)
        memory.chat_memory.add_ai_message(warning)
        yield warning
        yield "__END__STREAM__"
        return

    if question_check_chain.run(text=user_input).strip().upper() == "YES":
        async for token in stream_response(user_input, history):
            if token != "__END__STREAM__":
                yield token
        return

    async for token in stream_response(user_input, history):
        if token != "__END__STREAM__":
            yield token
    return
