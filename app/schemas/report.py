
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
    room: str
    reason: str
    additional_info: Optional[str] = None
    status: str
    seen: bool
    created_at: datetime
