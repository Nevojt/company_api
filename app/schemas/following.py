<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
from datetime import datetime




class Follower(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_name: str
    avatar: str
    following_at: datetime
    
=======
from pydantic import BaseModel, ConfigDict, UUID4, Strict
from typing import Annotated
from datetime import datetime

class Follower(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[UUID4, Strict(False)]
    user_name: str
    avatar: str
    following_at: datetime
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
