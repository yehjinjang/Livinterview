from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/me")
async def get_user(request: Request):
    raw_user = request.session.get("user")
    if not raw_user:
        return JSONResponse(status_code=401, content={"detail": "Not logged in"})

    # provider별 데이터 정리
    email = None
    name = None

    if "email" in raw_user and "name" in raw_user:
        # Google
        email = raw_user["email"]
        name = raw_user["name"]

    elif "kakao_account" in raw_user:
        # Kakao
        account = raw_user["kakao_account"]
        email = account.get("email")
        name = account.get("profile", {}).get("nickname")

    elif "email" in raw_user and "mobile" in raw_user:
        # Naver
        email = raw_user.get("email")
        name = raw_user.get("name")

    return {
        "email": email,
        "name": name
    }
