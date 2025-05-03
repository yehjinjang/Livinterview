import os
import sys
import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as TS
import torchvision

# Tag2Text 및 segment_anything 모듈을 로컬 경로로 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "Tag2Text"))
sys.path.append(os.path.join(BASE_DIR, "../recognize_anything"))

from models import tag2text
import inference_ram
from segment_anything import build_sam, SamPredictor
from masking.modules.loader import load_image, load_model_gdino
from masking.modules.predictor import get_grounding_output, get_sam_masks
from masking.modules.utils import normalize, is_must_keep

# 내부 구멍 메우기 함수 추가
def fill_holes(mask_np: np.ndarray) -> np.ndarray:
    # Step 1: Morphological Closing (닫힘 연산) - 작은 구멍 막기
    kernel = np.ones((15, 15), np.uint8)
    closed = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, kernel)

    # Step 2: Flood Fill 외부 채우기
    flood_filled = closed.copy()
    h, w = flood_filled.shape
    mask2 = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(flood_filled, mask2, (0, 0), 255)

    # Step 3: 반전해서 내부 구멍만 추출 후 원본과 OR
    inv_flood = cv2.bitwise_not(flood_filled)
    filled = cv2.bitwise_or(closed, inv_flood)
    return filled // 255  # 결과를 binary 형태로 변환

# 기본적으로 남겨야 할 키워드 정의
MUST_KEEP_KEYWORDS = ["room", "floor", "wall", "door", "window"]

def inference_ram_multiple_regions(image_pil, model, device, crop_size=384):
    transform = TS.Compose([
        TS.Resize((crop_size, crop_size)),
        TS.ToTensor(),
        TS.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    w, h = image_pil.size
    crops = [
        image_pil.crop((0, 0, w//2, h//2)),         # top-left
        image_pil.crop((w//2, 0, w, h//2)),         # top-right
        image_pil.crop((0, h//2, w//2, h)),         # bottom-left
        image_pil.crop((w//2, h//2, w, h))          # bottom-right
    ]

    all_tags = []
    for crop in crops:
        input_tensor = transform(crop).unsqueeze(0).to(device)
        tags, _ = inference_ram.inference(input_tensor, model)
        tags = tags.replace(" |", ",").split(",")
        tags = [normalize(t.strip()) for t in tags]
        all_tags.extend(tags)

    return sorted(set(all_tags))

def create_removal_mask(args):
    device = args.device
    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Load image
    image_pil, image_tensor = load_image(args.input_image)
    w, h = image_pil.size
    image_np = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    image_pil.save(os.path.join(args.output_dir, "raw_image.jpg"))

    # 2. Tag2Text tagging
    ram_model = tag2text.ram(pretrained=args.ram_checkpoint, image_size=384, vit='swin_l')
    ram_model.eval().to(device)
    ram_input = TS.Compose([
        TS.Resize((384, 384)),
        TS.ToTensor(),
        TS.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])(image_pil).unsqueeze(0).to(device)

    tags, _ = inference_ram.inference(ram_input, ram_model)
    prompt = tags.replace(" |", ",") + ", blanket, pillow, comforter, bedding, mattress cover"
    print("Predicted Tags:", prompt)

    # 3. Grounding DINO
    model = load_model_gdino(args.config, args.grounded_checkpoint, device)
    boxes, scores, phrases = get_grounding_output(model, image_tensor, prompt, args.box_threshold, args.text_threshold, device)
    if len(boxes) == 0:
        print("No boxes found.")
        return

    predictor = SamPredictor(build_sam(checkpoint=args.sam_checkpoint).to(device))
    predictor.set_image(image_np)

    boxes_px = boxes * torch.tensor([w, h, w, h])
    boxes_px[:, :2] -= boxes_px[:, 2:] / 2
    boxes_px[:, 2:] += boxes_px[:, :2]
    boxes_px = boxes_px.cpu()
    keep = torchvision.ops.nms(boxes_px, scores, args.iou_threshold)
    boxes_px = boxes_px[keep]
    phrases = [phrases[i] for i in keep]
    transformed = predictor.transform.apply_boxes_torch(boxes_px, image_np.shape[:2]).to(device)
    masks, _, _ = predictor.predict_torch(boxes=transformed, point_coords=None, point_labels=None, multimask_output=False)

    cleaned_labels = [normalize(p.split("(")[0]) for p in phrases]
    unique_labels = sorted(set(label for label in cleaned_labels if not is_must_keep(label)))

    print("\n마스킹 가능한 항목:")
    for label in unique_labels:
        print(f" - {label}")

    keep_input = input("\n남길 가구를 ,로 구분해서 입력하세요 (예: shelf,pillow,sofa):\n")
    keep_items = [normalize(k) for k in keep_input.split(",") if k.strip()]
    remove_items = [label for label in cleaned_labels if label not in keep_items and not is_must_keep(label)]

    final_mask = None
    for i, (mask, label) in enumerate(zip(masks, cleaned_labels)):
        if label in remove_items:
            mask_np = mask[0].cpu().numpy().astype(np.uint8)

            # 마스크 면적 기반 팽창 처리
            mask_area = np.sum(mask_np)
            area_ratio = mask_area / (mask_np.shape[0] * mask_np.shape[1])
            padding = int(50 + (100 - 50) * area_ratio)  # 최소 50, 최대 100
            kernel = np.ones((padding, padding), np.uint8)
            mask_dilated = cv2.dilate(mask_np, kernel, iterations=1)

            # 💡 내부 구멍 메우기
            mask_filled = fill_holes(mask_dilated)

            path = os.path.join(args.output_dir, f"mask_{label}_{i}.png")
            cv2.imwrite(path, mask_filled * 255)
            print(f"  💾 Saved ({label} / padding={padding}px / area_ratio={area_ratio:.3f})")

            final_mask = mask_filled if final_mask is None else np.maximum(final_mask, mask_filled)

    if final_mask is not None:
        merged_path = os.path.join(args.output_dir, "merged_mask.png")
        final_mask_img = Image.fromarray(final_mask * 255).convert("L")
        final_mask_resized = final_mask_img.resize((w, h), resample=Image.NEAREST)
        final_mask_resized.save(merged_path)
        print(f"\n✅ 병합 마스크 저장 완료 (리사이즈 포함): {merged_path}")
    else:
        print("⚠️ 병합할 마스크가 없습니다.")