from fastapi import APIRouter
from services.social.x_service import XAPI

router = APIRouter()
api = XAPI()

@router.get("/ping")
async def ping():
    return {"message": "X module is up and running!"}

@router.get("/get-rate-limit")
async def get_rate_limit():
    return api.get_rate_limit_status()

@router.post("/post")
async def run_posts():
    return await api.run_posts()
