from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, uuid, aiohttp, aiofiles


from chatbot_core.logic.run_conversation_api import run_initial_prompt, run_user_turn
from chatbot_core.memory.session_memory import get_memory
from chatbot_core.chains.summary_chain import get_summary_chain
from chatbot_core.chains.controlnet_chain import get_controlnet_chain

import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) 

# ───── 기본 설정 ─────
UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

# ───── 유틸: 이미지 저장 ─────
async def save_image_from_url(image_url: str) -> str:
    image_id = str(uuid.uuid4())
    image_path = os.path.join(UPLOAD_DIR, f"{image_id}.jpg")
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                raise ValueError("이미지 다운로드 실패")
            async with aiofiles.open(image_path, "wb") as f:
                await f.write(await resp.read())
    return image_id

# ───── 요청 모델 ─────
class ChatRequest(BaseModel):
    session_id: str
    image_url: str | None = None
    user_input: str | None = None
    image_id: str | None = None
    is_clean: bool | None = None
    structure_context: str | None = None

# ───── /chat 스트리밍 라우터 ─────
@router.post("/chat")
async def chat(request: ChatRequest):
    # 1) 사용자 메시지가 있으면 run_user_turn
    if request.user_input:
        async def event_stream():
            async for chunk in run_user_turn(
                user_input=request.user_input,
                session_id=request.session_id,
            ):
                yield chunk
        return StreamingResponse(event_stream(), media_type="text/plain")

    # 2) image_id 기반 초기 프롬프트
    if request.image_id:
        async def event_stream():
            async for chunk in run_initial_prompt(
                session_id=request.session_id,
                image_id=request.image_id,
                is_clean=request.is_clean or False,
            ):
                yield chunk
        return StreamingResponse(event_stream(), media_type="text/plain")

    # 3) image_url 기반 초기 프롬프트
    if request.image_url:
        image_id = await save_image_from_url(request.image_url)
        async def event_stream():
            async for chunk in run_initial_prompt(
                session_id=request.session_id,
                image_id=image_id,
                is_clean=False,
            ):
                yield chunk
        return StreamingResponse(event_stream(), media_type="text/plain")

    # 4) 오류
    async def error_stream():
        yield "image_url, image_id 또는 user_input 중 하나는 반드시 포함되어야 합니다."
    return StreamingResponse(error_stream(), media_type="text/plain")


# ───── 요약 요청 모델 ─────
class SummaryRequest(BaseModel):
    session_id: str

# ───── /analyze/summarize-memory 요약 라우터 ─────
from chatbot_core.logic.run_conversation_api import stream_summary

@router.post("/analyze/summarize-memory")
async def summarize_memory(request: SummaryRequest):
    memory = get_memory(request.session_id)
    history = memory.load_memory_variables({})["chat_history"]
    full_convo = "\n".join(str(m.content) for m in history)

    # 사용자 발화가 없을 경우 요약 생략
    has_user_message = any(m.type == "human" for m in history)
    if not has_user_message:
        return {"result": "요약할 대화가 없습니다."}

    result = ""
    async for chunk in stream_summary("", request.session_id):
        result += chunk

    return {"result": result.replace("__END__STREAM__", "").strip()}


# ───── /generate-image 엔드포인트 ─────
@router.post("/generate-image")
async def generate_image(request: ChatRequest):
    try:
        memory = get_memory(request.session_id)
        logger.info("✅ memory 불러옴")
        variables = memory.load_memory_variables({})
        history = variables["chat_history"]
        full_convo = "\n".join(str(m.content) for m in history)

        summary = variables.get("confirmed_summary")
        if not summary:
            summary = get_summary_chain().run({"conversation": full_convo})

        logger.info(f"[📝 요약 내용] {summary}")

        # 메모리에서 [방 구조] 내용 불러오기
        structure_desc = ""
        for message in memory.chat_memory.messages:
            if message.content.startswith("[상세구조]"):
                structure_desc = message.content.replace("[상세구조]", "").strip()
                break

        base_prompt = get_controlnet_chain().run({
                    "summary": summary,
                    "structure_context": structure_desc  # 방 구조를 추가
                }).strip().strip('"')
        final_prompt = (
            base_prompt
            + " Do not change the room’s layout, dimensions, wallpaper color, "
              "floor material, or the positions of the windows and doors, as they are fixed."
        )
        final_prompt = final_prompt[:2000]

        logger.info(f"[🎨 ControlNet 프롬프트] {final_prompt}")

        response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
        )
        image_url = response.data[0].url
        logger.info(f"[✅ DALL·E 응답] image_url: {image_url}")
        return {"image_url": image_url}

    except Exception as e:
        logger.exception("❌ generate-image 실패")
        raise HTTPException(status_code=500, detail=str(e))