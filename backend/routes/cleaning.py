from fastapi import APIRouter, Form
from typing import List
from empty_room_gen.masking.run import create_removal_mask
from empty_room_gen.masking.modules.extract_detected_labels import extract_detected_labels
from types import SimpleNamespace
from PIL import Image
from diffusers import AutoPipelineForInpainting
import os
import torch

router = APIRouter()

# ────────────────
# 인페인팅 모델 로딩 (전역)
# ────────────────
pipe = AutoPipelineForInpainting.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float32
).to("cuda" if torch.cuda.is_available() else "cpu")

positive_prompt = "a completely empty room. minimalist. clean. nothing inside."
negative_prompt = (
    "furniture, objects, table, chairs, decoration, plant, curtain, shelf, carpet, lighting fixture, window, artwork, clutter"
)

# ──────────────────────────────
# 경로 상수
# ──────────────────────────────
CHECKPOINT_DIR = "empty_room_gen/masking/checkpoints"
MODEL_CONFIG = "empty_room_gen/models/GroundingDINO_SwinT/config.py"

# ──────────────────────────────
# 객체 라벨 추출
# ──────────────────────────────
@router.post("/labels")
async def detect_labels(image_id: str = Form(...)):
    image_path = f"./data/uploads/{image_id}.jpg"
    try:
        _, _, _, cleaned_labels, _ = extract_detected_labels(
            image_path=image_path,
            config_path=MODEL_CONFIG,
            grounded_ckpt=os.path.join(CHECKPOINT_DIR, "groundingdino.pth"),
            sam_ckpt=os.path.join(CHECKPOINT_DIR, "sam_vit_h.pth"),
            ram_ckpt=os.path.join(CHECKPOINT_DIR, "tag2text_swin_14m.pth"),
            box_threshold=0.25,
            text_threshold=0.2,
            iou_threshold=0.5,
            device="cuda"
        )

        if not cleaned_labels:
            return {"status": "fail", "message": "감지된 객체가 없습니다."}

        return {"status": "success", "labels": sorted(set(cleaned_labels))}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ──────────────────────────────
# 마스크 생성 (선택 제외 기반)
# ──────────────────────────────
@router.post("/removal")
async def create_removal(
    image_id: str = Form(...),
    selected_items: List[str] = Form(...)
):
    if not selected_items:
        return {"status": "fail", "message": "선택된 객체가 없습니다."}

    args = SimpleNamespace(
        input_image=f"./data/uploads/{image_id}.jpg",
        output_dir=f"./data/results/{image_id}",
        selected_items=selected_items,
        device="cuda",
        config=MODEL_CONFIG,
        grounded_checkpoint=os.path.join(CHECKPOINT_DIR, "groundingdino.pth"),
        sam_checkpoint=os.path.join(CHECKPOINT_DIR, "sam_vit_h.pth"),
        ram_checkpoint=os.path.join(CHECKPOINT_DIR, "tag2text_swin_14m.pth"),
        box_threshold=0.25,
        text_threshold=0.2,
        iou_threshold=0.5,
    )

    removed_items = create_removal_mask(args)
    result_path = os.path.join(args.output_dir, "merged_mask.png")
    if not os.path.exists(result_path):
        return {"status": "fail", "message": "마스크 생성 실패"}

    return {
        "status": "success",
        "mask_url": f"/static/results/{image_id}/merged_mask.png",
        "removed_items": removed_items
    }

# ──────────────────────────────
# 인페인팅 실행
# ──────────────────────────────
@router.post("/inpaint")
async def run_inpaint(image_id: str = Form(...)):
    try:
        input_path = f"./data/uploads/{image_id}.jpg"
        original_image = Image.open(input_path).convert("RGB")
        original_size = original_image.size
        image = original_image.resize((512, 512))

        args = SimpleNamespace(
            input_image=input_path,
            output_dir=f"./data/results/{image_id}",
            selected_items=[],
            device="cuda",
            config=MODEL_CONFIG,
            grounded_checkpoint=os.path.join(CHECKPOINT_DIR, "groundingdino.pth"),
            sam_checkpoint=os.path.join(CHECKPOINT_DIR, "sam_vit_h.pth"),
            ram_checkpoint=os.path.join(CHECKPOINT_DIR, "tag2text_swin_14m.pth"),
            box_threshold=0.25,
            text_threshold=0.2,
            iou_threshold=0.5,
        )
        os.makedirs(args.output_dir, exist_ok=True)

        mask_image = create_removal_mask(args)
        if mask_image is None:
            return {"status": "fail", "message": "마스크 생성 실패"}

        mask = mask_image.resize((512, 512))

        result = pipe(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            image=image,
            mask_image=mask
        ).images[0]

        result = result.resize(original_size, Image.LANCZOS)
        output_path = os.path.join(args.output_dir, "sd_inpainted_room.png")
        result.save(output_path)

        return {
            "status": "success",
            "inpainted_url": f"/static/results/{image_id}/sd_inpainted_room.png"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
