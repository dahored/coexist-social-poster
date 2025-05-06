import os
import requests
from dotenv import load_dotenv

class WhatsappAPI:
    def __init__(self):
        load_dotenv()
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.pin_number = os.getenv("WHATSAPP_PIN_NUMBER")
        self.api_url = os.getenv("FACEBOOK_API", "https://graph.facebook.com/v18.0")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def set_pin_phone_number(self):
        url = f"{self.api_url}/{self.phone_number_id}"
        payload = {
            "pin": self.pin_number,
        }

        response = requests.post(url, json=payload, headers=self.headers)
        data = response.json()
        if response.status_code != 200:
            print(f"❌ Error setting pin: {data}")
            return {"success": False, "error": data}
        print(f"✅ Pin set successfully: {data}")
        return {"success": True, "response": data}

    async def register_phone_number(self):
        """
        Register the phone number in WhatsApp Cloud API.
        """
        url = f"{self.api_url}/{self.phone_number_id}/register"
        payload = {
            "messaging_product": "whatsapp",
            "pin": self.pin_number
            
        }

        response = requests.post(url, json=payload, headers=self.headers)
        data = response.json()

        if response.status_code != 200:
            print(f"❌ Error registering phone number: {data}")
            return {"success": False, "error": data}

        print(f"✅ Phone number {self.phone_number_id} registered successfully.")
        return {"success": True, "response": data}


    async def get_whatsapp_data(self):
        """
        Get WhatsApp phone number info (not messages).
        """
        url = f"{self.api_url}/{self.phone_number_id}"
        params = {
            "access_token": self.access_token,
            "fields": "id,display_phone_number,verified_name"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print(f"❌ Error fetching WhatsApp data: {data}")
            return {"success": False, "error": data}

        print("✅ WhatsApp phone number data fetched successfully")
        return {"success": True, "data": data}

    async def send_message(self, to_number, message):
        """
        Send a WhatsApp text message.
        :param to_number: Recipient phone number (including country code, e.g., '573001234567')
        :param message: Message body
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(url, json=payload, headers=self.headers)
        data = response.json()

        if response.status_code != 200:
            print(f"❌ Error sending WhatsApp message: {data}")
            return {"success": False, "error": data}

        print(f"✅ WhatsApp message sent to {to_number}")
        return {"success": True, "response": data}
    
    
