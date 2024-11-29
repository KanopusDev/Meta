import pandas as pd
from typing import List, Optional
from app.api.whatsapp import WhatsAppClient
from app.models.templates import WhatsAppTemplate, TemplateMessage
from app.models.messages import ScheduledMessage
from app.core.scheduler import scheduler
from app.utils.db import save_message, get_message_history
from app.utils.phone_validator import validate_phone_number

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

    async def process_csv_recipients(self, file_path: str) -> List[str]:
        df = pd.read_csv(file_path)
        phone_column = df.columns[0]  # Assume first column contains phone numbers
        valid_numbers = []
        
        for phone in df[phone_column]:
            is_valid, formatted = validate_phone_number(str(phone))
            if is_valid:
                valid_numbers.append(formatted)
                
        return valid_numbers

    async def send_batch_template(self, batch_msg: BatchMessage):
        results = []
        for recipient in batch_msg.recipients:
            is_valid, formatted_number = validate_phone_validator(recipient)
            if not is_valid:
                results.append({"recipient": recipient, "status": "error", "message": formatted_number})
                continue

            response = await self.client.send_template_with_content(
                formatted_number,
                batch_msg.template_name,
                batch_msg.content,
                batch_msg.language_code
            )
            results.append({"recipient": recipient, "status": "success", "message_id": response.get("message_id")})
        
        return results
