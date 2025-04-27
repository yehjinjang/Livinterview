from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from core.config import SESSION_SECRET_KEY
from routes.google import router as google_router
from routes.kakao import router as kakao_router
from routes.naver import router as naver_router
from routes.user import router as user_router
from routes.chat import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

app.include_router(google_router, prefix="/auth/google", tags=["Google"])
app.include_router(kakao_router, prefix="/auth/kakao", tags=["Kakao"])
app.include_router(naver_router, prefix="/auth/naver", tags=["Naver"])
app.include_router(user_router, tags=["User"])
app.include_router(chat_router,  tags=["Chat"])

