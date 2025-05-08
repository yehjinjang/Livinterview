from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import SESSION_SECRET_KEY, SESSION_COOKIE
from routes.google import router as google_router
from routes.kakao import router as kakao_router
from routes.naver import router as naver_router
from routes.user import router as user_router
from routes.chat import router as chat_router
from routes.vision_analyze import router as vision_router
from routes.generate import router as generate_router
from routes.cleaning import router as cleaning_router
from routes.data import router as data_router 

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie=SESSION_COOKIE,
)

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

app.include_router(google_router, prefix="/auth/google", tags=["Google"])
app.include_router(kakao_router, prefix="/auth/kakao", tags=["Kakao"])
app.include_router(naver_router, prefix="/auth/naver", tags=["Naver"])
app.include_router(data_router, prefix="/data", tags=["Data"])
app.include_router(user_router, tags=["User"])
app.include_router(chat_router, tags=["Chat"])
app.include_router(vision_router, prefix="/vision", tags=["VisionAnalyze"])
app.include_router(generate_router, tags=["Generate"])
app.include_router(cleaning_router, prefix="/cleaning", tags=["Cleaning"])

# 정적 파일 서빙 경로 추가
app.mount("/static", StaticFiles(directory="data"), name="static")

# from routes.roomie import router as roomie_router
