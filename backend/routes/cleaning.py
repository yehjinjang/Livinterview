# routes/cleaning.py

from fastapi import APIRouter, Form
from typing import List, Optional
import os
from types import SimpleNamespace
from PIL import Image
import torch
from diffusers import AutoPipelineForInpainting

from empty_room_gen.masking.modules.detection_cache import DETECTED_RESULTS
from empty_room_gen.masking.modules.extract_detected_labels import extract_detected_labels
from empty_room_gen.masking.run import create_removal_mask
from chatbot_core.memory.session_memory import get_memory
import traceback
import shutil

router = APIRouter()

# ──────────────────────────────
# 경로·프롬프트 상수
# ──────────────────────────────
CHECKPOINT_DIR = "empty_room_gen/masking/checkpoints"
MODEL_CONFIG   = os.path.join(CHECKPOINT_DIR, "GroundingDINO_SwinT_OGC.py")
GDINO_CKPT     = os.path.join(CHECKPOINT_DIR, "groundingdino_swint_ogc.pth")
SAM_CKPT       = os.path.join(CHECKPOINT_DIR, "sam_vit_h_4b8939.pth")
RAM_CKPT       = os.path.join(CHECKPOINT_DIR, "ram_swin_large_14m.pth")

positive_prompt = "a completely empty room. minimalist. clean. nothing inside."
negative_prompt = (
    "furniture, objects, door, table, chairs, decoration, plant, curtain, "
    "shelf, carpet, lighting fixture, window, artwork, clutter"
)

# ──────────────────────────────
# 인페인팅 파이프라인 헬퍼
# ──────────────────────────────
def get_inpaint_pipeline():
    return AutoPipelineForInpainting.from_pretrained(
        "stabilityai/stable-diffusion-2-inpainting",
        torch_dtype=torch.float16
    ).to("cuda" if torch.cuda.is_available() else "cpu")

INPAINT_PIPE = get_inpaint_pipeline()

# ──────────────────────────────
# 1) 객체 감지 (전체 래핑)
# ──────────────────────────────
@router.post("/detect")
async def detect_objects(image_id: str = Form(...)):
    image_path = f"./data/uploads/{image_id}.jpg"
    if not os.path.exists(image_path):
        return {"status": "fail", "message": "해당 이미지를 찾을 수 없습니다."}

    try:
        boxes, masks, scores, labels, size = extract_detected_labels(
            image_path,
            MODEL_CONFIG,
            GDINO_CKPT,
            SAM_CKPT,
            RAM_CKPT,
            box_threshold=0.25,
            text_threshold=0.2,
            iou_threshold=0.5,
        )
        DETECTED_RESULTS[image_id] = (boxes, masks, scores, labels, size)
        return {"status": "success", "labels": sorted(set(labels))}
    except Exception:
        traceback.print_exc()
        return {"status": "error", "message": "감지 중 오류 발생"}

# ──────────────────────────────
# 2) 캐시된 라벨 반환
# ──────────────────────────────
@router.post("/labels")
async def detect_labels(image_id: str = Form(...)):
    cached = DETECTED_RESULTS.get(image_id)
    if not cached:
        return {"status": "fail", "message": "해당 이미지의 감지 결과가 없습니다."}
    _, _, _, labels, _ = cached
    if not labels:
        return {"status": "fail", "message": "감지된 객체가 없습니다."}
    return {"status": "success", "labels": sorted(set(labels))}

# ──────────────────────────────
# 3) 선택 기반 마스크 생성
# ──────────────────────────────
@router.post("/removal")
async def create_removal(
    image_id: str = Form(...),
    selected_indices: Optional[List[int]] = Form(None)
):
    cached = DETECTED_RESULTS.get(image_id)
    if not cached:
        return {"status": "fail", "message": "해당 이미지의 감지 결과가 없습니다."}
    boxes, masks, scores, labels, (w, h) = cached

    if selected_indices is None:
        selected_indices = []

    args = SimpleNamespace(
        image_id=image_id,
        output_dir=f"./data/results/{image_id}",
        input_image=f"./data/uploads/{image_id}.jpg",
        selected_indices=selected_indices,
        masks=masks,
        device="cuda"
    )
    create_removal_mask(args)
    result_path = os.path.join(args.output_dir, "merged_mask.png")
    if not os.path.exists(result_path):
        return {"status": "fail", "message": "마스크 생성 실패"}
    return {"status": "success", "mask_url": f"/static/results/{image_id}/merged_mask.png"}

# ──────────────────────────────
# 4) 인페인팅 실행
# ──────────────────────────────
@router.post("/inpaint")
async def run_inpaint(image_id: str = Form(...)):
    try:
        input_path = f"./data/uploads/{image_id}.jpg"
        output_path = f"./data/results/{image_id}/sd_inpainted_room.png"
        final_path = f"./data/uploads/{image_id}.jpg"

        if os.path.exists(output_path):
            return {"status": "success", "inpainted_url": f"/static/results/{image_id}/sd_inpainted_room.png"}

        if not os.path.exists(input_path):
            return {"status": "fail", "message": "업로드 이미지가 없습니다."}
        mask_path = f"./data/results/{image_id}/merged_mask.png"
        if not os.path.exists(mask_path):
            return {"status": "fail", "message": "마스크 이미지가 없습니다."}

        # inpainting
        pipe = INPAINT_PIPE
        orig = Image.open(input_path).convert("RGB")
        image = orig.resize((512, 512))
        mask = Image.open(mask_path).convert("L").resize((512, 512))

        # 메모리에서 [간략구조] 읽어와서 프롬프트에 반영
        memory = get_memory(image_id)
        brief_msgs = [
            m.content.replace("[간략구조]", "").strip()
            for m in memory.chat_memory.messages
            if m.content.startswith("[간략구조]")
        ]
        brief = brief_msgs[-1].split(".")[0] if brief_msgs else "a completely empty room. clean. nothing inside"
        prompt = f"{positive_prompt} This room has {brief}."

        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image,
            mask_image=mask,
            num_inference_steps=15,
            guidance_scale=10
        ).images[0]

        result.resize(orig.size, Image.LANCZOS).save(output_path)
        # 구조 분석을 위해 uploads 경로에도 저장
        shutil.copy(output_path, final_path)
        return {"status": "success", "inpainted_url": f"/static/results/{image_id}/sd_inpainted_room.png"}

    except Exception:
        traceback.print_exc()
        return {"status": "error", "message": "인페인팅 중 오류 발생"}
