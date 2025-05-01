# 기본적으로 남겨야 할 키워드 정의
MUST_KEEP_KEYWORDS = ["room", "floor", "wall", "door", "window"]


def normalize(label: str) -> str:
    tokens = label.lower().strip().split()
    deduped = []
    for token in tokens:
        if not deduped or token != deduped[-1]:
            deduped.append(token)
    return " ".join(deduped)


def is_must_keep(label: str) -> bool:
    return any(keyword in label for keyword in MUST_KEEP_KEYWORDS)