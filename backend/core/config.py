from starlette.config import Config
from dotenv import load_dotenv
from pathlib import Path

# .env 위치를 명확히 지정
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

config = Config(".env")

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
KAKAO_REST_API_KEY = config("KAKAO_REST_API_KEY")
KAKAO_SECRET = config("KAKAO_SECRET")
NAVER_CLIENT_ID = config("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = config("NAVER_CLIENT_SECRET")
SESSION_SECRET_KEY = config("SESSION_SECRET_KEY")
SESSION_COOKIE = config("SESSION_COOKIE")
DB_URL = config("DB_URL")
REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")
SESSION_EXPIRE_SECONDS = 3600
