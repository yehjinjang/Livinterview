# chatbot_core/chains/controlnet_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import controlnet_prompt

def get_controlnet_chain() -> LLMChain:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    return LLMChain(llm=llm, prompt=controlnet_prompt)