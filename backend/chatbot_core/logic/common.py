# backend/chatbot_core/logic/common.py

furniture_keywords = [
    "침대", "책상", "의자", "옷장", "선반", "테이블", "소파",
    "러그", "조명", "커튼", "수납장", "소파", "협탁", "서랍", "거울"
]

def count_unique_furniture_mentions(text: str) -> int:
    return len({kw for kw in furniture_keywords if kw in text})
