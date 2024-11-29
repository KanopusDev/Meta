import requests
from app.core.config import settings
from app.models.templates import WhatsAppTemplate, TemplateMessage
from fastapi import APIRouter, HTTPException, Request
from app.models.messages import ScheduledMessage, MessageResponse
from app.core.scheduler import scheduler
from app.clients.whatsapp import WhatsAppClient
from circuitbreaker import circuit
from fastapi import UploadFile, File
import tempfile
import os

router = APIRouter()
whatsapp_client = WhatsAppClient()

class WhatsAppClient:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"

    @circuit(failure_threshold=5, recovery_timeout=60)
    async def send_message(self, to_phone: str, message: str):
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

@router.post("/send")
async def send_message(message: ScheduledMessage):
    response = await whatsapp_client.send_message(
        message.recipient,
        message.message
    )
    return response

@router.post("/create")
async def create_template(template: WhatsAppTemplate):
    response = whatsapp_client.create_template(template)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response

@router.get("/list")
async def list_templates():
    response = whatsapp_client.get_templates()
    return response.get("data", [])

@router.delete("/{template_name}")
async def delete_template(template_name: str):
    response = whatsapp_client.delete_template(template_name)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": f"Template {template_name} deleted successfully"}

@router.post("/send_template")
async def send_template_message(message: TemplateMessage):
    response = whatsapp_client.send_template(
        message.recipient,
        message.template_name,
        message.language_code
    )
    return response

@router.post("/send_scheduled")
async def send_scheduled_message(message: ScheduledMessage):
    job_id = scheduler.schedule_message(
        message.recipient,
        message.message,
        message.scheduled_time
    )
    return {"job_id": job_id}

@router.post("/batch/template")
async def send_batch_template(batch_msg: BatchMessage):
    """Send template message to multiple recipients"""
    whatsapp_service = WhatsAppService()
    results = await whatsapp_service.send_batch_template(batch_msg)
    return {"results": results}

@router.post("/batch/from-csv")
async def send_batch_from_csv(
    template_name: str,
    file: UploadFile = File(...),
    language_code: str = "en"
):
    """Send template message to recipients from CSV file"""
    whatsapp_service = WhatsAppService()
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_path = temp_file.name

    try:
        recipients = await whatsapp_service.process_csv_recipients(temp_path)
        batch_msg = BatchMessage(
            template_name=template_name,
            language_code=language_code,
            recipients=recipients
        )
        results = await whatsapp_service.send_batch_template(batch_msg)
        return {"results": results}
    finally:
        os.unlink(temp_path)  # Clean up temp file

