from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import uuid
import aiohttp
import aiofiles

from chatbot_core.logic.run_conversation_api import run_initial_prompt, run_user_turn
from chatbot_core.memory.session_memory import memory
from chatbot_core.chains import summary_chain, controlnet_chain


UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_image_from_url(image_url: str) -> str:
    image_id = str(uuid.uuid4())
    image_path = os.path.join(UPLOAD_DIR, f"{image_id}.jpg")

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                raise ValueError("이미지 다운로드 실패")

            async with aiofiles.open(image_path, mode="wb") as f:
                await f.write(await resp.read())

    return image_id


# ───── 환경 변수 로드 및 클라이언트 초기화 ─────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()

# ───── 요청 모델 ─────
class ChatRequest(BaseModel):
    image_url: str | None = None
    user_input: str | None = None

# ───── /chat 스트리밍 라우터 ─────
@router.post("/chat")
async def chat(request: ChatRequest):
    if request.image_url:
        try:
            # 1. 이미지 저장
            image_id = await save_image_from_url(request.image_url)

            # 2. 스트리밍 응답에 image_id를 먼저 보냄
            async def event_stream():
                yield f"__IMAGE_ID__:{image_id}__END__STREAM__"
                async for chunk in run_initial_prompt(request.image_url):
                    yield chunk

            return StreamingResponse(event_stream(), media_type="text/plain")

        except Exception as e:
            async def error_stream():
                yield f"에러: {str(e)}"
            return StreamingResponse(error_stream(), media_type="text/plain")

    if request.user_input:
        async def event_stream():
            async for chunk in run_user_turn(request.user_input):
                yield chunk
        return StreamingResponse(event_stream(), media_type="text/plain")

    async def error_stream():
        yield "image_url 또는 user_input 중 하나는 반드시 포함되어야 합니다."
    return StreamingResponse(error_stream(), media_type="text/plain")


# ───── /generate-image 엔드포인트 ─────
@router.post("/generate-image")
async def generate_image():
    try:
        history = memory.load_memory_variables({})["chat_history"]
        full_convo = "\n".join(str(m.content) for m in history)

        summary = summary_chain.run({"conversation": full_convo}).strip()
        base_prompt = controlnet_chain.run({"summary": summary}).strip().strip('"')
        final_prompt = (
            base_prompt
            + " Do not change the room’s layout, dimensions, wallpaper color, "
              "floor material, or the positions of the windows and doors, as they are fixed."
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
        )
        image_url = response.data[0].url
        return {"image_url": image_url}

    except Exception as e:
        return {"error": str(e)}
