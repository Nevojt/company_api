
from typing import Optional
from pydantic import BaseModel

class ReportMessage(BaseModel):
    
    message_id: int
    reason: str
    additional_info: Optional[str] = None
    
class NotificationToModerator(BaseModel):
    
    room_id: int
    message_id: int
    moderator_id: int
    seen: bool = False
    