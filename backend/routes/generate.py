from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class GenerateRequest(BaseModel):
    prompt: str

@router.post("/generate-image")
async def generate_image(req: GenerateRequest):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=req.prompt,
        n=1,
        size="1024x1024",
        quality="standard",
        response_format="url"
    )
    image_url = response['data'][0]['url']
    return {"image_url": image_url}
