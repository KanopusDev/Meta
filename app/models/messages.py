
from datetime import datetime
from pydantic import BaseModel

class ScheduledMessage(BaseModel):
    recipient: str
    message: str
    scheduled_time: datetime
    status: str = "pending"

class MessageResponse(BaseModel):
    from_number: str
    message: str
    timestamp: datetime