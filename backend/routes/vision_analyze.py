from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse
import base64

from chatbot_core.logic.run_conversation_api import run_initial_prompt

router = APIRouter()

@router.post("/analyze-image")
async def analyze_image(image: UploadFile):
    content = await image.read()
    encoded_image = base64.b64encode(content).decode("utf-8")
    image_url = f"data:image/png;base64,{encoded_image}"

    async def event_stream():
        async for chunk in run_initial_prompt(image_url):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")
