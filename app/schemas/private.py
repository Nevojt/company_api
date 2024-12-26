
<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
=======
from pydantic import BaseModel, Strict, UUID4
from typing import Annotated
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

        
        

class PrivateRecipient(BaseModel):
<<<<<<< HEAD
    sender_id: int
    sender_name: str
    sender_avatar: str
    receiver_id: int
=======
    sender_id: Annotated[UUID4, Strict(False)] = None
    sender_name: str
    sender_avatar: str
    receiver_id: Annotated[UUID4, Strict(False)] = None
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    receiver_name: str
    receiver_avatar: str

class PrivateInfoRecipient(BaseModel):
<<<<<<< HEAD
    receiver_id: int
=======
    receiver_id: Annotated[UUID4, Strict(False)] = None
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    receiver_name: str
    receiver_avatar: str
    verified: bool
    is_read: bool


<<<<<<< HEAD
class PrivateReturnMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    created_at: datetime
    receiver_id: Optional[int] = None
    id: int
    message: Optional[str] = None
    fileUrl: Optional[str] = None
    user_name: Optional[str] = "USER DELETE"
    avatar: Optional[str] = "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp"
=======

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        
        



