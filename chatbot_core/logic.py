from langchain.schema import SystemMessage, HumanMessage
from .utils import ask_gpt, gpt
from .prompts import (
    check_agreement_prompt, check_prompt, question_check_prompt,
    summary_prompt, controlnet_prompt, extract_proposal_prompt,
    check_completion_prompt, followup_question_prompt
)

system_prompt = SystemMessage(content="""
넌 인테리어 전문가이자 챗봇이야. 사용자가 올린 빈 방 사진을 바탕으로, 벽지 색, 바닥 색, 구조를 설명해주고, 어울리는 가구나 배치 스타일을 전문가 관점에서 먼저 제안해.

각 응답에서는 가구 추천, 배치 제안, 스타일 제안을 먼저 하고,
마무리로는 사용자의 취향이나 의견을 물어봐야 해. 예를 들면:

- "이 중에 마음에 드는 가구 있어?"
- "혹시 다른 스타일이나 필요한 아이템 있을까?"
- "더 자세히 얘기해보고 싶은 부분 있어?"

항상 친근하고 자연스러운 반말로, 기계적으로 느껴지지 않게 다양한 표현을 사용해줘.
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

        # 동의 여부, 완료 여부 판단 (동시 처리)
        agree_resp = gpt.invoke(check_agreement_prompt.format(text=user_text)).content.strip().upper()
        is_agree = "YES" in agree_resp

        is_done = gpt.invoke(check_completion_prompt.format(text=user_text)).content.strip().upper() == "YES"

        # 동의된 경우 → 제안 요약 추가
        if is_agree:
            print("\n→ GPT 제안에 동의한 것으로 판단됨.")
            proposals = gpt.invoke(extract_proposal_prompt.format(response=last_gpt_response)).content
            extracted = [p.strip() for p in proposals.split("\n") if p.strip()]
            matched = [
                s for s in extracted
                if "YES" in gpt.invoke(check_agreement_prompt.format(sentence=s, text=user_text)).content.upper()
            ]
            if matched:
                approved_contents.append(". ".join(matched) + ".")

        # 대화 전체 구성
        user_turns = [str(m.content).strip() for m in messages if isinstance(m, HumanMessage)]
        full_conversation = "\n".join(approved_contents + user_turns)

        if is_done:
            check_result = gpt.invoke(check_prompt.format(conversation=full_conversation)).content.strip().upper()
            summary = gpt.invoke(summary_prompt.format(conversation=full_conversation)).content
            print("\n→ 더 필요한 게 없다고 했어. 그럼 정리해볼게!")
            print("\n지금까지의 내용을 정리해봤어:\n", summary)

            if check_result == "YES":
                confirm = input("\n이대로 인테리어된 이미지 만들어줄까? (네/아니오): ").strip()
                is_confirm = gpt.invoke(check_agreement_prompt.format(text=confirm)).content.strip().upper() == "YES"

                if is_confirm:
                    control = gpt.invoke(controlnet_prompt.format(summary=summary)).content
                    final_prompt = control.strip().strip('"') + \
                        " Do not change the room’s layout, dimensions, wallpaper color, floor material, or the positions of the windows and doors, as they are fixed based on the uploaded image."
                    print("\nControlNet용 최종 영어 프롬프트:\n", final_prompt)
                    return
                else:
                    messages.append(HumanMessage(content=confirm))
                    followup = gpt.invoke(followup_question_prompt.format(conversation=full_conversation)).content
                    print("\nGPT 제안 질문:\n", followup)
                    continue
            else:
                print("\n→ 정리는 했지만 아직 이미지 생성엔 부족해. 좀 더 얘기해보자!")
                followup = gpt.invoke(followup_question_prompt.format(conversation=full_conversation)).content
                print("\nGPT 제안 질문:\n", followup)
                continue

        # 질문이면 GPT 응답만
        is_question = gpt.invoke(question_check_prompt.format(text=user_text)).content.strip().upper() == "YES"
        if is_question:
            response = ask_gpt(messages)
            last_gpt_response = response.content
            print("\nGPT 응답:\n", last_gpt_response)
            messages.append(HumanMessage(content=last_gpt_response))
            continue

        # 일반 응답이면 다음 제안
        response = ask_gpt(messages)
        last_gpt_response = response.content
        print("\nGPT 응답:\n", last_gpt_response)
        messages.append(HumanMessage(content=last_gpt_response))