# chatbot_core/chains/extract_proposal_chain.py

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import extract_proposal_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

extract_proposal_chain = LLMChain(
    llm=llm,
    prompt=extract_proposal_prompt
)
