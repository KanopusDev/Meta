from fastapi import APIRouter, HTTPException
from app.models.templates import WhatsAppTemplate, TemplateMessage
from app.api.whatsapp import WhatsAppClient
from app.core.scheduler import scheduler
from typing import List

router = APIRouter()
whatsapp_client = WhatsAppClient()

@router.post("/create")
async def create_template(template: WhatsAppTemplate):
    """Create a new WhatsApp message template"""
    response = whatsapp_client.create_template(template)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response

@router.get("/list")
async def list_templates() -> List[dict]:
    """Get all available templates"""
    response = whatsapp_client.get_templates()
    return response.get("data", [])

@router.delete("/{template_name}")
async def delete_template(template_name: str):
    """Delete a template"""
    response = whatsapp_client.delete_template(template_name)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return {"message": f"Template {template_name} deleted successfully"}

@router.post("/send")
async def send_template_message(message: TemplateMessage):
    """Send a template message"""
    response = whatsapp_client.send_template(
        message.recipient,
        message.template_name,
        message.language_code
    )
    return response
