# backend/interior/controlnet_inference.py

import torch
import numpy as np
import cv2
import uuid
import os
from PIL import Image, ImageDraw
from diffusers import StableDiffusionControlNetImg2ImgPipeline, ControlNetModel

# 환경에 따라 device 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] ControlNet running on: {device}")

# 모델 로딩
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
)

pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    safety_checker=None,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32
).to(device)

# 바닥만 흰색인 마스크 (선택사항 – 여기선 사용하지 않음)
def create_floor_mask(width=512, height=512) -> Image.Image:
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    floor_top = int(height * 2 / 3)
    draw.rectangle([0, floor_top, width, height], fill=255)

    os.makedirs("./data/debug", exist_ok=True)
    mask.save("./data/debug/floor_mask.jpg")

    return mask

# 메인 함수
def interior_with_controlnet(image_path: str, prompt: str) -> str:
    base_image = Image.open(image_path).convert("RGB").resize((512, 512))
    canny = cv2.Canny(np.array(base_image), 50, 150)
    control_img = Image.fromarray(canny).resize((512, 512))

    os.makedirs("./data/debug", exist_ok=True)
    control_img.save("./data/debug/canny_preview.jpg")

    # ✅ 프롬프트 로그
    print("\n" + "=" * 60)
    print("[🧠 ControlNet Prompt]")
    print(prompt)
    print("=" * 60 + "\n")

    # 이미지 생성 
    result = pipe(
        prompt=prompt,
        image=base_image,
        control_image=control_img,
        strength=0.5,  # 원본 유지 정도 (0.3~0.6 권장)
        guidance_scale=9.0,
        num_inference_steps=30
    ).images[0]

    # 결과 저장
    os.makedirs("./data/results", exist_ok=True)
    output_path = f"./data/results/{uuid.uuid4()}.jpg"
    result.save(output_path)
    return output_path
