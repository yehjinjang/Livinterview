
from langchain.schema import SystemMessage, HumanMessage
from .utils import ask_gpt, gpt
from .prompts import (
    check_agreement_prompt, check_prompt, question_check_prompt,
    summary_prompt, controlnet_prompt, extract_proposal_prompt
)

import re

system_prompt = SystemMessage(content="""
넌 인테리어 전문가이자 챗봇이야. 사용자가 올린 빈 방 사진을 바탕으로, 벽지 색, 바닥 색, 구조를 설명해주고, 어울리는 가구나 배치 스타일을 전문가 관점에서 먼저 제안해.
그 다음엔 자연스럽게 어떤 가구가 필요한지, 원하는 스타일이 있는지를 물어봐.
사용자에게 직접 말하듯이, 자연스럽고 친근한 반말로 말해줘.
최종 목표는 ControlNet 프롬프트를 만드는 거야.
""")

def run_conversation(image_url: str):
    messages = [
        system_prompt,
        HumanMessage(content=[
            {"type": "text", "text": "이 방 어떻게 꾸미면 좋을까?"},
            {"type": "image_url", "image_url": {"url": image_url}}
        ])
    ]

    response = ask_gpt(messages)
    last_gpt_response = response.content
    print("GPT 응답:\n", last_gpt_response)

    approved_contents = []

    while True:
        user_text = input("\n너의 입력 (또는 '종료' 입력 시 종료): ").strip()
        if user_text.lower() in ["종료", "exit", "quit"]:
            break

        user_input = HumanMessage(content=user_text)
        messages.append(user_input)

        # 동의 여부 판단
        agree_result = gpt.invoke(check_agreement_prompt.format(text=user_text))
        if "YES" in agree_result.content.upper():
            print("\n→ GPT 제안에 동의한 것으로 판단됨.")

            # GPT 응답에서 구체적인 제안 추출
            proposal_extract = gpt.invoke(extract_proposal_prompt.format(response=last_gpt_response))
            extracted_proposals = [p.strip() for p in proposal_extract.content.split("\n") if p.strip()]

            # 사용자 응답과 매칭하여 동의한 제안만 누적
            matched_sentences = []
            for sentence in extracted_proposals:
                agreement_check = gpt.invoke(check_agreement_prompt.format(sentence=sentence, text=user_text))
                if "YES" in agreement_check.content.upper():
                    matched_sentences.append(sentence)

            if matched_sentences:
                approved_contents.append(". ".join(matched_sentences) + ".")
        else:
            print("\n→ 추가 의견을 준 것으로 판단됨.")

        # 전체 대화 문맥 구성
        user_turns = [str(m.content).strip() for m in messages if isinstance(m, HumanMessage)]
        full_conversation = "\n".join(approved_contents + user_turns)

        # 질문 여부 판단
        is_question = gpt.invoke(question_check_prompt.format(text=user_text)).content.strip().upper() == "YES"

        if is_question:
            response = ask_gpt(messages)
            last_gpt_response = response.content
            print("\nGPT 응답:\n", last_gpt_response)
            messages.append(HumanMessage(content=last_gpt_response))
            continue

        # 프롬프트 생성 가능 여부 판단
        check_result_raw = gpt.invoke(check_prompt.format(conversation=full_conversation))
        check_result = check_result_raw.content.strip().upper()

        if check_result == "YES":
            print("\n프롬프트 만들 수 있는지? → YES")

            summary = gpt.invoke(summary_prompt.format(conversation=full_conversation))
            print("\n✨ 지금까지 내용을 정리해봤어:\n", summary.content)

            confirm = input("\n이대로 인테리어된 이미지 만들어줄까? (네/아니오): ").strip()
            if confirm in ["네", "넹", "응", "좋아", "ㅇㅇ"]:
                control_prompt = gpt.invoke(controlnet_prompt.format(summary=summary.content))
                final_prompt = control_prompt.content.strip().strip('"') + \
                    " Do not change the room’s layout, dimensions, wallpaper color, floor material, or the positions of the windows and doors, as they are fixed based on the uploaded image."
                print("\nControlNet용 최종 영어 프롬프트:\n", final_prompt)
                break
            else:
                print("\n알겠어! 그럼 조금 더 도와줄게.")
        else:
            print("\n프롬프트 만들 수 있는지? → NO")
            print("\n아직 프롬프트 만들기엔 조금 부족해. 조금만 더 얘기해보자!")

        # 다음 GPT 응답 요청 (자연스러운 제안 + 질문)
        response = ask_gpt(messages)
        last_gpt_response = response.content
        print("\nGPT 응답:\n", last_gpt_response)
        messages.append(HumanMessage(content=last_gpt_response))
