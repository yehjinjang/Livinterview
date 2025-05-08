import asyncio
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage

from chatbot_core.memory.session_memory import memory
from chatbot_core.chains.check_completion_chain import get_check_completion_chain
from chatbot_core.chains.extract_structure_chain import get_extract_structure_chain
from chatbot_core.chains.check_agreement_chain import get_check_agreement_chain
from chatbot_core.chains.furniture_warning_chain import get_furniture_warning_chain
from chatbot_core.prompts import chat_prompt, summary_prompt, system_prompt
from chatbot_core.logic.common import count_unique_furniture_mentions


async def stream_fixed_message(text: str, delay: float = 0.03):
    for chunk in text:
        yield chunk
        await asyncio.sleep(delay)


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

    memory.chat_memory.messages = [
        m for m in memory.chat_memory.messages
        if not m.content.startswith("지금까지 대화한 내용을 정리해봤어")
    ]
    memory.chat_memory.add_ai_message(summary)

    if "SUMMARY_PENDING_CONFIRMATION" not in [m.content for m in memory.chat_memory.messages]:
        memory.chat_memory.add_ai_message("SUMMARY_PENDING_CONFIRMATION")

    yield "__END__STREAM__"


async def run_initial_prompt(blank_room_url: str):
    callback = AsyncIteratorCallbackHandler()
    llm = ChatOpenAI(model="gpt-4o", streaming=True, callbacks=[callback])
    messages = [
        system_prompt,
        HumanMessage(content=f"""
다음은 사용자가 올린 빈 방 사진이야: {blank_room_url}

벽지 색, 바닥 색, 전체적인 구조를 먼저 설명해줘. 그리고 어울리는 가구나 배치 스타일을 제안하고,
마무리로 사용자의 취향이나 의견을 물어봐.
"""),
    ]
    task = asyncio.create_task(llm.ainvoke(messages))
    full_response = ""

    async for token in callback.aiter():
        yield token
        full_response += token

    await task

    structure_desc = get_extract_structure_chain().run({"response": full_response}).strip()
    memory.chat_memory.add_ai_message(f"[방 구조] {structure_desc}")

    yield "__END__STREAM__"


async def run_user_turn(user_input: str):
    memory.chat_memory.add_user_message(user_input)
    ai_messages = [m.content for m in memory.chat_memory.messages if m.type == "ai"]

    full_conversation = "\n".join(
        m.content for m in memory.chat_memory.messages
        if m.type in ("human", "ai") and not m.content.startswith("[가구 경고]")
    )
    only_user_conversation = "\n".join(
        m.content for m in memory.chat_memory.messages
        if m.type == "human" and not m.content.startswith("[가구 경고]")
    )

    structure_context = next(
        (m.content.replace("[방 구조]", "").strip()
         for m in memory.chat_memory.messages if m.content.startswith("[방 구조]")),
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

    if ai_messages and ai_messages[-1] == "SUMMARY_PENDING_CONFIRMATION":
        last_summary = ai_messages[-2] if len(ai_messages) >= 2 else ""
        result = get_check_agreement_chain().run(gpt_response=last_summary, text=user_input).strip().upper()
        memory.chat_memory.messages = [m for m in memory.chat_memory.messages if m.content != "SUMMARY_PENDING_CONFIRMATION"]

        if result == "YES":
            detailed = memory.variables.get("detailed_structure", "")
            final_summary = f"{detailed} Also, here’s a quick recap: {last_summary}" if last_summary else detailed
            memory.variables["confirmed_summary"] = final_summary
            async for chunk in stream_fixed_message("좋아! 그럼 지금까지 얘기한 걸로 방을 꾸며볼게. 조금만 기다려줘."):
                yield chunk
            yield "__END__STREAM__"
            return
        else:
            async for chunk in stream_response(user_input, full_conversation, prompt_template=dynamic_chat_prompt):
                if chunk != "__END__STREAM__":
                    yield chunk
            return

    if get_check_completion_chain().run(text=user_input).strip().upper() == "YES":
        async for chunk in stream_fixed_message("좋아, 그럼 이대로 꾸며볼게! 오른쪽 아래 '인테리어 생성' 버튼을 눌러줘."):
            yield chunk
        yield "__END__STREAM__"
        return

    already_warned = any("[가구 경고]" in m.content for m in memory.chat_memory.messages)
    if not already_warned and count_unique_furniture_mentions(only_user_conversation) == 6:
        warning = get_furniture_warning_chain().run({"conversation": full_conversation}).strip()
        memory.chat_memory.add_ai_message(f"[가구 경고] {warning}")
        async for chunk in stream_fixed_message(warning):
            yield chunk
        yield "__END__STREAM__"
        return

    async for token in stream_response(user_input, full_conversation, prompt_template=dynamic_chat_prompt):
        if token != "__END__STREAM__": yield token
