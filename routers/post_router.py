from fastapi import APIRouter
from services.post_service import PostService
from services.social.x_service import XAPI
from services.social.instagram_service import InstagramAPI
from services.social.facebook_service import FacebookAPI
from services.social.telegram_service import TelegramAPI
from utils.file_utils import FileHandler

router = APIRouter()
post_service = PostService()

x_api = XAPI()
instagram_api = InstagramAPI()
facebook_api = FacebookAPI()
telegram_api = TelegramAPI()

file_handler = FileHandler()

@router.post("/run")
async def run():
    result = {}
    errors = []

    await post_service.process_posts()

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

    all_ok = x_ok and instagram_ok and facebook_ok

    if all_ok:
        await file_handler.clean_uploaded_files()

    message = "✅ Posts processed and published successfully."
    if errors:
        message = "⚠️ Posts processed, but there were errors."

    response = {
        "message": message,
        "result": result,
        "errors": errors or None,
        "all_ok": all_ok,
        "social_ok": {
            "x": x_ok,
            "instagram": instagram_ok,
            "facebook": facebook_ok
        }
    }

    error_text = 'No errors.' if not errors else 'Errors:\n- ' + '\n- '.join(errors)
    telegram_message = (
        f"📢 Posting Summary:\n"
        f"✅ X: {'OK' if x_ok else '❌ ERROR'}\n"
        f"✅ Instagram: {'OK' if instagram_ok else '❌ ERROR'}\n"
        f"✅ Facebook: {'OK' if facebook_ok else '❌ ERROR'}\n"
        "\n"
        f"{error_text}"
    )

    # Send to Telegram
    await telegram_api.send_message(telegram_message.strip())

    return response
