import os
import shutil
import sys
from pathlib import Path

# ------------------------------------------------------------
# 경로 설정
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
LAMA_DIR = BASE_DIR.parent.parent.parent / "lama"
sys.path.append(str(LAMA_DIR))  # saicinpainting import 가능하게 함

MODEL_PATH = LAMA_DIR / "pretrained_models/big-lama"
INPUT_DIR = BASE_DIR / "lama_input"
OUTPUT_DIR = BASE_DIR / "lama_output"

# 입력 이미지 및 마스크 이름
RAW_IMG_NAME = "room.png"
MASK_IMG_NAME = "room_mask.png"

# inpaint 대상 이미지 및 마스크 경로
RAW_IMAGE = BASE_DIR / "test.png"
MASK_IMAGE = BASE_DIR / "merged_mask.png"

def prepare_input():
    if INPUT_DIR.exists():
        shutil.rmtree(INPUT_DIR)
    INPUT_DIR.mkdir(parents=True)

    shutil.copy(RAW_IMAGE, INPUT_DIR / RAW_IMG_NAME)
    shutil.copy(MASK_IMAGE, INPUT_DIR / MASK_IMG_NAME)

def run_lama_direct():
    print("LaMa 직접 import 실행 중...")

    sys.argv = [
        "predict.py",
        f"model.path={MODEL_PATH}",
        f"indir={INPUT_DIR}",
        f"outdir={OUTPUT_DIR}"
    ]

    predict_path = LAMA_DIR / "bin/predict.py"
    with open(predict_path, "rb") as f:
        code = compile(f.read(), str(predict_path), "exec")
        exec(code, {"__name__": "__main__"})

    print(f"완료! 결과 저장됨: {OUTPUT_DIR / RAW_IMG_NAME}")

def main():
    prepare_input()
    run_lama_direct()

if __name__ == "__main__":
    main()
