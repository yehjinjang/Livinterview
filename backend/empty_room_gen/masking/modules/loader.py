# empty_room_gen/masking/modules/loader.py

import os
import torch
from PIL import Image
import torchvision.transforms as TS
import groundingdino.datasets.transforms as GD
from groundingdino.util.slconfig import SLConfig
from groundingdino.models import build_model
from groundingdino.util.utils import clean_state_dict
from segment_anything import sam_model_registry, SamPredictor
from empty_room_gen.masking.Tag2Text.inference_ram import ram as RAMModel

def load_image(image_path: str):
    image_pil = Image.open(image_path).convert("RGB")
    resized_pil, _ = GD.RandomResize([800], max_size=1333)(image_pil, None)
    image_tensor = TS.ToTensor()(resized_pil)
    return image_pil, image_tensor

def load_model(config_path: str, ckpt_path: str, device: str = "cpu"):
    # 1) Grounding DINO
    if config_path and os.path.exists(config_path) and os.path.exists(ckpt_path):
        args = SLConfig.fromfile(config_path)
        args.device = device
        model = build_model(args)
        ckpt = torch.load(ckpt_path, map_location="cpu")
        model.load_state_dict(clean_state_dict(ckpt["model"]), strict=False)
        model.eval()
        return model.to(device)

    # 2) SAM
    basename = os.path.basename(ckpt_path or "").lower()
    if "sam" in basename and os.path.exists(ckpt_path):
        backbone = sam_model_registry["default"](checkpoint=ckpt_path).to(device)
        return SamPredictor(backbone)

    # 3) RAM — inference_ram.py에 정의된 ram() 함수 사용
    if os.path.exists(ckpt_path):
        # inference_ram.py: ram(pretrained=..., image_size=..., vit=...) 로 모델 생성
        model = RAMModel(pretrained=ckpt_path, image_size=384, vit="swin_l")
        model.to(device).eval()
        return model

    raise ValueError(f"모델 로드 실패: config={config_path}, ckpt={ckpt_path}")
