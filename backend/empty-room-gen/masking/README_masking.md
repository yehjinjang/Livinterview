# 🧹 Object Masking for Empty Room Generation

이 프로젝트는 GroundingDINO, Tag2Text (RAM), Segment Anything (SAM)을 활용하여  
방 사진에서 **남기고 싶은 객체만 고르면**, 나머지 객체를 자동으로 제거하는 마스크를 생성하는 파이프라인입니다.

---

## 📁 폴더 구조

```
masking/
├── main.py                # 실행 진입점 (CLI)
├── run.py                 # create_removal_mask 함수 정의
├── modules/               # 주요 기능 모듈
│   ├── loader.py
│   ├── predictor.py
│   ├── mask_handler.py
│   └── utils.py
├── Tag2Text/              # 직접 복사한 Tag2Text 코드
├── requirements.txt       # 실행을 위한 패키지 목록
└── README.md              # 설명 문서
```

---

## 🚀 설치 및 실행 방법

### 1. 가상환경 생성 및 라이브러리 설치

```bash
python -m venv env
source env/bin/activate          # Windows: .\env\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 사전 학습 모델 다운로드

```bash
mkdir -p checkpoints

# GroundingDINO
wget -P checkpoints https://github.com/IDEA-Research/GroundingDINO/releases/download/0.1/groundingdino_swint_ogc.pth
wget -P checkpoints https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py

# Segment Anything (SAM)
wget -P checkpoints https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# Tag2Text (RAM)
wget -P checkpoints https://huggingface.co/spaces/xinyu1205/Recognize_Anything-Tag2Text/resolve/main/tag2text_swin_14m.pth
```

> 또는 수동으로 다운로드 후 `checkpoints/` 폴더에 넣어도 됩니다.

---

### 3. CLI 테스트 실행 예시

```bash
python main.py \
  --config checkpoints/GroundingDINO_SwinT_OGC.py \
  --ram_checkpoint checkpoints/tag2text_swin_14m.pth \
  --grounded_checkpoint checkpoints/groundingdino_swint_ogc.pth \
  --sam_checkpoint checkpoints/sam_vit_h_4b8939.pth \
  --input_image path/to/image.jpg \
  --output_dir outputs \
  --device cuda
```

---

## 🧠 결과 설명

- `outputs/raw_image.jpg` : 입력 이미지 저장본  
- `outputs/mask_*.png` : 제거 대상별 마스크  
- `outputs/merged_mask.png` : 병합된 최종 마스크

---

## 📌 참고사항

- Tag2Text는 pip으로 설치되지 않으므로, `Tag2Text/` 폴더로 직접 복사한 코드가 필요합니다.
- PyTorch는 CUDA 환경에 따라 설치 버전이 달라질 수 있습니다. [공식 가이드 참고](https://pytorch.org/get-started/locally/)
- 본 프로젝트는 마스킹만 수행합니다. 인페인팅은 [IOPaint](https://github.com/Sanster/IOPaint) 또는 [LaMa](https://github.com/saic-mdal/lama)를 활용하세요.

---
