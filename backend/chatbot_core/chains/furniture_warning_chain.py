# chatbot_core/chains/furniture_warning_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import furniture_warning_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

furniture_warning_chain = LLMChain(
    llm=llm,
    prompt=furniture_warning_prompt
)
