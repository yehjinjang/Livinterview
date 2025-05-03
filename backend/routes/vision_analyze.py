from fastapi import APIRouter, UploadFile
import openai
import base64
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/analyze-image")
async def analyze_image(image: UploadFile):
    content = await image.read()
    encoded_image = base64.b64encode(content).decode('utf-8')

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're an expert in analyzing room interiors."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 방의 벽 색, 바닥 소재, 창문 유무, 전체 구조를 간단히 설명해줘."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                ]
            }
        ],
        temperature=0.2
    )

    description = response.choices[0].message.content
    return {"description": description}
