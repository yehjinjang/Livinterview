# chatbot_core/chains/check_prompt_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import check_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

check_prompt_chain = LLMChain(
    llm=llm,
    prompt=check_prompt
)
