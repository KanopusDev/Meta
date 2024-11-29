from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
import uvicorn
from config import settings
from whatsapp_client import WhatsAppClient
from scheduler import MessageScheduler
from models import WhatsAppTemplate
from instagram_client import InstagramClient
from models import InstagramMessageRequest, InstagramMediaRequest

app = FastAPI()
whatsapp = WhatsAppClient()
scheduler = MessageScheduler()
instagram = InstagramClient()

# Store conversation history
conversations: Dict[str, list] = {}

class MessageRequest(BaseModel):
    phone: str
    message: str
    schedule_time: datetime = None

class TemplateRequest(BaseModel):
    phone: str
    template_name: str
    language_code: str = "en_US"

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.VERIFY_TOKEN:
            return int(challenge)
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    
    try:
        # Extract message data from webhook
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_number = message['from']
        message_body = message['text']['body']
        
        # Store in conversations
        if from_number not in conversations:
            conversations[from_number] = []
        conversations[from_number].append({
            "from": "user",
            "message": message_body,
            "timestamp": datetime.now()
        })
        
        return {"status": "success"}
    except:
        return {"status": "error", "message": "Invalid webhook payload"}

@app.post("/send")
async def send_message(message_request: MessageRequest):
    if message_request.schedule_time:
        job_id = scheduler.schedule_message(
            message_request.phone,
            message_request.message,
            message_request.schedule_time
        )
        return {"status": "scheduled", "job_id": job_id}
    else:
        response = whatsapp.send_message(message_request.phone, message_request.message)
        
        # Store in conversations
        if message_request.phone not in conversations:
            conversations[message_request.phone] = []
        conversations[message_request.phone].append({
            "from": "admin",
            "message": message_request.message,
            "timestamp": datetime.now()
        })
        
        return response

@app.post("/send-template")
async def send_template(template_request: TemplateRequest):
    response = whatsapp.send_template(
        template_request.phone,
        template_request.template_name,
        template_request.language_code
    )
    
    # Store in conversations
    if template_request.phone not in conversations:
        conversations[template_request.phone] = []
    conversations[template_request.phone].append({
        "from": "admin",
        "message": f"Template: {template_request.template_name}",
        "timestamp": datetime.now()
    })
    
    return response

@app.post("/templates")
async def create_template(template: WhatsAppTemplate):
    """Create a new WhatsApp template"""
    response = whatsapp.create_template(template)
    return response

@app.get("/templates")
async def list_templates():
    """Get all available templates"""
    return whatsapp.get_templates()

@app.delete("/templates/{template_name}")
async def delete_template(template_name: str):
    """Delete a template"""
    return whatsapp.delete_template(template_name)

@app.post("/schedule-template")
async def schedule_template(template_request: TemplateRequest, schedule_time: datetime):
    """Schedule a template message"""
    job_id = scheduler.schedule_template(
        template_request.phone,
        template_request.template_name,
        template_request.language_code,
        schedule_time
    )
    return {"status": "scheduled", "job_id": job_id}

@app.get("/conversations/{phone}")
async def get_conversation(phone: str):
    return conversations.get(phone, [])

@app.post("/instagram/send")
async def send_instagram_message(message_request: InstagramMessageRequest):
    if message_request.schedule_time:
        job_id = scheduler.schedule_instagram_message(
            message_request.recipient_id,
            message_request.message,
            message_request.schedule_time
        )
        return {"status": "scheduled", "job_id": job_id}
    else:
        response = instagram.send_message(
            message_request.recipient_id,
            message_request.message
        )
        
        # Store in conversations
        if message_request.recipient_id not in conversations:
            conversations[message_request.recipient_id] = []
        conversations[message_request.recipient_id].append({
            "from": "admin",
            "message": message_request.message,
            "platform": "instagram",
            "timestamp": datetime.now()
        })
        
        return response

@app.post("/instagram/send-media")
async def send_instagram_media(media_request: InstagramMediaRequest):
    if media_request.schedule_time:
        job_id = scheduler.schedule_instagram_media(
            media_request.recipient_id,
            media_request.media_url,
            media_request.media_type,
            media_request.schedule_time
        )
        return {"status": "scheduled", "job_id": job_id}
    else:
        response = instagram.send_media(
            media_request.recipient_id,
            media_request.media_url,
            media_request.media_type
        )
        return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)