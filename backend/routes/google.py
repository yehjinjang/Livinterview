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
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        request.session['user'] = user
        return RedirectResponse("http://localhost:5173/survey")
    except Exception as e:
        logger.error(f"Google Login Error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Google login failed"})

