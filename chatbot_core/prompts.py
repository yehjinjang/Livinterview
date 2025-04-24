
from langchain.prompts import PromptTemplate

refine_reply_prompt = PromptTemplate.from_template("""
아래는 인테리어 챗봇이 사용자 질문에 답한 초안이야.
전체적으로 괜찮긴 하지만, 아래 세 가지를 더해서 자연스럽고 이해하기 쉽게 고쳐줘:

1. 사용자가 요청한 내용을 맨 앞에 자연스럽게 요약해줘
2. 배치나 스타일 이유는 방 분위기랑 연결해서 설명해줘
3. 톤이나 스타일 키워드를 강조해서 끝에 정리해줘

초기 응답:
{response}

출력 형식:
사용자 요청 요약 + 배치 제안 + 스타일 요약 (친근하고 자연스러운 반말)
""")

question_check_prompt = PromptTemplate.from_template("""
다음 문장이 질문인지 판단해줘. 질문이면 "YES", 아니면 "NO"라고만 답해.

문장:
{text}
""")

check_agreement_prompt = PromptTemplate.from_template("""
다음 사용자의 말이 GPT 제안에 '좋아', '그렇게 해줘', '응' 같은 명확한 동의 표현인지 판단해줘.

조건:
- "좋아", "그래", "응", "좋은 생각이야", "그렇게 해줘" 같은 말이면 "YES"라고 답해
- 그냥 가구 이름이나 키워드만 말한 건 "NO"로 해줘

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


followup_question_prompt = PromptTemplate.from_template("""
다음 대화 내용은 인테리어 프롬프트를 만들기엔 정보가 부족해.
부족한 이유를 반영해서, 자연스럽게 이어갈 수 있는 구체적인 질문을 1개 반말로 만들어줘.
예: 스타일, 가구 색상/위치, 추가 장식 요소 등을 물어보는 질문이 좋아.

대화 내용:
{conversation}
""")



summary_prompt = PromptTemplate.from_template("""
다음 대화는 인테리어 AI 챗봇과 사용자 간의 대화야.  
이 중에서 **사용자가 동의한 내용에 대해서만** 요약해줘.

조건:
- 사용자가 "좋아요", "그대로 해줘", "응", "맞아" 등으로 명확하게 동의한 제안 내용만 포함해줘.
- 사용자가 "조명 좋아", "침대는 괜찮아"처럼 일부만 언급한 경우에는 해당 **부분만 간단히 포함**해줘.
- GPT가 추가로 제안했지만 사용자가 언급하지 않은 내용은 **절대 포함하지 마**.

형식: 사용자에게 직접 말하듯이, 3~5줄 정도의 자연스럽고 친근한 한국어 반말로 정리해줘.

대화 내용:
{conversation}
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