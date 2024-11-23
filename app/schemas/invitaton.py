<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
from datetime import datetime

=======

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Strict, UUID4

from typing import  Annotated


>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
class InvitationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
<<<<<<< HEAD
    room_id: int
    sender_id: int
=======
    room_id:  Annotated[UUID4, Strict(False)]
    sender_id:  Annotated[UUID4, Strict(False)]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    status: str
    created_at: datetime