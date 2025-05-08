# chatbot_core/chains/check_completion_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import check_completion_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

check_completion_chain = LLMChain(
    llm=llm,
    prompt=check_completion_prompt
)
