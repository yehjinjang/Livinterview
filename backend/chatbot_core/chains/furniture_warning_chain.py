# chatbot_core/chains/furniture_warning_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import furniture_warning_prompt

def get_furniture_warning_chain():
    return LLMChain(
        llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
        prompt=furniture_warning_prompt
    )