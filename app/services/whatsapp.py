from typing import List, Optional
from app.api.whatsapp import WhatsAppClient
from app.models.templates import WhatsAppTemplate, TemplateMessage
from app.models.messages import ScheduledMessage
from app.core.scheduler import scheduler
from app.utils.db import save_message, get_message_history

class WhatsAppService:
    def __init__(self):
        self.client = WhatsAppClient()

    async def send_scheduled_message(self, message: ScheduledMessage):
        job_id = scheduler.schedule_message(
            message.recipient,
            message.message,
            message.scheduled_time
        )
        await save_message(message, job_id)
        return job_id

    async def send_template_message(self, template_msg: TemplateMessage):
        response = self.client.send_template(
            template_msg.recipient,
            template_msg.template_name,
            template_msg.language_code
        )
        await save_message(template_msg, response.get("message_id"))
        return response

    async def get_chat_history(self, phone_number: str) -> List[dict]:
        return await get_message_history(phone_number)
