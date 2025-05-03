import os
import sys
import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as TS
import torchvision

# Tag2Text, RAM, SAM 등 로컬 모듈 경로 추가
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "Tag2Text"))
sys.path.append(os.path.join(BASE_DIR, "../recognize_anything"))

# 필요한 커스텀 모듈 import
from models import tag2text
import inference_ram
from segment_anything import build_sam, SamPredictor
from masking.modules.loader import load_image, load_model_gdino
from masking.modules.predictor import get_grounding_output, get_sam_masks
from masking.modules.utils import normalize, is_must_keep

### 마스킹 보완 함수들
# 마스크 내부의 작은 구멍을 메우기 위한 함수 (closing + flood fill 조합)
def fill_holes(mask_np: np.ndarray) -> np.ndarray:
    kernel = np.ones((50, 50), np.uint8) # 커널 크기로 채우는 강도 조절
    closed = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, kernel) # 작은 구멍 닫기

    flood_filled = closed.copy()
    h, w = flood_filled.shape
    mask2 = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(flood_filled, mask2, (0, 0), 255) # 외곽부터 채우기

    inv_flood = cv2.bitwise_not(flood_filled)
    filled = cv2.bitwise_or(closed, inv_flood) # 내부만 보존
    return filled // 255

# 객체 경계가 울퉁불퉁할 때, 골짜기처럼 남는 영역을 메우기 위한 함수
def fill_valleys(mask_np: np.ndarray) -> np.ndarray:
    kernel = np.ones((30, 30), np.uint8)  # 커널 조절
    dilated = cv2.dilate(mask_np, kernel, iterations=2)  # 두 번 확장해서 윤곽선 완화
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(mask_np)
    cv2.drawContours(filled, contours, -1, 255, thickness=cv2.FILLED) # 전체를 채움
    return filled // 255

MUST_KEEP_KEYWORDS = ["room", "floor", "wall", "door", "window", "apartment"]

### Tag2Text로 이미지에 있는 태그 추출
# 이미지를 4등분해서 각 영역의 태그를 추출 → 객체 인식 누락 방지
def inference_ram_multiple_regions(image_pil, model, device, crop_size=384):
    transform = TS.Compose([
        TS.Resize((crop_size, crop_size)),
        TS.ToTensor(),
        TS.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    w, h = image_pil.size
    crops = [
        image_pil.crop((0, 0, w//2, h//2)),
        image_pil.crop((w//2, 0, w, h//2)),
        image_pil.crop((0, h//2, w//2, h)),
        image_pil.crop((w//2, h//2, w, h))
    ]

    all_tags = []
    for crop in crops:
        input_tensor = transform(crop).unsqueeze(0).to(device)
        tags, _ = inference_ram.inference(input_tensor, model)
        tags = tags.replace(" |", ",").split(",")
        tags = [normalize(t.strip()) for t in tags]
        all_tags.extend(tags)

    return sorted(set(all_tags))


### 메인 함수: 객체 마스크 생성 및 병합
def create_removal_mask(args):
    device = args.device
    os.makedirs(args.output_dir, exist_ok=True)

    # 이미지 로딩 및 전처리
    image_pil, image_tensor = load_image(args.input_image)
    w, h = image_pil.size
    image_np = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    image_pil.save(os.path.join(args.output_dir, "raw_image.jpg"))

    # Tag2Text로 태그 예측
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

    # Grounding DINO로 객체 검출
    model = load_model_gdino(args.config, args.grounded_checkpoint, device)
    boxes, scores, phrases = get_grounding_output(model, image_tensor, prompt, args.box_threshold, args.text_threshold, device)
    if len(boxes) == 0:
        print("No boxes found.")
        return

    # SAM으로 마스크 생성
    predictor = SamPredictor(build_sam(checkpoint=args.sam_checkpoint).to(device))
    predictor.set_image(image_np)

    # 박스 좌표를 실제 픽셀로 변환 후 NMS 적용
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

    # 사용자에게 남길 항목 입력받고 제거 대상 분리
    keep_input = input("\n남길 가구를 ,로 구분해서 입력하세요 (예: shelf,pillow,sofa):\n")
    keep_items = [normalize(k) for k in keep_input.split(",") if k.strip()]
    remove_items = [label for label in cleaned_labels if label not in keep_items and not is_must_keep(label)]

    # 마스크 처리 및 보완
    final_mask = None
    for i, (mask, label) in enumerate(zip(masks, cleaned_labels)):
        if label in remove_items:
            mask_np = mask[0].cpu().numpy().astype(np.uint8)
            mask_area = np.sum(mask_np)
            area_ratio = mask_area / (mask_np.shape[0] * mask_np.shape[1])
            padding = int(50 + (100 - 50) * area_ratio)

            # 마스크 팽창 → 구멍 채움 → 골짜기 채움
            kernel = np.ones((padding, padding), np.uint8)
            mask_dilated = cv2.dilate(mask_np, kernel, iterations=1)
            mask_filled = fill_holes(mask_dilated)
            mask_filled = fill_valleys(mask_filled)

            # 파일 저장 및 마스크 병합
            path = os.path.join(args.output_dir, f"mask_{label}_{i}.png")
            cv2.imwrite(path, mask_filled * 255)
            print(f"  Saved ({label} / padding={padding}px / area_ratio={area_ratio:.3f})")

            final_mask = mask_filled if final_mask is None else np.maximum(final_mask, mask_filled)

    # 최종 마스크 병합 결과 저장
    if final_mask is not None:
        merged_path = os.path.join(args.output_dir, "merged_mask.png")
        final_mask_img = Image.fromarray(final_mask * 255).convert("L")
        final_mask_resized = final_mask_img.resize((w, h), resample=Image.NEAREST)
        final_mask_resized.save(merged_path)
        print(f"\n병합 마스크 저장 완료 (리사이즈 포함): {merged_path}")
    else:
        print("병합할 마스크가 없습니다.")
