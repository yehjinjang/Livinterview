from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from chatbot_core.prompts import extract_structure_prompt

def get_extract_structure_chain():
    return LLMChain(
        llm=ChatOpenAI(model="gpt-4o", temperature=0.5),
        prompt=extract_structure_prompt
    )