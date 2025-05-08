from PIL import Image
import torch
import torchvision.transforms as TS
import groundingdino.datasets.transforms as GD
from groundingdino.util.slconfig import SLConfig
from groundingdino.models        import build_model
from groundingdino.util.utils    import clean_state_dict

def load_image(image_path):
    image_pil = Image.open(image_path).convert("RGB")

    # 1) Grounding‑DINO 전처리: RandomResize → PIL.Image 반환
    resized_pil, _ = GD.RandomResize([800], max_size=1333)(image_pil, None)

    # 2) TorchVision → Tensor [C,H,W]
    image_tensor = TS.ToTensor()(resized_pil)

    return image_pil, image_tensor        # ← 두 번째 값이 텐서!

def load_model_gdino(config_path, ckpt_path, device):
    args  = SLConfig.fromfile(config_path)
    args.device = device
    model = build_model(args)
    ckpt  = torch.load(ckpt_path, map_location="cpu")
    model.load_state_dict(clean_state_dict(ckpt["model"]), strict=False)
    model.eval()
    print(args.backbone)
    return model.to(device)