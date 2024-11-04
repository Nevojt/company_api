
from pydantic import BaseModel, Strict, UUID4
from typing import Annotated

        
        

class PrivateRecipient(BaseModel):
    sender_id: Annotated[UUID4, Strict(False)] = None
    sender_name: str
    sender_avatar: str
    receiver_id: Annotated[UUID4, Strict(False)] = None
    receiver_name: str
    receiver_avatar: str

class PrivateInfoRecipient(BaseModel):
    receiver_id: Annotated[UUID4, Strict(False)] = None
    receiver_name: str
    receiver_avatar: str
    verified: bool
    is_read: bool



        
        



