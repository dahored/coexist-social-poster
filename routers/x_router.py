from fastapi import APIRouter
from services.x_service import XAPI

router = APIRouter()
x_api = XAPI()

@router.get("/ping")
async def ping():
    return {"message": "X module is up and running!"}

@router.post("/post")
async def post_single():
    return await x_api.run_posts()
