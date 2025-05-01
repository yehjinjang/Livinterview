import os
import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as TS
from segment_anything import build_sam, SamPredictor

import sys

# Tag2Text 모듈을 로컬 경로로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "Tag2Text"))
from models import tag2text
import inference_ram

# 나머지 masking 모듈
from masking.modules.loader import load_image, load_model_gdino
from masking.modules.predictor import get_grounding_output, get_sam_masks
from masking.modules.mask_handler import save_and_merge_masks
from masking.modules.utils import normalize, is_must_keep

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

    masks, keep = get_sam_masks(predictor, boxes_px, scores, args.iou_threshold, image_np.shape[:2])
    phrases = [phrases[i] for i in keep]
    cleaned_labels = [normalize(p.split("(")[0]) for p in phrases]
    unique_labels = sorted(set(label for label in cleaned_labels if not is_must_keep(label)))

    print("\n마스킹 가능한 항목:")
    for label in unique_labels:
        print(f" - {label}")

    keep_input = input("\n남길 가구를 ,로 구분해서 입력하세요 (예: shelf,pillow,sofa):\n")
    keep_items = [normalize(k) for k in keep_input.split(",") if k.strip()]
    remove_items = [
        label for label in cleaned_labels
        if label not in keep_items and not is_must_keep(label)
    ]

    save_and_merge_masks(masks, cleaned_labels, remove_items, args.output_dir, (w, h))