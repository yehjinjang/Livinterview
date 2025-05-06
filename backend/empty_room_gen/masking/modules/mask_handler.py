import numpy as np
import os
import cv2
from PIL import Image

def save_and_merge_masks(masks, labels, remove_items, output_dir, image_shape):
    print("\n 마스크 저장 중...")
    w, h = image_shape
    final_mask = None

    for i, (mask, label) in enumerate(zip(masks, labels)):
        if label in remove_items:
            mask_np = mask[0].cpu().numpy().astype(np.uint8)

            mask_area = np.sum(mask_np)
            h_, w_ = mask_np.shape
            image_area = h_ * w_
            area_ratio = mask_area / image_area

            base_padding = 40
            max_padding = 90
            padding = int(base_padding + (max_padding - base_padding) * area_ratio)

            kernel = np.ones((padding, padding), np.uint8)
            mask_dilated = cv2.dilate(mask_np, kernel, iterations=1)

            path = os.path.join(output_dir, f"mask_{label}_{i}.png")
            cv2.imwrite(path, mask_dilated * 255)
            print(f"  Saved ({label} / padding={padding}px / area_ratio={area_ratio:.3f})")

            final_mask = mask_dilated if final_mask is None else np.maximum(final_mask, mask_dilated)

    if final_mask is not None:
        merged_path = os.path.join(output_dir, "merged_mask.png")

        final_mask_img = Image.fromarray(final_mask * 255).convert("L")
        final_mask_resized = final_mask_img.resize((w, h), resample=Image.NEAREST)
        final_mask_resized.save(merged_path)

        print(f"\n병합 마스크 저장 완료 (리사이즈 포함): {merged_path}")
    else:
        print("병합할 마스크가 없습니다.")