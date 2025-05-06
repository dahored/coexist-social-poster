from fastapi import APIRouter
from services.post_service import PostService
from services.social.x_service import XAPI
from services.social.instagram_service import InstagramAPI
from services.social.facebook_service import FacebookAPI
from utils.file_utils import FileHandler

router = APIRouter()
post_service = PostService()

x_api = XAPI()
instagram_api = InstagramAPI()
facebook_api = FacebookAPI()

file_handler = FileHandler()

@router.post("/run")
async def run():
    result = {}
    errors = []

    await post_service.process_posts()

    # Bandera para rastrear el éxito de cada red
    x_ok = instagram_ok = facebook_ok = True

    try:
        result["x"] = await x_api.run_posts()
    except Exception as e:
        result["x"] = None
        errors.append(f"X error: {str(e)}")
        x_ok = False

    try:
        result["instagram"] = await instagram_api.run_posts()
    except Exception as e:
        result["instagram"] = None
        errors.append(f"Instagram error: {str(e)}")
        instagram_ok = False

    try:
        result["facebook"] = await facebook_api.run_posts()
    except Exception as e:
        result["facebook"] = None
        errors.append(f"Facebook error: {str(e)}")
        facebook_ok = False

    # Determinar si todo estuvo OK
    all_ok = x_ok and instagram_ok and facebook_ok

    if all_ok:
        await file_handler.clean_uploaded_files()

    response = {
        "message": "Posts processed and posts published.",
        "result": result,
        "errors": errors or None,
        "all_ok": all_ok,
        "social_ok": {
            "x": x_ok,
            "instagram": instagram_ok,
            "facebook": facebook_ok
        }
    }

    return response
