
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

        
        

class PrivateRecipient(BaseModel):
    sender_id: int
    sender_name: str
    sender_avatar: str
    receiver_id: int
    receiver_name: str
    receiver_avatar: str

class PrivateInfoRecipient(BaseModel):
    receiver_id: int
    receiver_name: str
    receiver_avatar: str
    verified: bool
    is_read: bool


class PrivateReturnMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    created_at: datetime
    receiver_id: Optional[int] = None
    id: int
    message: Optional[str] = None
    fileUrl: Optional[str] = None
    user_name: Optional[str] = "USER DELETE"
    avatar: Optional[str] = "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp"
        
        



