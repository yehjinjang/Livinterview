from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import KAKAO_REST_API_KEY, KAKAO_SECRET
import httpx, logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def login_kakao(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/kakao/callback"
    login_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"response_type=code&client_id={KAKAO_REST_API_KEY}&redirect_uri={redirect_uri}"
    )
    print("🔗 Kakao login URL:", login_url)
    return RedirectResponse(login_url)

@router.get("/callback")
async def auth_kakao_callback(request: Request):
    # print("---- Kakao 콜백 호출됨----- ")
    try:
        code = request.query_params.get("code")
        print("Code:", code)
        redirect_uri = "http://127.0.0.1:8000/auth/kakao/callback"
        
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": KAKAO_REST_API_KEY,
                    "redirect_uri": redirect_uri,
                    "code": code,
                    "client_secret": KAKAO_SECRET
                }
            )
            token = token_res.json()
            access_token = token["access_token"]
            print("Access Token:", access_token)

            user_res = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user = user_res.json()
            # print("Kakao 사용자 정보:", user)
            request.session['user'] = user

            return RedirectResponse("http://localhost:5173/survey")

    except Exception as e:
        logger.error(f"Kakao Login Error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Kakao login failed"})
