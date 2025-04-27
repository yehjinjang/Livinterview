from fastapi import APIRouter
from pydantic import BaseModel
import openai 
import os 
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": request.message}]
    )
    reply = response.choices[0].message.content
    return {"reply": reply}