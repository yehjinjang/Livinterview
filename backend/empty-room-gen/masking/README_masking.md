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
│   ├── models/
│   │   └── tag2text.py
│   ├── inference_ram.py
│   └── __init__.py
├── requirements.txt       # 실행을 위한 패키지 목록
├── README.md              # 설명 문서
├── checkpoints/           # 사전학습 모델 넣는 폴더 (수동 생성 필요)
└── outputs/               # 마스크 결과 저장 폴더 (자동 생성됨)
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

> `--input_image`는 main.py 실행 위치를 기준으로 경로를 지정해야 합니다.  
> 예를 들어 `masking/test.jpg`에 이미지가 있다면 `--input_image test.jpg`로 지정하세요.

---

## 🧠 결과 설명

- `outputs/`: 마스크 이미지가 저장되는 폴더로, **실행 시 자동 생성**됩니다.
- `checkpoints/`: 사전 학습 모델을 수동으로 넣어야 하며, **직접 폴더를 만들어야 합니다.**

---

## 📌 참고사항

- Tag2Text는 pip으로 설치할 수 없으며, 아래와 같이 필요한 파일만 `Tag2Text/` 폴더에 직접 복사해 사용합니다.

```
Tag2Text/
├── models/
│   └── tag2text.py        # ram() 함수 포함
├── inference_ram.py       # 태깅 추론용
└── __init__.py            # 비어 있어도 괜찮음
```

- `ram.py`는 `tag2text.py` 안에 ram() 함수가 포함된 구조라면 필요하지 않습니다.
- PyTorch는 CUDA 환경에 따라 설치 버전이 달라질 수 있습니다. [공식 가이드 참고](https://pytorch.org/get-started/locally/)
- 마스킹 후에는 같은 프로젝트의 `inpaint/` 폴더 내 인페인팅 모듈과 연동되어,  
  빈 방 이미지를 완성하는 통합 파이프라인으로 확장될 예정입니다.

---
