🖌️ Inpainting for Empty Room Completion

이 모듈은 Stable Diffusion 기반의 인페인팅 기능을 통해, 마스킹된 방 사진을 완전한 빈 방 이미지로 생성합니다.
masking/ 모듈과 연동되어, 남기고 싶은 객체만 마스크로 남기고 나머지는 자연스럽게 제거된 이미지를 생성할 수 있습니다.

📁 폴더 구조

inpaint/
├── run_sd_inpaint.py       # Stable Diffusion 기반 인페인팅 실행 스크립트
├── merged_mask.png         # masking 결과로 생성된 마스크 파일 (예시)
├── test.png                # 원본 테스트 이미지 (예시)
├── sd_inpainted_room.png   # 생성된 빈 방 이미지 결과

테스트 이미지와 마스크는 예시용이며, 직접 실행 시 masking 모듈 결과를 사용하세요.

🚀 설치 및 실행 방법

1. 사전 준비

masking 모듈을 먼저 실행해 merged_mask.png 파일을 생성해야 합니다.

Python 환경이 준비되어 있어야 하며, diffusers, transformers, torch 등이 설치되어 있어야 합니다.

pip install diffusers transformers accelerate torch

2. 인페인팅 실행

python run_sd_inpaint.py

스크립트는 inpaint/test.jpg와 inpaint/merged_mask.png 파일을 불러와 처리합니다.
출력은 inpaint/sd_inpainted_room.png로 저장됩니다.

✏️ 프롬프트 설명

Positive Prompt:

a completely empty room. minimalist. clean. nothing inside.

Negative Prompt:

furniture, objects, table, chairs, decoration, plant, curtain, shelf, carpet, lighting fixture, window, artwork, clutter

위의 프롬프트를 기반으로, Stable Diffusion 모델이 남은 공간을 자연스럽게 재구성합니다.

📌 참고사항

사용 모델: stabilityai/stable-diffusion-2-inpainting

해상도는 자동으로 512x512로 조정되며, 결과는 원래 이미지 크기로 다시 리사이즈됩니다.

마스크는 RGB 형식이어야 하며, 흰색(255,255,255)이 인페인팅 대상입니다.

📷 테스트 이미지 관리

테스트 이미지는 Git에는 포함되어 있지 않으며, .gitignore에 의해 제외되어 있습니다.

직접 실행을 위해서는 test.png 및 merged_mask.png 파일을 준비해 inpaint/ 폴더에 넣어야 합니다.

