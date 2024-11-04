
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Strict, UUID4

from typing import  Annotated


class InvitationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id:  Annotated[UUID4, Strict(False)]
    sender_id:  Annotated[UUID4, Strict(False)]
    status: str
    created_at: datetime