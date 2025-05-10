import asyncio
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from chatbot_core.memory.session_memory import get_memory
from chatbot_core.chains.check_completion_chain import get_check_completion_chain
from chatbot_core.chains.extract_structure_chain import get_extract_structure_chain
from chatbot_core.chains.check_agreement_chain import get_check_agreement_chain
from chatbot_core.chains.summary_chain import get_summary_chain
from chatbot_core.chains.furniture_warning_chain import get_furniture_warning_chain
from chatbot_core.prompts import summary_prompt, system_prompt
from chatbot_core.logic.common import count_unique_furniture_mentions

import logging
logger = logging.getLogger(__name__)


def get_chat_model(use_vision=False, temperature=0.5, callbacks=None):
    return ChatOpenAI(
        model="gpt-4o" if use_vision else "gpt-4o-mini",
        streaming=True,
        temperature=temperature,
        callbacks=callbacks
    )


async def stream_fixed_message(text: str, delay: float = 0.03):
    for chunk in text:
        yield chunk
        await asyncio.sleep(delay)


async def stream_response(user_input: str, history: str, session_id: str):
    callback = AsyncIteratorCallbackHandler()
    llm = get_chat_model(use_vision=False, temperature=0.5, callbacks=[callback])

    messages = [
        SystemMessage(content=system_prompt.content),
        HumanMessage(content=f"""
지금까지 사용자와 나눈 대화야:

{history}

이제 사용자가 이렇게 말했어:
"{user_input}"

맥락을 반영해서 자연스럽게 반말로 답변해줘.
""")
    ]

    task = asyncio.create_task(llm.ainvoke(messages))

    full_response = ""
    async for token in callback.aiter():
        yield token
        full_response += token

    await task
    memory = get_memory(session_id)
    memory.chat_memory.add_ai_message(full_response)
    yield "__END__STREAM__"


async def stream_summary(conversation: str, session_id: str):
    memory = get_memory(session_id)

    relevant_messages = [
        m.content for m in memory.chat_memory.messages
        if (
            m.type in ("human", "ai")
            and not m.content.startswith("[상세구조]")
            and not m.content.startswith("[간략구조]")
            and not m.content.startswith("[방 구조]")
            and not m.content.startswith("[system]")
        )
    ]

    has_user_message = any(
        isinstance(m, HumanMessage) for m in memory.chat_memory.messages if m.content in relevant_messages
    )
    if not has_user_message:
        yield "요약할 대화가 없습니다."
        yield "__END__STREAM__"
        return

    conversation = "\n".join(relevant_messages)

    summary_chain = get_summary_chain()
    summary = summary_chain.run({"conversation": conversation})
    memory.chat_memory.add_ai_message(summary)

    if not any(m.content == "SUMMARY_PENDING_CONFIRMATION" for m in memory.chat_memory.messages):
        memory.chat_memory.add_ai_message("SUMMARY_PENDING_CONFIRMATION")

    yield summary
    yield "__END__STREAM__"


async def run_initial_prompt(session_id: str, image_id: str, is_clean: bool = False):
    logger.info(f"[run_initial_prompt] 호출됨: session_id={session_id}, image_id={image_id}, is_clean={is_clean}")
    memory = get_memory(session_id)
    logger.info("[run_initial_prompt] memory 불러옴")
    callback = AsyncIteratorCallbackHandler()
    llm = get_chat_model(use_vision=True, callbacks=[callback])

    # 무조건 구조 분석 수행
    logger.info("[run_initial_prompt] 구조 분석 시작")
    local_path = f"./data/uploads/{image_id}.jpg"
    from chatbot_core.chains.structure_chains import detailed_structure_chain
    detailed_msg = await detailed_structure_chain.ainvoke({"image_path": local_path})
    structure_context = detailed_msg.content.strip()
    memory.chat_memory.add_ai_message(f"[상세구조][{image_id}] {structure_context}")
    logger.info("[run_initial_prompt] 구조 분석 완료")

    # 시스템 메시지 생성
    system = SystemMessage(
        content=system_prompt.content + f"\n\n참고로, 이 방은 다음과 같아: {structure_context}"
    )
    messages = [system]

    # 스트리밍 시작
    logger.info("[run_initial_prompt] 스트리밍 시작")
    task = asyncio.create_task(llm.ainvoke(messages))
    full_response = ""

    async for token in callback.aiter():
        yield token
        full_response += token

    await task
    logger.info("[run_initial_prompt] 스트리밍 완료")

    structure_desc = get_extract_structure_chain().run({"response": full_response}).strip()
    memory.chat_memory.add_ai_message(f"[방 구조] {structure_desc}")
    logger.info("[run_initial_prompt] 구조 요약 저장 완료")

    yield "__END__STREAM__"


async def run_user_turn(user_input: str, session_id: str):
    memory = get_memory(session_id)
    memory.chat_memory.add_user_message(user_input)

    ai_messages = [m.content for m in memory.chat_memory.messages if m.type == "ai"]
    full_conversation = "\n".join(
        m.content for m in memory.chat_memory.messages
        if m.type in ("human", "ai") and not m.content.startswith("[가구 경고]")
    ) or user_input
    only_user_conversation = "\n".join(
        m.content for m in memory.chat_memory.messages
        if m.type == "human" and not m.content.startswith("[가구 경고]")
    )

    if ai_messages and ai_messages[-1] == "SUMMARY_PENDING_CONFIRMATION":
        last_summary = ai_messages[-2] if len(ai_messages) >= 2 else ""
        decision = get_check_agreement_chain().run(
            gpt_response=last_summary,
            text=user_input
        ).strip().upper()

        if decision == "YES":
            detailed = memory.variables.get("detailed_structure", "")
            final_summary = (
                f"{detailed} Also, here’s a quick recap: {last_summary}"
                if last_summary else detailed
            )
            memory.variables["confirmed_summary"] = final_summary
            async for chunk in stream_fixed_message(
                "좋아! 그럼 지금까지 얘기한 걸로 방을 꾸며볼게. 조금만 기다려줘."
            ):
                yield chunk
            yield "__END__STREAM__"
            return
        else:
            async for chunk in stream_response(user_input, full_conversation, session_id):
                if chunk != "__END__STREAM__":
                    yield chunk
            return

    if get_check_completion_chain().run(text=user_input).strip().upper() == "YES":
        async for chunk in stream_fixed_message(
            "좋아, 그럼 이대로 꾸며볼게! 오른쪽 아래 '인테리어 생성' 버튼을 눌러줘."
        ):
            yield chunk
        yield "__END__STREAM__"
        return

    already_warned = any(
        m.content.startswith("[가구 경고]")
        for m in memory.chat_memory.messages
    )
    if not already_warned and count_unique_furniture_mentions(only_user_conversation) == 6:
        warning = get_furniture_warning_chain().run(
            {"conversation": full_conversation}
        ).strip()
        memory.chat_memory.add_ai_message(f"[가구 경고] {warning}")
        async for chunk in stream_fixed_message(warning):
            yield chunk
        yield "__END__STREAM__"
        return

    async for token in stream_response(user_input, full_conversation, session_id):
        if token != "__END__STREAM__":
            yield token
    yield "__END__STREAM__"
