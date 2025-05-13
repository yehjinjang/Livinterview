import os
import sys
import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
import torchvision

# 커스텀 경로 append
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "Tag2Text"))
sys.path.append(os.path.join(BASE_DIR, "../recognize_anything"))

DEFAULT_CHECKPOINT = os.path.join(BASE_DIR, "checkpoints", "ram_swin_large_14m.pth")

# 커스텀 모듈 import
from empty_room_gen.masking.Tag2Text.models import tag2text
import empty_room_gen.masking.Tag2Text.inference_ram as inference_ram
from empty_room_gen.recognize_anything.segment_anything import build_sam, SamPredictor
from empty_room_gen.masking.modules.utils import normalize, is_must_keep
from empty_room_gen.masking.modules.detection_cache import DETECTED_RESULTS

# 마스크 보정 함수들
def fill_holes(mask_np: np.ndarray) -> np.ndarray:
    kernel = np.ones((50, 50), np.uint8)
    closed = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, kernel)
    flood_filled = closed.copy()
    h, w = flood_filled.shape
    mask2 = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(flood_filled, mask2, (0, 0), 255)
    inv_flood = cv2.bitwise_not(flood_filled)
    filled = cv2.bitwise_or(closed, inv_flood)
    return filled // 255

def fill_valleys(mask_np: np.ndarray) -> np.ndarray:
    kernel = np.ones((30, 30), np.uint8)
    dilated = cv2.dilate(mask_np, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(mask_np)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED)
    return filled // 255

# 메인 함수: 기존 감지 결과를 기반으로 마스크 생성
def create_removal_mask(args):
    device = args.device
    os.makedirs(args.output_dir, exist_ok=True)

    image_id = os.path.splitext(os.path.basename(args.input_image))[0]
    if image_id not in DETECTED_RESULTS:
        raise ValueError(f"[ERROR] 감지 결과가 존재하지 않음: {image_id}")

    boxes_px, masks, scores, cleaned_labels, (w, h) = DETECTED_RESULTS[image_id]

    # 선택된 인덱스 기반으로 남길 항목 계산
    if hasattr(args, "selected_indices") and args.selected_indices is not None:
        keep_items = [
            normalize(cleaned_labels[i]) 
            for i in args.selected_indices 
            if 0 <= i < len(cleaned_labels)
        ]
        print(f"[선택된 남길 항목]: {keep_items}")
    else:
        keep_items = []
        print("[⚠️ 선택된 항목 없음] → 전체 제거 대상 처리 (must_keep 제외)")

    remove_items = [
        label for label in cleaned_labels
        if normalize(label) not in keep_items and not is_must_keep(label)
    ]

    final_mask = None
    for i, (mask, label) in enumerate(zip(masks, cleaned_labels)):
        norm_label = normalize(label)
        if norm_label in remove_items:
            if isinstance(mask, torch.Tensor):
                mask_np = mask.squeeze(0).cpu().numpy().astype(np.uint8)
            else:
                mask_np = np.array(mask).astype(np.uint8)

            mask_area  = np.sum(mask_np)
            area_ratio = mask_area / (mask_np.shape[0] * mask_np.shape[1])
            padding    = int(50 + (100 - 50) * area_ratio)

            kernel = np.ones((padding, padding), np.uint8)
            mask_dilated = cv2.dilate(mask_np, kernel, iterations=1)
            mask_filled = fill_holes(mask_dilated)
            mask_filled = fill_valleys(mask_filled)

            path = os.path.join(args.output_dir, f"mask_{norm_label}_{i}.png")
            cv2.imwrite(path, mask_filled * 255)
            print(f"  Saved ({norm_label} / padding={padding}px / area_ratio={area_ratio:.3f})")

            final_mask = mask_filled if final_mask is None else np.maximum(final_mask, mask_filled)

    if final_mask is not None:
        final_mask_img = Image.fromarray(final_mask * 255).convert("RGB")
        final_mask_resized = final_mask_img.resize((w, h), resample=Image.NEAREST)
        final_mask_resized.save(os.path.join(args.output_dir, "merged_mask.png"))  # ✅ 이거 추가!
        return final_mask_resized
    else:
        return None