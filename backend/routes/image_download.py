from fastapi import APIRouter
from pydantic import BaseModel
import uuid, aiohttp, aiofiles, os

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

class DownloadRequest(BaseModel):
    image_url: str

@router.post("/download-image")
async def download_image(req: DownloadRequest):
    image_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{image_id}.jpg")
    async with aiohttp.ClientSession() as sess, sess.get(req.image_url) as r:
        async with aiofiles.open(path, "wb") as f:
            await f.write(await r.read())
    return {"image_id": image_id}
