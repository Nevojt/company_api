from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, Strict, UUID4

from datetime import datetime

from typing_extensions import Annotated


class SocketModel(BaseModel):
    created_at: datetime
    receiver_id:  Annotated[UUID4, Strict(False)] = None
    id: int
    message: Optional[str] = None
    fileUrl: Optional[str] = None
    user_name: Optional[str] = "USER DELETE"
    avatar: Optional[str] = "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp"
    verified: Optional[bool] = None
    vote: int
    id_return: Optional[int] = None
    edited: bool
    deleted: bool
    room_id: Annotated[UUID4, Strict(False)] = None


# Send message to chat
class WrappedSocketMessage(BaseModel):
    message: SocketModel


async def wrap_message(socket_model_instance: SocketModel) -> WrappedSocketMessage:
    return WrappedSocketMessage(message=socket_model_instance)

class SocketReturnMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    created_at: datetime
    receiver_id: Annotated[UUID4, Strict(False)] = None
    id: int
    message: Optional[str] = None
    fileUrl: Optional[str] = None
    user_name: Optional[str] = "USER DELETE"
    avatar: Optional[str] = "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp"
    deleted: bool
    room_id: Annotated[UUID4, Strict(False)] = None

class SocketUpdate(BaseModel):
    message: str
    
class Vote(BaseModel):
    message_id: int
    dir: Annotated[int, Field(strict=True, le=1)]