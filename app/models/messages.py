from typing import List, Optional, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime

class Button(BaseModel):
    type: str  # quick_reply, url
    text: str
    url: Optional[HttpUrl] = None

class MediaContent(BaseModel):
    type: str  # image, video, document
    url: HttpUrl
    caption: Optional[str] = None

class TemplateContent(BaseModel):
    header: Optional[Union[str, MediaContent]] = None
    body: str
    footer: Optional[str] = None
    buttons: Optional[List[Button]] = None

class BatchMessage(BaseModel):
    template_name: str
    language_code: str = "en"
    recipients: List[str]
    content: TemplateContent
    scheduled_time: Optional[datetime] = None

class ScheduledMessage(BaseModel):
    recipient: str
    message: str
    scheduled_time: datetime
    status: str = "pending"

class MessageResponse(BaseModel):
    from_number: str
    message: str
    timestamp: datetime