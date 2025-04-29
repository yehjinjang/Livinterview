from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

class ImageRequest(BaseModel):
    conversation: list[Message]

@router.post("/chat")
async def chat(request: ChatRequest):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": m.role, "content": m.content} for m in request.messages]
    )
    reply = response.choices[0].message.content
    return {"reply": reply}

@router.post("/generate-image")
async def generate_image(request: ImageRequest):
    # 먼저 대화내용을 요약해서 인테리어 프롬프트 만들기
    summary_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "사용자와의 대화 내용을 요약해서 인테리어 스타일에 대한 짧은 영어 프롬프트로 만들어줘. (예: 'Modern bedroom with light wood furniture, white curtains')"},
            *[{"role": m.role, "content": m.content} for m in request.conversation]
        ]
    )
    summarized_prompt = summary_response.choices[0].message.content.strip()

    # DALL·E로 이미지 생성
    image_response = openai.Image.create(
        model="dall-e-3",
        prompt=summarized_prompt,
        n=1,
        size="1024x1024"
    )

    image_url = image_response["data"][0]["url"]
    return {"image_url": image_url}