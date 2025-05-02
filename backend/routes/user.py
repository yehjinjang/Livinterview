from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from database import get_db
from models import User, StateEnum
from core.config import SESSION_COOKIE
from redis_connect import get_session, destroy_session

router = APIRouter()


@router.get("/me")
def get_user(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    print(session_id)
    if not session_id:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    raw_user = get_session(session_id)
    if not raw_user:
        return JSONResponse(
            status_code=401, content={"detail": "Session expired or invalid"}
        )

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
    if not email:
        return JSONResponse(status_code=400, content={"detail": "Email not found"})

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    if user.state == StateEnum.inactive:
        user.state = StateEnum.active
        db.commit()

    return {"email": email, "name": name}


@router.post("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        destroy_session(session_id)
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_id")
    return response


@router.post("/unregister")
def unregister(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    session_id = request.cookies.get("session_id")
    if session_id:
        raw_user = get_session(session_id)
        email = raw_user.get("email")
        destroy_session(session_id)
        db.query(User).filter(User.email == email).update({User.state: "inactive"})
        db.commit()
    response.delete_cookie("session_id")
    return {"message": "Logged out"}
