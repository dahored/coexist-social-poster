from fastapi import APIRouter
from services.social.facebook_service import FacebookAPI

router = APIRouter()
api = FacebookAPI()

@router.get("/ping")
async def ping():
    return {"message": "Facebook module is up and running!"}

@router.post("/test")
async def test():
    return await api.get_user_data()

@router.post("/get-page-token")
async def get_page_token():
    return await api.get_page_access_token()

@router.post("/post")
async def run_posts():
    return await api.run_posts()
