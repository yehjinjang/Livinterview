# chatbot_core/chains/controlnet_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import controlnet_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

controlnet_chain = LLMChain(
    llm=llm,
    prompt=controlnet_prompt
)
