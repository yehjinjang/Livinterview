# 🖌️ Inpainting for Empty Room Completion

이 모듈은 Stable Diffusion 기반의 인페인팅 기능을 통해, 마스킹된 방 사진을 완전한 **빈 방 이미지**로 생성합니다.  
`masking/` 모듈과 연동되어, **남기고 싶은 객체만 선택하고 나머지는 자연스럽게 제거된 이미지**를 만들 수 있습니다.

---

## 📁 폴더 구조

```
inpaint/
├── run_sd_inpaint.py        # Stable Diffusion 기반 인페인팅 실행 스크립트
├── merged_mask.png          # masking 결과로 생성된 마스크 파일 (예시)
├── test.png                 # 원본 테스트 이미지 (예시)
└── sd_inpainted_room.png    # 생성된 빈 방 이미지 결과
```

> 테스트 이미지와 마스크는 예시용이며, 실제 실행 시 masking 모듈의 결과를 사용하는 것을 권장합니다.

---

## 🚀 설치 및 실행 방법

### 1. 사전 준비

- `masking` 모듈을 먼저 실행하여 `merged_mask.png` 파일을 생성하세요.
- Python 환경에서 다음 라이브러리를 설치해야 합니다:

```bash
pip install diffusers transformers accelerate torch
```

---

### 2. 인페인팅 실행

```bash
python run_sd_inpaint.py
```

- 입력: `inpaint/test.png`, `inpaint/merged_mask.png`
- 출력: `inpaint/sd_inpainted_room.png`

이미지와 마스크는 512x512로 자동 리사이즈되며, 인페인팅 결과는 원본 크기로 복원됩니다.

---

## ✏️ 프롬프트 설명

- **Positive Prompt:**
  ```
  a completely empty room. minimalist. clean. nothing inside.
  ```

- **Negative Prompt:**
  ```
  furniture, objects, table, chairs, decoration, plant, curtain, shelf, carpet, lighting fixture, window, artwork, clutter
  ```

Stable Diffusion 모델은 위의 프롬프트를 기반으로, 가구가 제거된 공간을 자연스럽게 재구성합니다.

---

## 📌 참고사항

- 사용 모델: `stabilityai/stable-diffusion-2-inpainting`
- 마스크는 **RGB 형식**이어야 하며, **흰색(255, 255, 255)** 영역이 인페인팅 대상입니다.
- 입력 이미지는 SD 2.x 권장 해상도인 512x512로 처리되며, 결과는 다시 원본 해상도로 복원됩니다.

---

## 📷 테스트 이미지 관리

- 테스트 이미지는 Git에 포함되어 있지 않으며, `.gitignore`에 의해 무시됩니다.
- 실행을 위해서는 `test.png`, `merged_mask.png` 파일을 직접 `inpaint/` 폴더에 넣어야 합니다.
