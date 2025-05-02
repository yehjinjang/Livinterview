from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("")
async def login_google(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    # print(" Google Login URL 생성")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_google_callback(request: Request):
    try:
        # print("Google 콜백 호출됨")
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        user = {
            'email':user.get('email'),
            'name':user.get('name')
        }
        # print("User Info:", user)
        request.session['user'] = user
        # print(request.session.get('user'))
        return RedirectResponse("http://localhost:5173/roomie")
    except Exception as e:
        logger.error(f"Google Login Error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Google login failed"})