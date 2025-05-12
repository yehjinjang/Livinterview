from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from chatbot_core.memory.session_memory import get_memory
from chatbot_core.chains.structure_chains import build_vision_chain
from chatbot_core.chains.structure_chains import brief_structure_chain

UPLOAD_DIR = "./data/uploads"
router = APIRouter()

# 통합 Vision Chain 정의
structure_chain = build_vision_chain(
    """
    Please analyze the following room image and extract:

    [BRIEF]
    - A concise description of the wallpaper color, floor material, and overall tone in one sentence.

    [DETAILED]
    - A detailed breakdown of the room structure including:
      - Wallpaper pattern and color
      - Floor material and finish
      - Window and door positions
      - Ceiling height and lighting
      - Any unique architectural features

    Output in this format:
    [BRIEF]
    ...
    [DETAILED]
    ...
    """
)

class StructureRequest(BaseModel):
    session_id: str
    image_id: str   # 클라이언트는 image_id만 전달

@router.post("/analyze-structure")
async def analyze_structure(req: StructureRequest):
    memory = get_memory(req.session_id)

    # 1) image_id 기반 로컬 파일 경로 결정 (jpg, jpeg, png 순으로 시도)
    image_path = None
    for ext in (".jpg", ".jpeg", ".png"):
        candidate = os.path.join(UPLOAD_DIR, f"{req.image_id}{ext}")
        if os.path.isfile(candidate):
            image_path = os.path.abspath(candidate)
            break
    if image_path is None:
        raise HTTPException(status_code=404, detail="저장된 이미지를 찾을 수 없습니다.")

    basename = req.image_id

    # 2) Vision Chain 호출
    msg = await structure_chain.ainvoke({"image_path": image_path})
    content = msg.content if hasattr(msg, "content") else str(msg)

    # 3) BRIEF / DETAILED 분리
    parts = content.split("[DETAILED]")
    brief = parts[0].replace("[BRIEF]", "").strip()
    detailed = parts[-1].strip()

    # 4) 메모리 업데이트
    memory.chat_memory.add_user_message("[system] 방 구조 설명")
    memory.chat_memory.add_ai_message(f"[간략구조] {brief}")
    memory.chat_memory.add_ai_message(f"[상세구조][{basename}] {detailed}")
    memory.chat_memory.add_ai_message(image_path)

    # 5) 결과 리턴 (확장자 없이 image_id 반환)
    return {
        "brief": brief,
        "detailed": detailed,
        "image_id": basename
    }


# /vision/analyze-brief
@router.post("/analyze-brief")
async def analyze_brief(req: StructureRequest):
    memory = get_memory(req.session_id)

    image_path = None
    for ext in (".jpg", ".jpeg", ".png"):
        candidate = os.path.join(UPLOAD_DIR, f"{req.image_id}{ext}")
        if os.path.isfile(candidate):
            image_path = os.path.abspath(candidate)
            break
    if image_path is None:
        raise HTTPException(status_code=404, detail="이미지 없음")

    msg = await brief_structure_chain.ainvoke({"image_path": image_path})
    content = msg.content if hasattr(msg, "content") else str(msg)

    memory.chat_memory.add_user_message("[system] 간략 구조 설명")
    memory.chat_memory.add_ai_message(f"[간략구조] {content}")
    memory.chat_memory.add_ai_message(image_path)

    return {"brief": content}
