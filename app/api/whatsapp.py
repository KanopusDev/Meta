import requests
from app.core.config import settings
from app.models import WhatsAppTemplate
from fastapi import APIRouter, HTTPException, Request
from app.models.messages import ScheduledMessage, MessageResponse
from app.core.scheduler import scheduler

router = APIRouter()

class WhatsAppClient:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"

    def send_message(self, to_phone: str, message: str):
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

    def send_template(self, to_phone: str, template_name: str, language_code: str = "en_US"):
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

    def create_template(self, template: WhatsAppTemplate):
        url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_BUSINESS_ID}/message_templates"
        payload = {
            "name": template.name,
            "language": template.language_code,
            "category": template.category,
            "components": [comp.dict() for comp in template.components]
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_templates(self):
        url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_BUSINESS_ID}/message_templates"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def delete_template(self, template_name: str):
        url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_BUSINESS_ID}/message_templates"
        payload = {"name": template_name}
        response = requests.delete(url, headers=self.headers, json=payload)
        return response.json()

@router.post("/webhook")
async def webhook_handler(request: Request):
    body = await request.json()
    if "messages" in body["entry"][0]["changes"][0]["value"]:
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        return MessageResponse(
            from_number=message["from"],
            message=message["text"]["body"],
            timestamp=message["timestamp"]
        )
    return {"status": "no_message"}

@router.get("/webhook")
async def verify_webhook(token: str):
    if token == settings.WEBHOOK_VERIFY_TOKEN:
        return {"challenge": token}
    raise HTTPException(status_code=403, detail="Invalid verification token")

@router.post("/schedule")
async def schedule_message(message: ScheduledMessage):
    job_id = scheduler.schedule_message(
        message.recipient,
        message.message,
        message.scheduled_time
    )
    return {"job_id": job_id}