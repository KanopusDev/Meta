import requests
from app.core.config import settings
from app.models.templates import WhatsAppTemplate
from circuitbreaker import circuit
from app.utils.monitoring import monitor_request

class WhatsAppClient:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"

    @circuit(failure_threshold=5, recovery_timeout=60)
    @monitor_request(counter_metric='whatsapp_requests', latency_metric='whatsapp_latency')
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

    def get_message_status(self, message_id: str):
        url = f"{self.base_url}/messages/{message_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    @circuit(failure_threshold=5, recovery_timeout=60)
    @monitor_request(counter_metric='whatsapp_requests', latency_metric='whatsapp_latency')
    def send_media(self, to_phone: str, media_url: str, media_type: str):
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": media_type,
            media_type: {"link": media_url}
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

    def mark_as_read(self, message_id: str):
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        response = requests.post(f"{self.base_url}/messages", headers=self.headers, json=payload)
        return response.json()
