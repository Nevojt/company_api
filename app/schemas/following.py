from pydantic import BaseModel, ConfigDict
from datetime import datetime




class Follower(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_name: str
    avatar: str
    following_at: datetime
    