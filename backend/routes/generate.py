# backend/routes/generate.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from chatbot_core.chains.controlnet_chain import get_controlnet_chain
from chatbot_core.memory.session_memory import get_memory
from interior.controlnet_inference import interior_with_controlnet

router = APIRouter()
load_dotenv()

class GenerateRequest(BaseModel):
    session_id: str
    image_id: str
    prompt: str | None = None 

@router.post("/generate-image")
async def generate_image(req: GenerateRequest):
    try:
        # 1) 메모리에서 대화 및 요약 불러오기
        memory = get_memory(req.session_id)

        # 디버깅: 저장된 메시지 출력
        for m in memory.chat_memory.messages:
            print("📌", m.content)

        variables = memory.load_memory_variables({})
        summary = variables.get("confirmed_summary") or req.prompt
        if not summary:
            raise ValueError("요약 결과가 없습니다. 프롬프트도 전달되지 않았습니다.")

        # 2) 구조 설명도 가져오기
        structure_desc = ""
        for m in memory.chat_memory.messages:
            if m.content.startswith("[간략구조]"):
                structure_desc = m.content.replace("[간략구조]", "").strip()
                break

        # 3) 프롬프트 생성 (간략구조 + 대화 요약 기반)
        base_prompt = get_controlnet_chain().run({
            "summary": summary
        }).strip().strip('"')

        final_prompt = (
            f"{structure_desc.strip()} {base_prompt.strip()} "
            "Do not change the room’s layout, dimensions, wallpaper color, "
            "floor material, or the positions of the windows and doors, as they are fixed. "
            "Use the same camera angle and perspective as the original image."
        )[:2000]

        # 4) ControlNet 기반 이미지 생성
        image_path = f"./data/uploads/{req.image_id}.jpg"
        result_path = interior_with_controlnet(image_path, final_prompt)
        result_url = result_path.replace("./data", "/data")
        full_url = f"http://localhost:8000{result_url}"  # 혹은 os.getenv("BACKEND_URL") 등으로 추후 대체

        return {"image_url": full_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
