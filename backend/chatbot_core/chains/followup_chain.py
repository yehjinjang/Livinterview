# chatbot_core/chains/followup_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import followup_question_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

followup_chain = LLMChain(
    llm=llm,
    prompt=followup_question_prompt
)
