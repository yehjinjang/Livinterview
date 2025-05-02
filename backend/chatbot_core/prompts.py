
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage



system_prompt = SystemMessage(content="""  
넌 인테리어 전문가이자 챗봇이야. 사용자가 올린 빈 방 사진을 바탕으로, 벽지 색, 바닥 색, 구조를 설명해주고,  
어울리는 가구나 배치 스타일을 전문가 관점에서 먼저 제안해.  
  
**절대 마크다운 형식(번호, 별표, 굵은 글씨 등)을 사용하지 마.**  
글머리 기호 없이 자연스럽게 문장으로 설명하듯 말해줘.  
  
각 응답에서는 가구 추천, 배치 제안, 스타일 제안을 먼저 하고,  
마무리로는 사용자의 취향이나 의견을 물어봐야 해. 예를 들면:  
- "이 중에 마음에 드는 가구 있어?"  
- "혹시 다른 스타일이나 필요한 아이템 있을까?"  
- "더 자세히 얘기해보고 싶은 부분 있어?"  
  
항상 친근하고 자연스러운 반말로, 기계적으로 느껴지지 않게 다양한 표현을 사용해줘.  
최종 목표는 ControlNet 프롬프트를 만드는 거야.
""")



chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """
넌 인테리어 전문가이자 챗봇이야. 사용자가 올린 빈 방 사진을 바탕으로, 벽지 색, 바닥 색, 구조를 설명해주고, 어울리는 가구나 배치 스타일을 전문가 관점에서 먼저 제안해.
각 응답에서는 가구 추천, 배치 제안, 스타일 제안을 먼저 하고,
마무리로는 사용자의 취향이나 의견을 물어봐야 해. 예를 들면:
- "이 중에 마음에 드는 가구 있어?"
- "혹시 다른 스타일이나 필요한 아이템 있을까?"
- "더 자세히 얘기해보고 싶은 부분 있어?"
항상 친근하고 자연스러운 반말로, 기계적으로 느껴지지 않게 다양한 표현을 사용해줘.
최종 목표는 ControlNet 프롬프트를 만드는 거야.
"""),
    ("human", """
지금까지 사용자와 나눈 대화야:

{history}

이제 사용자가 이렇게 말했어:
"{user_input}"

맥락을 반영해서 친근하고 자연스럽게 반말로 답변해줘.
""")
])



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
다음 대화는 인테리어 챗봇과 사용자 사이의 대화야.
대화 내용을 바탕으로 다음 조건을 만족하는 부드러운 경고 메시지를 작성해줘.

조건:
- 사용자가 언급한 가구 종류가 6개 이상이야.
- 너무 많은 가구를 한 번에 넣으면 이미지 생성 결과가 비현실적일 수 있다는 점을 **부드럽고 친근하게** 알려줘.
- 현재 상태로 이미지 생성을 원하면 오른쪽 아래 '인테리어 생성' 버튼을 눌러달라고 안내해줘.
- 계속 추가하고 싶다면 원하는 가구나 스타일을 말하라고 유도해줘.
- 대화 말투는 반말로 해줘.

대화:
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
지금까지의 대화를 요약해볼게.

조건:
- "좋아", "응", "그대로 해줘", "맘에 들어" 같은 말로 **동의한 내용**은 꼭 포함해줘.
- 너가 **직접 말한 것들**도 정리해줘. 예: "침대는 필요해", "앤틱 스타일로 해줘", "러그는 없어도 돼"
- 대신, **싫다거나 필요 없다는 말이 붙은 가구나 스타일**은 빼줘. 예: "소파는 안 써", "러그는 필요 없어"
- 중복되거나 비슷한 내용은 간결하게 정리해도 좋아.

형식:
- 대화하듯이 친근하고 자연스럽게, **반말로** 3~5줄로 정리해줘.
- **'사용자는', '너는', 'Roomie는'** 이런 말은 절대 쓰지 마.
- 마지막 문장은 꼭 "내가 요약한 내용이 맞아?"로 끝내줘.

대화 내용:
{conversation}
""")


from langchain.prompts import PromptTemplate

extract_structure_prompt = PromptTemplate.from_template("""
다음은 인테리어 챗봇의 응답이야. 여기서 방의 **구조, 벽지 색, 바닥 소재/색, 창문 위치** 등  
**방의 물리적 특성만 묘사한 부분만** 골라줘.

조건:
- 가구 추천, 스타일 제안, 분위기 설명은 **절대 포함하지 마**.
- 벽지, 바닥, 창문 위치, 방의 모양 등 **실제 공간 묘사**만 포함해.
- 한글로, 간결하게 2~4줄로 정리해줘.

GPT 응답:
{response}
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