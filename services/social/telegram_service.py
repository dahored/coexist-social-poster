import os
import requests
from dotenv import load_dotenv

class TelegramAPI:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = os.getenv("TELEGRAM_API")

    async def get_chat_id(self):
        url = f"{self.api_url}{self.bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200 or not data.get("ok"):
            print(f"❌ Error fetching Telegram chat ID: {data}")
            return {"success": False, "error": data}
        if data["result"]:
            chat_id = data["result"][0]["message"]["chat"]["id"]
            print(f"✅ Telegram chat ID: {chat_id}")
            return {"success": True, "chat_id": chat_id}
        else:
            print("❌ No chat ID found in Telegram updates.")
            return {"success": False, "error": "No chat ID found"}

    async def send_message(self, message):
        url = f"{self.api_url}{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }
        print(f"📩 Sending message to Telegram: {payload}")
        response = requests.post(url, data=payload)
        data = response.json()

        if response.status_code != 200 or not data.get("ok"):
            print(f"❌ Error sending Telegram message: {data}")
            return {"success": False, "error": data}

        print(f"✅ Telegram message sent to {self.chat_id}")
        return {"success": True, "response": data}

    
