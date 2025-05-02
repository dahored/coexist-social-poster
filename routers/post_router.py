from fastapi import APIRouter
from services.post_service import PostService
from services.social.x_service import XAPI

router = APIRouter()
post_service = PostService()
x_api = XAPI()

@router.post("/run")
async def run():
    await post_service.process_posts()
    await x_api.run_posts()
    return {"message": "Posts processed and posts published successfully."}
