from fastapi import APIRouter
from services.social.whatsapp_service import WhatsappAPI

router = APIRouter()
api = WhatsappAPI()

@router.get("/ping")
async def ping():
    return {"message": "Whatsapp module is up and running!"}

@router.get("/test")
async def test():
    return await api.get_whatsapp_data()

@router.post("/set-pin")
async def set_pin():
    response = await api.set_pin_phone_number()
    return response

@router.post("/register")
async def register():
    response = await api.register_phone_number()
    return response

@router.post("/send")
async def send_message(to_number: str, message: str):
    response = await api.send_message(to_number, message)
    return response


