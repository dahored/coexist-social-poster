from fastapi import APIRouter
from services.social.telegram_service import TelegramAPI

router = APIRouter()
api = TelegramAPI()

@router.get("/ping")
async def ping():
    return {"message": "Telegram module is up and running!"}

@router.get("/get-chat-id")
async def get_chat_id():
    response = await api.get_chat_id()
    return response

@router.post("/send")
async def send_message(message: str):
    response = await api.send_message(message)
    return response


