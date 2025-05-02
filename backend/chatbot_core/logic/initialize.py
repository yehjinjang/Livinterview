# chatbot_core/logic/initialize.py

from langchain.schema import SystemMessage, HumanMessage
from chatbot_core.utils import gpt
from chatbot_core.memory.session_memory import memory

def initialize_conversation(image_input: str, is_base64: bool = False) -> str:
    """
    이미지 기반 첫 대화를 시작하고 memory에 초기 기록을 남긴다.
    :param image_input: 이미지 URL 또는 base64 문자열
    :param is_base64: base64 이미지인지 여부
    :return: 첫 GPT 응답 문자열
    """
    # 1. 이미지 타입에 따라 메시지 준비
    if is_base64:
        image_url = f"data:image/png;base64,{image_input}"
    else:
        image_url = image_input

    messages = [
        system_prompt,
        HumanMessage(content=[
            {"type": "text", "text": "이 방 어떻게 꾸미면 좋을까?"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ])
    ]

    # 2. GPT 응답 생성
    first_response = gpt.invoke(messages).content

    # 3. memory 초기화 + 대화 기록
    memory.chat_memory.clear()
    memory.chat_memory.add_user_message("이 방 어떻게 꾸미면 좋을까? (이미지 포함)")
    memory.chat_memory.add_ai_message(first_response)

    return first_response
