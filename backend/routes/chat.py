from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from chatbot_core.logic.run_conversation_api import run_initial_prompt, run_user_turn

router = APIRouter()

# ───── 요청 모델 ─────
class ChatRequest(BaseModel):
    image_url: str | None = None
    user_input: str | None = None

# ───── /chat 스트리밍 라우터 ─────
@router.post("/chat")
async def chat(request: ChatRequest):
    # 초기 이미지 기반 메시지
    if request.image_url:
        async def event_stream():
            async for chunk in run_initial_prompt(request.image_url):
                yield chunk
        return StreamingResponse(event_stream(), media_type="text/plain")

    # 일반 텍스트 기반 응답
    if request.user_input:
        async def event_stream():
            async for chunk in run_user_turn(request.user_input):
                yield chunk
        return StreamingResponse(event_stream(), media_type="text/plain")

    # 유효하지 않은 요청 처리
    async def error_stream():
        yield "image_url 또는 user_input 중 하나는 반드시 포함되어야 합니다."
    return StreamingResponse(error_stream(), media_type="text/plain")

# ───── /generate-image 엔드포인트 ─────────────────
@router.post("/generate-image")
async def generate_image():
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
