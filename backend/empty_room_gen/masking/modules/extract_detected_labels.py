# masking/modules/extract_detected_labels.py
import re
from typing import Tuple, List

import cv2
import numpy as np
import torch
import torchvision
import torchvision.transforms as TS
from PIL import Image

from empty_room_gen.masking.modules.loader import load_image, load_model_gdino
from empty_room_gen.masking.modules.predictor import get_grounding_output
from empty_room_gen.masking.modules.utils import normalize, is_must_keep
from empty_room_gen.recognize_anything.segment_anything import build_sam, SamPredictor
import empty_room_gen.masking.Tag2Text.inference_ram as inference_ram
from empty_room_gen.masking.Tag2Text.models.tag2text import ram

# -------------------- 공통 유틸 --------------------
def normalize_label(label: str) -> str:
    """라벨 대·소문자/순서 무관 중복 제거용 키 반환"""
    return " ".join(sorted(set(re.findall(r"\w+", label.lower()))))

def deduplicate_labels(
    labels: List[str], scores: torch.Tensor, boxes, masks
) -> Tuple[list, list, list, list]:
    """동일 객체 중 score 최댓값만 남김"""
    label_map = {}
    for i, (lbl, score) in enumerate(zip(labels, scores)):
        key = normalize_label(lbl)
        if key not in label_map or label_map[key]["score"] < score:
            label_map[key] = {
                "label": key,
                "score": score,
                "box": boxes[i],
                "mask": masks[i],
            }
    return (
        [v["box"] for v in label_map.values()],
        [v["mask"] for v in label_map.values()],
        [v["score"] for v in label_map.values()],
        [v["label"] for v in label_map.values()],
    )

# -------------------- 모델 캐시 --------------------
class _ModelCache:
    _store: dict[str, object] = {}

    @classmethod
    def get(cls, key: str):
        return cls._store.get(key)

    @classmethod
    def add(cls, key: str, obj):
        cls._store[key] = obj
        return obj

def _get_or_build_ram(ram_ckpt: str, device: str):
    key = f"ram|{ram_ckpt}|{device}"
    mdl = _ModelCache.get(key)
    if mdl is None:
        mdl = ram(
            pretrained=ram_ckpt,
            image_size=384,
            vit="swin_l",            # 또는 swin_l / base / large 등 가중치에 맞게
            threshold=0.68,
            delete_tag_index=[]
        )
        mdl = mdl.to(device).eval()
        _ModelCache.add(key, mdl)
    return mdl

def _get_or_build_dino(config: str, ckpt: str, device: str):
    key = f"dino|{ckpt}|{device}"
    mdl = _ModelCache.get(key)
    if mdl is None:
        mdl = load_model_gdino(config, ckpt, device)
        _ModelCache.add(key, mdl)
    return mdl

def _get_or_build_sam(sam_ckpt: str, device: str):
    key = f"sam|{sam_ckpt}|{device}"
    mdl = _ModelCache.get(key)
    if mdl is None:
        mdl = build_sam(checkpoint=sam_ckpt).to(device)
        _ModelCache.add(key, mdl)
    return mdl

def _get_or_build_predictor(sam_ckpt: str, device: str):
    key = f"predictor|{sam_ckpt}|{device}"
    pred = _ModelCache.get(key)
    if pred is None:
        pred = SamPredictor(_get_or_build_sam(sam_ckpt, device))
        _ModelCache.add(key, pred)
    return pred

# -------------------- 메인 함수 --------------------
def extract_detected_labels(
    image_path: str,
    config_path: str,
    grounded_ckpt: str,
    sam_ckpt: str,
    ram_ckpt: str,
    box_threshold: float = 0.25,
    text_threshold: float = 0.2,
    iou_threshold: float = 0.5,
    device: str | None = None,
):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    # 이미지 불러오기
    image_pil, image_tensor = load_image(image_path)
    w, h = image_pil.size
    image_np = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    # ---------- 1) RAM 태깅 ----------
    ram_model = _get_or_build_ram(ram_ckpt, device)
    ram_input = (
        TS.Compose(
            [
                TS.Resize((384, 384)),
                TS.ToTensor(),
                TS.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )(image_pil)
        .unsqueeze(0)
        .to(device)
    )
    
    tags, _ = inference_ram.inference(ram_input, ram_model)
    print("[RAM TAGS]:", tags)

    # must_keep 아닌 항목만 필터링
    tag_list = [t.strip() for t in tags.split("|")]
    filtered_tags = [t for t in tag_list if not is_must_keep(t)]

    prompt = f"{', '.join(filtered_tags)}, blanket, pillow, comforter, bedding, mattress cover"
    print("[GROUNDING PROMPT]:", prompt)

    # ---------- 2) Grounding DINO ----------
    dino_model = _get_or_build_dino(config_path, grounded_ckpt, device)
    boxes, scores, phrases = get_grounding_output(
        dino_model,
        image_tensor,
        prompt,
        box_threshold,
        text_threshold,
        device,
    )
    if len(boxes) == 0:
        return [], [], [], [], (w, h)

    # ---------- 3) SAM 마스킹 ----------
    predictor = _get_or_build_predictor(sam_ckpt, device)
    predictor.set_image(image_np)

    boxes_px = boxes * torch.tensor([w, h, w, h], dtype=boxes.dtype, device=boxes.device)
    boxes_xyxy = torch.empty_like(boxes_px)
    boxes_xyxy[:, :2] = boxes_px[:, :2] - boxes_px[:, 2:] / 2
    boxes_xyxy[:, 2:] = boxes_px[:, :2] + boxes_px[:, 2:] / 2

    keep = torchvision.ops.nms(boxes_xyxy.cpu(), scores.cpu(), iou_threshold)
    boxes_xyxy = boxes_xyxy[keep]
    kept_scores = scores[keep]
    kept_labels = [phrases[i] for i in keep]

    transformed = predictor.transform.apply_boxes_torch(
        boxes_xyxy, image_np.shape[:2]
    ).to(device)
    masks, _, _ = predictor.predict_torch(
        boxes=transformed,
        point_coords=None,
        point_labels=None,
        multimask_output=False,
    )
    masks = [m.squeeze(0).cpu().numpy().astype(np.uint8) for m in masks]

    # ---------- 4) dedup + 필터 ----------
    boxes_d, masks_d, scores_d, labels_d = deduplicate_labels(
        kept_labels, kept_scores, boxes_xyxy.cpu(), masks
    )
    filt_idx = [i for i, lbl in enumerate(labels_d) if not is_must_keep(lbl)]
    final_boxes = [boxes_d[i] for i in filt_idx]
    final_masks = [masks_d[i] for i in filt_idx]
    final_scores = [scores_d[i] for i in filt_idx]
    final_labels = [labels_d[i] for i in filt_idx]

    # ---------- 5) 로그 ----------
    print("[✅ 감지된 라벨]:", final_labels)
    print("[✅ 박스 개수]:", len(final_boxes))

    return final_boxes, final_masks, final_scores, final_labels, (w, h)
