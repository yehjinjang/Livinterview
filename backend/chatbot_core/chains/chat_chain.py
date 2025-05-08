from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from chatbot_core.memory.session_memory import memory

def get_chat_chain() -> LLMChain:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    
    chat_prompt = PromptTemplate(
        input_variables=["chat_history", "user_input"],
        template="""
넌 인테리어 전문가야.
아래는 지금까지 사용자와 나눈 대화야:

{chat_history}

이제 사용자가 이렇게 말했어:
"{user_input}"

맥락을 반영해서 친근하고 자연스럽게 반말로 답변해줘.
"""
    )
    
    return LLMChain(
        llm=llm,
        prompt=chat_prompt,
        memory=memory,
        verbose=True
    )
