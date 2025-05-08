# chatbot_core/chains/summary_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import summary_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

summary_chain = LLMChain(
    llm=llm,
    prompt=summary_prompt
)