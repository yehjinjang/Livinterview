from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

load_dotenv()

REDIS_URL = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"

def get_memory(session_id: str) -> ConversationBufferMemory:
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=RedisChatMessageHistory(
            session_id=session_id,
            url=REDIS_URL
        )
    )