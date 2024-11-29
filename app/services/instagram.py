from typing import Optional
from app.api.instagram import InstagramClient
from app.utils.db import save_message
from app.core.scheduler import scheduler
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class InstagramService:
    def __init__(self):
        self.client = InstagramClient()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_message(self, recipient_id: str, message: str) -> dict:
        try:
            response = self.client.send_message(recipient_id, message)
            if "error" in response:
                logger.error(f"Instagram API error: {response['error']}")
                raise Exception(response['error'])
            
            await save_message({
                "recipient": recipient_id,
                "message": message,
                "platform": "instagram"
            }, response.get("message_id"))
            
            return response
        except Exception as e:
            logger.error(f"Failed to send Instagram message: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_media(self, recipient_id: str, media_url: str, media_type: str) -> dict:
        try:
            response = self.client.send_media(recipient_id, media_url, media_type)
            if "error" in response:
                logger.error(f"Instagram API error: {response['error']}")
                raise Exception(response['error'])
            
            await save_message({
                "recipient": recipient_id,
                "media_url": media_url,
                "media_type": media_type,
                "platform": "instagram"
            }, response.get("message_id"))
            
            return response
        except Exception as e:
            logger.error(f"Failed to send Instagram media: {e}")
            raise

    async def schedule_message(self, recipient_id: str, message: str, scheduled_time) -> str:
        try:
            job_id = scheduler.schedule_instagram_message(
                recipient_id,
                message,
                scheduled_time
            )
            await save_message({
                "recipient": recipient_id,
                "message": message,
                "scheduled_time": scheduled_time,
                "platform": "instagram"
            }, job_id)
            return job_id
        except Exception as e:
            logger.error(f"Failed to schedule Instagram message: {e}")
            raise
