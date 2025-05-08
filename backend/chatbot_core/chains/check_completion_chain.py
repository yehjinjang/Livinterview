# chatbot_core/chains/check_completion_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import check_completion_prompt

def get_check_completion_chain():
    return LLMChain(
        llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
        prompt=check_completion_prompt
    )