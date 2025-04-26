
from langchain.prompts import PromptTemplate


question_check_prompt = PromptTemplate.from_template("""
다음 문장이 질문인지 판단해줘. 질문이면 "YES", 아니면 "NO"라고만 답해.

문장:
{text}
""")

check_partial_agreement_prompt = PromptTemplate.from_template("""
다음 문장은 인테리어 제안 한 줄에 대해 **동의하거나 긍정적으로 반응한 표현인지** 판단해줘.

판단 기준:
- 사용자가 "좋아", "괜찮아", "맘에 들어", "그거 하자", "응", "네", "ㅇㅇ", "그대로 해줘", "그거 예쁘다", "마음에 들어" 등 긍정 표현을 포함하면 "YES"
- 또는, 제안 문장에 포함된 가구나 스타일 키워드를 **사용자가 직접 언급**하면 "YES"
  - 예: 제안이 "러그는 침대 옆에 깔기"이고 사용자가 "러그 필요해"라고 하면 YES
- 단순히 제안과 무관한 단어거나, 어떤 반응도 없이 키워드만 언급한 경우는 "NO"

GPT 제안:
{gpt_response}

사용자 응답:
{text}
""")

extract_proposal_prompt = PromptTemplate.from_template("""
아래는 챗봇이 해준 인테리어 제안이야. 여기서 **하나의 제안마다 한 줄씩** 뽑아줘.

조건:
- 단순한 분위기 설명이나 감정 표현, 질문은 **제외**하고
- **가구 종류, 배치 위치, 스타일, 색상**이 들어간 구체적인 제안만 골라
- 각 줄에 **하나의 가구나 배치 제안**만 담기도록 해줘 (ex. 침대는 창가에, 커튼은 하얀색)

출력 형식:
- 한 줄에 하나씩
- 군더더기 없이 간결하게

GPT 응답:
{response}
""")


check_prompt = PromptTemplate.from_template("""
다음 대화 내용을 보고 인테리어 프롬프트를 만들 수 있을지 판단해줘.

프롬프트를 만들 수 있다고 판단하려면, 아래 조건 중 최소 3개 이상을 충족해야 해:
1. 사용자가 원하는 가구 종류를 언급하거나 GPT의 제안에 동의했는가?
2. 가구의 배치 위치에 대한 정보가 있는가?
3. 가구의 스타일이나 색상에 대한 정보가 있는가?
4. 인테리어 스타일에 대한 언급 또는 동의가 있는가?
5. 조명, 커튼, 소품 등 추가 장식 요소에 대한 언급 또는 동의가 있는가?

조건이 3개 이상 충족되면 "YES", 아니라면 "NO"라고만 답해.
대화 내용:
{conversation}
""")


furniture_warning_prompt = PromptTemplate.from_template("""
현재까지의 대화 내용을 기반으로, 인테리어에 제안된 가구가 너무 많을 수 있어.
이미지 생성 시 현실적이지 않을 수 있다는 점을 사용자에게 자연스럽게 알려줘.

조건:
- 너무 많은 가구가 포함되면 현실성이 떨어질 수 있음을 부드럽게 경고
- 사용자가 "그만 추가하고 이대로 이미지 만들기"를 선택할지, 아니면 이미지가 이상해져도 계속 추가할 건지 물어보기
- 반말, 자연스러운 톤, 부담 없는 질문으로 마무리

대화 내용:
{conversation}
""")



followup_question_prompt = PromptTemplate.from_template("""
다음 대화 내용은 인테리어 프롬프트를 만들기엔 정보가 부족해.
부족한 이유를 반영해서, 자연스럽게 이어갈 수 있는 구체적인 질문을 1개 반말로 만들어줘.
예: 스타일, 필요한 가구, 가구 색상/위치, 추가 장식 요소 등을 물어보는 질문이 좋아.

대화 내용:
{conversation}
""")



summary_prompt = PromptTemplate.from_template("""
다음 대화는 인테리어 AI 챗봇과 사용자 간의 대화야.  
이 중에서 **사용자가 동의하거나 직접 제안한 내용에 대해서만** 요약해줘.

조건:
- 사용자가 "좋아요", "그대로 해줘", "응", "맞아" 등으로 명확하게 동의한 제안 내용만 포함해줘.
- 사용자가 "조명 좋아", "침대는 괜찮아"처럼 일부만 언급한 경우에는 해당 **부분만 간단히 포함**해줘.
- GPT가 추가로 제안했지만 사용자가 언급하지 않은 내용은 **절대 포함하지 마**.
- 사용자가 명확하게 **가구 이름을 직접 언급한 경우에도 포함**해줘 (예: "옷장 필요해", "침대랑 선반", "수납장도 넣어줘")

형식: 사용자에게 직접 말하듯이, 3~5줄 정도의 자연스럽고 친근한 한국어 반말로 정리해줘.
마지막 문장은 요약한 내용이 맞는지 확인하는 질문을 해줘.

대화 내용:
{conversation}
""")


check_completion_prompt = PromptTemplate.from_template("""
다음 사용자 입력이 인테리어에 대한 추가 요청이나 질문 없이,
**지금 상태로 충분하다는 의사 표현** 또는 **이미지 생성을 요청하는 표현**이면 "YES",
추가적인 요청이나 아이디어를 포함하면 "NO"라고 답해.

판단 기준:
- 다음과 같은 의미를 가지면 "YES":
  - "이제 됐어", "그 정도면 됐어", "더 필요한 거 없어", "충분해", "이대로 좋아요", "딱 좋아요", "이대로 하자", "이대로 가자", "이대로 진행하자", "이렇게 해줘" 등 추가 요청이 없다는 의미
  - "아니", "아니요", "없어", "이제 없어" 등 추가하지 않겠다는 의미
  - "지금 상태로 이미지 만들어줘", "이대로 이미지 생성해", "그대로 생성해줘", "지금 만들자", "이미지 만들어줘", "지금 만들어줘", "이대로 만들어", "이미지 만들자" 등 이미지 생성 요청 의미
- 위 표현들과 정확히 일치하지 않아도, 문맥상 "추가 요청 없이 지금 상태로 충분하다" 또는 "이제 이미지 만들자"는 뜻이 명확하면 "YES"
- 그 외에는 "NO"

사용자 입력:
{text}
""")


controlnet_prompt = PromptTemplate.from_template("""
Generate a one-line English prompt for ControlNet based on the following interior summary.

Only include information about:
- specific furniture types and their placement (e.g., bed by the window)
- furniture material, style, or color (e.g., light wood desk, white curtains)

Exclude:
- any mention of room mood, atmosphere, or effects like "makes the room look bigger", "adds warmth", etc.

User summary:
{summary}
""")