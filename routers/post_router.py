from fastapi import APIRouter
from services.post_service import PostService
from services.x_service import XAPI

router = APIRouter()
post_service = PostService()
x_api = XAPI()

@router.post("/process")
async def process_posts():
    await post_service.process_posts()
    return await x_api.run_posts()
