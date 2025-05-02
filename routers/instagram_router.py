from fastapi import APIRouter
from services.social.instagram_service import InstagramAPI

router = APIRouter()
instagram_api = InstagramAPI()

@router.get("/ping")
async def ping():
    return {"message": "Instagram module is up and running!"}

@router.post("/test")
async def test():
    return await instagram_api.get_user_data()

@router.post("/post")
async def run_posts():
    return await instagram_api.run_posts()
