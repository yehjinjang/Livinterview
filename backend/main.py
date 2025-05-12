from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import SESSION_SECRET_KEY, SESSION_COOKIE, DB_URL

from routes.google import router as google_router
from routes.kakao import router as kakao_router
from routes.naver import router as naver_router
from routes.user import router as user_router
from routes.chat import router as chat_router
from routes.image_download import router as download_router
from routes.structure_analyze import router as structure_router
from routes.data import router as data_router
from routes.create_map import router as map_router
from routes.generate import router as generate_router
from routes.cleaning import router as cleaning_router
# from routes.roomie import router as roomie_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# 세션 미들웨어
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie=SESSION_COOKIE,
)

# CORS 설정
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

# 라우터 등록
app.include_router(google_router, prefix="/auth/google", tags=["Google"])
app.include_router(kakao_router, prefix="/auth/kakao", tags=["Kakao"])
app.include_router(naver_router, prefix="/auth/naver", tags=["Naver"])
app.include_router(data_router, prefix="/data", tags=["Data"])
app.include_router(user_router, tags=["User"])
app.include_router(chat_router, tags=["Chat"])
app.include_router(download_router, prefix="/vision")
app.include_router(structure_router, prefix="/vision")
app.include_router(generate_router, tags=["Generate"])
app.include_router(map_router, tags=["Map"])
app.include_router(cleaning_router, prefix="/cleaning", tags=["Cleaning"])
# app.include_router(roomie_router, prefix="/api", tags=["Roomie"])

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="data"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

# DB URL 마스킹 출력
safe_db_url = DB_URL.replace(DB_URL.split(":")[2].split("@")[0], "****")
print(f"🟢 DB 연결 확인: {safe_db_url}")
