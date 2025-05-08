from fastapi import APIRouter, Form
from typing import List
from empty_room_gen.masking.run import create_removal_mask
from empty_room_gen.masking.modules.detection_cache import DETECTED_RESULTS
from types import SimpleNamespace
from PIL import Image
from diffusers import AutoPipelineForInpainting
import os
import torch
from chatbot_core.memory.session_memory import memory
import traceback
from typing import List, Optional 

router = APIRouter()

# 모델 로딩을 함수로 정의
def load_models():
    groundingdino_model = load_model(
        "empty_room_gen/masking/checkpoints/GroundingDINO_SwinT_OGC.py", 
        "empty_room_gen/masking/checkpoints/groundingdino_swint_ogc.pth", 
        "cuda"
    )
    sam_model = load_model(
        "empty_room_gen/masking/checkpoints/sam_vit_h_4b8939.pth", 
        "", 
        "cuda"
    )
    ram_model = load_model(
        "empty_room_gen/masking/checkpoints/ram_swin_large_14m.pth", 
        "", 
        "cuda"
    )
    return groundingdino_model, sam_model, ram_model

# ──────────────────────────────
# 인페인팅 모델 지연 로딩 함수
# ──────────────────────────────
def get_inpaint_pipeline():
    return AutoPipelineForInpainting.from_pretrained(
        "stabilityai/stable-diffusion-2-inpainting",
        torch_dtype=torch.float16
    ).to("cuda" if torch.cuda.is_available() else "cpu")


# ──────────────────────────────
# 프롬프트 상수
# ──────────────────────────────

positive_prompt = "a completely empty room. minimalist. clean. nothing inside."
negative_prompt = (
    "furniture, objects, table, chairs, decoration, plant, curtain, shelf, carpet, lighting fixture, window, artwork, clutter"
)

# ──────────────────────────────
# 경로 상수
# ──────────────────────────────
CHECKPOINT_DIR   = "empty_room_gen/masking/checkpoints"
RAM_CKPT         = os.path.join(CHECKPOINT_DIR, "ram_swin_large_14m.pth")
GDINO_CKPT       = os.path.join(CHECKPOINT_DIR, "groundingdino_swint_ogc.pth")
SAM_CKPT         = os.path.join(CHECKPOINT_DIR, "sam_vit_h_4b8939.pth")
MODEL_CONFIG     = os.path.join(CHECKPOINT_DIR, "GroundingDINO_SwinT_OGC.py")

# ──────────────────────────────
# 감지된 객체 라벨 목록 반환
# ──────────────────────────────
@router.post("/labels")
async def detect_labels(image_id: str = Form(...)):
    cached = DETECTED_RESULTS.get(image_id)
    if not cached:
        return {"status": "fail", "message": "해당 이미지의 감지 결과가 없습니다."}

    _, _, _, cleaned_labels, _ = cached

    if not cleaned_labels:
        return {"status": "fail", "message": "감지된 객체가 없습니다."}

    return {"status": "success", "labels": sorted(set(cleaned_labels))}

# ──────────────────────────────
# 마스크 생성 (선택 제외 기반, 인덱스 기반 선택)
# ──────────────────────────────
@router.post("/removal")
async def create_removal(
    image_id: str = Form(...),
    selected_indices: Optional[List[int]] = Form(None)
):
    cached = DETECTED_RESULTS.get(image_id)
    if not cached:
        return {"status": "fail", "message": "해당 이미지의 감지 결과가 없습니다."}

    boxes, masks, scores, cleaned_labels, (w, h) = cached

    if not selected_indices:
        print("[선택된 항목 없음] → 전체 제거 대상 처리 (must_keep 제외)")
        selected_indices = []

    args = SimpleNamespace(
        image_id=image_id,
        output_dir=f"./data/results/{image_id}",
        input_image=f"./data/uploads/{image_id}.jpg",  
        selected_indices=selected_indices,
        masks=masks,
        device="cuda"
    )


    removal_mask = create_removal_mask(args)
    result_path = os.path.join(args.output_dir, "merged_mask.png")

    if not os.path.exists(result_path):
        return {"status": "fail", "message": "마스크 생성 실패"}

    # removed_items 리스트 필요 없음. 그냥 성공하면 URL만 넘겨줘
    return {
        "status": "success",
        "mask_url": f"/static/results/{image_id}/merged_mask.png"
    }

# ──────────────────────────────
# 인페인팅 실행
# ──────────────────────────────
@router.post("/inpaint")
async def run_inpaint(image_id: str = Form(...)):
    try:
        print(f"[inpaint] 요청 받은 image_id: {image_id}")
        input_path = f"./data/uploads/{image_id}.jpg"
        output_path = os.path.join(f"./data/results/{image_id}", "sd_inpainted_room.png")

        if os.path.exists(output_path):
            print("[inpaint] 이미 존재하는 이미지, 재생성 안 함")
            return {
                "status": "success",
                "inpainted_url": f"/static/results/{image_id}/sd_inpainted_room.png"
            }

        if not os.path.exists(input_path):
            print(f"[inpaint] 업로드된 이미지 없음: {input_path}")
            return {"status": "fail", "message": "업로드 이미지가 없습니다."}

        mask_path = os.path.join(f"./data/results/{image_id}", "merged_mask.png")
        if not os.path.exists(mask_path):
            print(f"[inpaint] 마스크 이미지 없음: {mask_path}")
            return {"status": "fail", "message": "마스크 이미지가 없습니다."}

        original_image = Image.open(input_path).convert("RGB")
        original_size = original_image.size
        image = original_image.resize((512, 512))

        mask_image = Image.open(mask_path).convert("L")
        mask = mask_image.resize((512, 512))

        # 프롬프트 구성
        brief_msgs = [
            m.content.replace("[간략구조]", "").strip()
            for m in memory.chat_memory.messages
            if m.content.startswith("[간략구조]")
        ]
        brief = brief_msgs[-1].split(".")[0] if brief_msgs else "a completely empty room. clean. nothing inside"
        inpaint_prompt = (
                f"{positive_prompt} "
                f"This room has {brief}. "
                "Please inpaint missing or removed objects while preserving the room's original structure, wall materials, and layout."
            )
        print(f"[inpaint] 프롬프트: {inpaint_prompt}")

        # 모델 실행
        pipe = get_inpaint_pipeline() 
        result = pipe(
            prompt=inpaint_prompt,
            negative_prompt=negative_prompt,
            image=image,
            mask_image=mask,
            num_inference_steps=25,
            guidance_scale=7.5
        ).images[0]

        result = result.resize(original_size, Image.LANCZOS)
        result.save(output_path)

        if not os.path.exists(output_path):
            print(f"[inpaint] 결과 저장 실패: {output_path}")
            return {"status": "fail", "message": "결과 저장 실패"}

        print(f"[inpaint] 최종 이미지 저장 완료: {output_path}")
        return {
            "status": "success",
            "inpainted_url": f"/static/results/{image_id}/sd_inpainted_room.png"
        }

    except Exception as e:
        print("[inpaint] 예외 전체 트레이스 ↓↓↓")
        traceback.print_exc()
        return {
            "status": "error",
            "message": "인페인팅 중 오류 발생",
            "detail": str(e)
        }