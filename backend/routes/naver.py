from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
import httpx, logging, os

os.environ.pop("SSL_CERT_FILE", None)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def login_naver(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/naver/callback"
    state = "randomstate123"

    login_url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?response_type=code"
        f"&client_id={NAVER_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )

    print("🔗 Naver login URL:", login_url)
    return RedirectResponse(login_url)

@router.get("/callback", name="auth_naver_callback")
async def auth_naver_callback(request: Request):
    # print("----- 콜백 함수 호출됨!!!!------")  
    try:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        print("Code:", code)
        print("State:", state)

        redirect_uri = "http://127.0.0.1:8000/auth/naver/callback"
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://nid.naver.com/oauth2.0/token",
                params={
                    "grant_type": "authorization_code",
                    "client_id": NAVER_CLIENT_ID,
                    "client_secret": NAVER_CLIENT_SECRET,
                    "code": code,
                    "state": state
                }
            )

            token = token_res.json()
            access_token = token["access_token"]
            user_res = await client.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user = user_res.json()["response"]
            request.session['user'] = user
            # print("네이버 사용자 정보:", user)

            return RedirectResponse("http://localhost:5173/roomie")
    except Exception as e:
        logger.error(f"Naver Login Error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Naver login failed"})
