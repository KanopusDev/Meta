from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class TemplateComponent(BaseModel):
    type: str  # HEADER, BODY, FOOTER, BUTTONS
    text: Optional[str]
    format: Optional[str] = "text"  # text, image, video, document
    buttons: Optional[List[Dict]] = None

class WhatsAppTemplate(BaseModel):
    name: str
    language_code: str = "en_US"
    category: str = "MARKETING"
    components: List[TemplateComponent]

class InstagramMessageRequest(BaseModel):
    recipient_id: str
    message: str
    platform: str = "instagram"
    schedule_time: Optional[datetime] = None

class InstagramMediaRequest(BaseModel):
    recipient_id: str
    media_url: str
    media_type: str  # image, video, audio, file
    schedule_time: Optional[datetime] = None