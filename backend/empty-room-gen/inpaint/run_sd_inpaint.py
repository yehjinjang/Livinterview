from diffusers import AutoPipelineForInpainting
from PIL import Image
import torch

# Load pipeline
pipe = AutoPipelineForInpainting.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    torch_dtype=torch.float32
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# Load original image and mask
original_image = Image.open("inpaint/test2.png").convert("RGB")
original_size = original_image.size

# SD 2.x inpainting 권장 해상도: 512x512
image = original_image.resize((512, 512))
mask = Image.open("inpaint/merged_mask.png").convert("RGB").resize((512, 512))

# Prompts
positive_prompt = "a completely empty room. minimalist. clean. nothing inside."
negative_prompt = (
    "furniture, objects, table, chairs, decoration, plant, curtain, shelf, carpet, lighting fixture, window, artwork, clutter"
)

# Inpaint
result = pipe(
    prompt=positive_prompt,
    negative_prompt=negative_prompt,
    image=image,
    mask_image=mask
).images[0]

# Resize back to original size
result = result.resize(original_size, Image.LANCZOS)
result.save("inpaint/sd_inpainted_room.png")
