# masking/modules/extract_detected_labels.py

import torch
import numpy as np
import cv2
from PIL import Image
import torchvision.transforms as TS
import torchvision

from empty_room_gen.masking.modules.loader import load_image, load_model_gdino
from empty_room_gen.masking.modules.predictor import get_grounding_output
from empty_room_gen.masking.modules.utils import normalize, is_must_keep
from empty_room_gen.recognize_anything.segment_anything import build_sam, SamPredictor
from empty_room_gen.masking.Tag2Text.models import tag2text
import empty_room_gen.masking.Tag2Text.inference_ram as inference_ram

def extract_detected_labels(
    image_path: str,
    config_path: str,
    grounded_ckpt: str,
    sam_ckpt: str,
    ram_ckpt: str,
    box_threshold: float = 0.25,
    text_threshold: float = 0.2,
    iou_threshold: float = 0.5,
    device="cuda"
):
    # Load image
    image_pil, image_tensor = load_image(image_path)
    w, h = image_pil.size
    image_np = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    # Tag2Text inference
    ram_model = tag2text.ram(pretrained=ram_ckpt, image_size=384, vit='swin_l').to(device)
    ram_model.eval()
    ram_input = TS.Compose([
        TS.Resize((384, 384)),
        TS.ToTensor(),
        TS.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])(image_pil).unsqueeze(0).to(device)

    tags, _ = inference_ram.inference(ram_input, ram_model)
    prompt = tags.replace(" |", ",") + ", blanket, pillow, comforter, bedding, mattress cover"

    # Grounding DINO
    model = load_model_gdino(config_path, grounded_ckpt, device)
    boxes, scores, phrases = get_grounding_output(model, image_tensor, prompt, box_threshold, text_threshold, device)
    if len(boxes) == 0:
        return [], [], [], [], None

    # SAM predictor
    predictor = SamPredictor(build_sam(checkpoint=sam_ckpt).to(device))
    predictor.set_image(image_np)

    boxes_px = boxes * torch.tensor([w, h, w, h])
    boxes_px[:, :2] -= boxes_px[:, 2:] / 2
    boxes_px[:, 2:] += boxes_px[:, :2]
    boxes_px = boxes_px.cpu()

    keep = torchvision.ops.nms(boxes_px, scores, iou_threshold)
    boxes_px = boxes_px[keep]
    phrases = [phrases[i] for i in keep]

    transformed = predictor.transform.apply_boxes_torch(boxes_px, image_np.shape[:2]).to(device)
    masks, _, _ = predictor.predict_torch(boxes=transformed, point_coords=None, point_labels=None, multimask_output=False)

    cleaned_labels = [normalize(p.split("(")[0]) for p in phrases]
    filtered_indices = [i for i, label in enumerate(cleaned_labels) if not is_must_keep(label)]

    # 반환: 필터링된 박스, 마스크, 라벨
    return (
        [boxes_px[i] for i in filtered_indices],
        [masks[i] for i in filtered_indices],
        [scores[i] for i in filtered_indices],
        [cleaned_labels[i] for i in filtered_indices],
        (w, h)
    )
