import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

load_dotenv()

gpt = ChatOpenAI(model="gpt-4o", temperature=0.5)

def ask_gpt(messages):
    return gpt.invoke(messages)
