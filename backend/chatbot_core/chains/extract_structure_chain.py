from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from chatbot_core.prompts import extract_structure_prompt

extract_structure_chain = LLMChain(
    llm=ChatOpenAI(model="gpt-4o", temperature=0.3),
    prompt=extract_structure_prompt
)
