# backend/chatbot_core/logic/common.py

import re

def count_unique_furniture_mentions(conversation: str) -> int:
    furniture_keywords = [
    "침대", "책상", "의자", "옷장", "선반", "테이블", "소파",
    "러그", "조명", "커튼", "수납장", "소파", "협탁", "서랍", "거울"
]
    negative_patterns = ["없어", "필요 없어", "안 써", "제외", "빼줘", "싫어"]

    mentioned = set()

    for kw in furniture_keywords:
        # 가구 키워드가 있는 문장을 전부 탐색
        pattern = rf"[^.!?\n]*{kw}[^.!?\n]*"
        matches = re.findall(pattern, conversation)

        for sentence in matches:
            # 해당 문장에 부정 표현 포함되면 제외
            if any(neg in sentence for neg in negative_patterns):
                continue
            mentioned.add(kw)
            break  # 중복 방지

    return len(mentioned)
