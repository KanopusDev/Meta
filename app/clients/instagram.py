
import requests
from app.core.config import settings

class InstagramClient:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v21.0/{settings.INSTAGRAM_ACCOUNT_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.INSTAGRAM_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

    def send_message(self, recipient_id: str, message: str):
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message}
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

    def send_media(self, recipient_id: str, media_url: str, media_type: str):
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": media_type,
                    "payload": {"url": media_url}
                }
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()