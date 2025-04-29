from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/me")
async def get_user(request: Request):
    return {"user": request.session.get("user")}