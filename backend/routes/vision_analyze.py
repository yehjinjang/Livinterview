# routes/vision_analyze.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid, aiohttp, aiofiles, os
from langchain.schema import AIMessage
from chatbot_core.memory.session_memory import memory 

from chatbot_core.chains.structure_chains import brief_structure_chain, detailed_structure_chain
from empty_room_gen.masking.modules.extract_detected_labels import extract_detected_labels
from empty_room_gen.masking.modules.detection_cache import DETECTED_RESULTS

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
    local_path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{image_id}.jpg"))

    async def event_stream():
        yield f"__IMAGE_ID__:{image_id}__END__STREAM__"

        # 객체 감지 실행
        detection_result = extract_detected_labels(
            image_path=local_path,
            config_path="empty_room_gen/masking/checkpoints/GroundingDINO_SwinT_OGC.py",
            grounded_ckpt="empty_room_gen/masking/checkpoints/groundingdino_swint_ogc.pth",
            sam_ckpt="empty_room_gen/masking/checkpoints/sam_vit_h_4b8939.pth",
            ram_ckpt="empty_room_gen/masking/checkpoints/ram_swin_large_14m.pth",
            device="cuda"
        )
        DETECTED_RESULTS[image_id] = detection_result

        # 간략 구조 설명 (Vision 기반)
        brief_msg = await brief_structure_chain.ainvoke({"image_path": local_path})
        brief = brief_msg.content
        yield f"[간략구조] {brief}\n"
        memory.save_context({"input": "[system] 간략 구조 설명"}, {"output": f"[간략구조] {brief}"})

        # 상세 구조 설명 (Vision 기반)
        detailed_msg = await detailed_structure_chain.ainvoke({"image_path": local_path})
        detailed = detailed_msg.content
        yield f"[상세구조] {detailed}\n"
        memory.save_context({"input": "[system] 상세 구조 설명"}, {"output": detailed})

        memory.save_context({"input": "[system] 이미지 경로"}, {"output": local_path})

    return StreamingResponse(event_stream(), media_type="text/plain")