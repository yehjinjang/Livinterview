# routes/vision_analyze.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid, aiohttp, aiofiles, os

from chatbot_core.chains.structure_chain import brief_structure_chain, detailed_structure_chain
from chatbot_core.memory.session_memory import memory

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

class ImageRequest(BaseModel):
    image_url: str

async def _save_from_url(url: str) -> str:
    img_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{img_id}.jpg")
    async with aiohttp.ClientSession() as sess, sess.get(url) as r:
        async with aiofiles.open(path, "wb") as f:
            await f.write(await r.read())
    return img_id

@router.post("/analyze-image")
async def analyze_image(req: ImageRequest):
    image_id = await _save_from_url(req.image_url)

    async def event_stream():
        # ① image_id 먼저 전달
        yield f"__IMAGE_ID__:{image_id}__END__STREAM__"

        # ② 간략 구조 설명
        brief = brief_structure_chain.run({"image_url": req.image_url})
        yield f"[간략구조] {brief}\n"
        memory.variables["brief_structure"] = brief   # 메모리에 저장

        # ③ 상세 구조 설명
        detailed = detailed_structure_chain.run({"image_url": req.image_url})
        yield f"[상세구조] {detailed}\n"
        memory.variables["detailed_structure"] = detailed  # 메모리에 저장

    return StreamingResponse(event_stream(), media_type="text/plain")
