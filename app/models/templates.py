
from pydantic import BaseModel
from typing import List, Optional

class TemplateComponent(BaseModel):
    type: str  # header, body, footer, buttons
    format: Optional[str] = None  # text, image, video, document
    text: Optional[str] = None
    buttons: Optional[List[dict]] = None

class WhatsAppTemplate(BaseModel):
    name: str
    language_code: str = "en"
    category: str  # MARKETING, UTILITY, AUTHENTICATION
    components: List[TemplateComponent]

class TemplateMessage(BaseModel):
    template_name: str
    recipient: str
    language_code: str = "en"
    components: Optional[List[dict]] = None