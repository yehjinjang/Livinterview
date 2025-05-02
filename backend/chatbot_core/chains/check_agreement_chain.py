# chatbot_core/chains/check_agreement_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import check_partial_agreement_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

check_agreement_chain = LLMChain(
    llm=llm,
    prompt=check_partial_agreement_prompt
)
