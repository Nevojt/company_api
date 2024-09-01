
from email import message
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ReportMessage(BaseModel):
    
    message_id: int
    reason: str
    additional_info: Optional[str] = None
    
class NotificationToModerator(BaseModel):
    
    room_id: int
    message_id: int
    moderator_id: int
    seen: bool = False
    
    
class ReportsGetNotification(BaseModel):
    
    report_id: int
    reporter_by_user_id: int
    message_id: int
    message: str
    room_id: int
    room: str
    reason: str
    additional_info: Optional[str] = None
    status: str
    seen: bool
    created_at: datetime