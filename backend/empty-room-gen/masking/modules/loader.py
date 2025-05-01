from PIL import Image
import torch
import torchvision.transforms as TS
import groundingdino.datasets.transforms as T
from groundingdino.util.slconfig import SLConfig
from groundingdino.models import build_model
from groundingdino.util.utils import clean_state_dict

def load_image(image_path):
    image_pil = Image.open(image_path).convert("RGB")
    transform = T.Compose([
        T.RandomResize([800], max_size=1333),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    image, _ = transform(image_pil, None)
    return image_pil, image


def load_model_gdino(config_path, ckpt_path, device):
    args = SLConfig.fromfile(config_path)
    args.device = device
    model = build_model(args)
    ckpt = torch.load(ckpt_path, map_location="cpu")
    model.load_state_dict(clean_state_dict(ckpt["model"]), strict=False)
    model.eval()
    return model.to(device)