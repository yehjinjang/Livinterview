from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from core.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
import httpx, logging
import os
os.environ.pop("SSL_CERT_FILE", None)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
async def login_naver(request: Request):
    redirect_uri = request.url_for("auth_naver_callback")
    state = "randomstate123"
    return RedirectResponse(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={NAVER_CLIENT_ID}&redirect_uri={redirect_uri}&state={state}"
    )

@router.get("/callback")
async def auth_naver_callback(request: Request):
    try:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        redirect_uri = request.url_for("auth_naver_callback")
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
            return RedirectResponse("http://localhost:5173/survey")
    except Exception as e:
        logger.error(f"Naver Login Error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Naver login failed"})
