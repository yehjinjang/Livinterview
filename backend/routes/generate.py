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
    # 1) 프론트가 보낸 summary (한국어)
    summary = req.prompt.strip()

    # 2) 영어 변환 + 제약 추가
    base_prompt = controlnet_chain.run({"summary": summary}).strip().strip('"')
    final_prompt = (
        base_prompt
        + " Do not change the room’s layout, dimensions, wallpaper color, "
          "floor material, or the positions of the windows and doors, "
          "as they are fixed."
    )

    # 3) DALL·E 3 호출
    response = client.images.generate(
        model="dall-e-3",
        prompt=final_prompt,
        n=1,
        size="1024x1024",
        quality="standard",
    )
    return {"image_url": response.data[0].url}