
<<<<<<< HEAD
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
=======
from typing import Optional, Annotated
from pydantic import BaseModel, UUID4, Strict
from datetime import datetime


class ReportMessage(BaseModel):
    message_id: Annotated[UUID4, Strict(False)]
    reason: str
    additional_info: Optional[str] = None


class NotificationToModerator(BaseModel):
    room_id: Annotated[UUID4, Strict(False)]
    message_id: Annotated[UUID4, Strict(False)]
    moderator_id: Annotated[UUID4, Strict(False)]
    seen: bool = False


class ReportsGetNotification(BaseModel):
    report_id: int
    reporter_by_user_id: Annotated[UUID4, Strict(False)]
    message_id: Annotated[UUID4, Strict(False)]
    message: str
    room_id: Annotated[UUID4, Strict(False)]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    room: str
    reason: str
    additional_info: Optional[str] = None
    status: str
    seen: bool
<<<<<<< HEAD
    created_at: datetime
=======
    created_at: datetime
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
