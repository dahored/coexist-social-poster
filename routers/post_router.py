from fastapi import APIRouter
from services.post_service import PostService
from services.social.x_service import XAPI
from services.social.instagram_service import InstagramAPI
from services.social.facebook_service import FacebookAPI

router = APIRouter()
post_service = PostService()

x_api = XAPI()
instagram_api = InstagramAPI()
facebook_api = FacebookAPI()

@router.post("/run")
async def run():
    result = {}
    errors = []

    await post_service.process_posts()

    try:
        result["x"] = await x_api.run_posts()
    except Exception as e:
        result["x"] = None
        errors.append(f"X error: {str(e)}")

    try:
        result["instagram"] = await instagram_api.run_posts()
    except Exception as e:
        result["instagram"] = None
        errors.append(f"Instagram error: {str(e)}")

    try:
        result["facebook"] = await facebook_api.run_posts()
    except Exception as e:
        result["facebook"] = None
        errors.append(f"Facebook error: {str(e)}")

    return {
        "message": "Posts processed and posts published.",
        "result": result,
        "errors": errors or None
    }
