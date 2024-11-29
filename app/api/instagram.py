import requests
from app.core.config import settings
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.core.scheduler import scheduler
from app.clients.instagram import InstagramClient

router = APIRouter()
instagram_client = InstagramClient()

class InstagramMessage(BaseModel):
    recipient_id: str
    message: str
    scheduled_time: datetime = None

class MediaMessage(BaseModel):
    recipient_id: str
    media_url: str
    media_type: str  # image, video
    scheduled_time: datetime = None

@router.post("/send")
async def send_instagram_message(message: InstagramMessage):
    if message.scheduled_time:
        job_id = scheduler.schedule_instagram_message(
            message.recipient_id,
            message.message,
            message.scheduled_time
        )
        return {"job_id": job_id}
    
    response = instagram_client.send_message(
        message.recipient_id,
        message.message
    )
    return response

@router.post("/send-media")
async def send_instagram_media(message: MediaMessage):
    if message.scheduled_time:
        job_id = scheduler.schedule_instagram_media(
            message.recipient_id,
            message.media_url,
            message.media_type,
            message.scheduled_time
        )
        return {"job_id": job_id}
    
    response = instagram_client.send_media(
        message.recipient_id,
        message.media_url,
        message.media_type
    )
    return response