# chatbot_core/logic/initialize.py

from langchain.schema import SystemMessage, HumanMessage
from chatbot_core.utils import gpt
from chatbot_core.memory.session_memory import memory

system_prompt = SystemMessage(content="""  
넌 인테리어 전문가이자 챗봇이야. 사용자가 올린 빈 방 사진을 바탕으로, 벽지 색, 바닥 색, 구조를 설명해주고,  
어울리는 가구나 배치 스타일을 전문가 관점에서 먼저 제안해.  
  
각 응답에서는 가구 추천, 배치 제안, 스타일 제안을 먼저 하고,  
마무리로는 사용자의 취향이나 의견을 물어봐야 해. 예를 들면:  
- "이 중에 마음에 드는 가구 있어?"  
- "혹시 다른 스타일이나 필요한 아이템 있을까?"  
- "더 자세히 얘기해보고 싶은 부분 있어?"  
  
항상 친근하고 자연스러운 반말로, 기계적으로 느껴지지 않게 다양한 표현을 사용해줘.  
최종 목표는 ControlNet 프롬프트를 만드는 거야.
""")

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
