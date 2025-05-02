# chatbot_core/chains/question_check_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import question_check_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

question_check_chain = LLMChain(
    llm=llm,
    prompt=question_check_prompt
)