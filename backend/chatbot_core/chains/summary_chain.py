# chatbot_core/chains/summary_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import summary_prompt

def get_summary_chain() -> LLMChain:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    return LLMChain(llm=llm, prompt=summary_prompt)