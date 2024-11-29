from pydantic import BaseModel
from typing import List, Optional, Union

class TemplateButton(BaseModel):
    type: str  # quick_reply, url
    text: str
    url: Optional[str] = None

class TemplateMedia(BaseModel):
    type: str  # image, video, document
    url: str
    filename: Optional[str] = None

class TemplateComponent(BaseModel):
    type: str  # header, body, footer, buttons
    parameters: Optional[List[str]] = []
    text: Optional[str] = None
    buttons: Optional[List[TemplateButton]] = None
    media: Optional[TemplateMedia] = None

class WhatsAppTemplate(BaseModel):
    name: str
    language_code: str = "en"
    category: str
    components: List[TemplateComponent]

class TemplateMessage(BaseModel):
    recipient: str
    template_name: str
    language_code: str = "en"
    components: List[TemplateComponent]