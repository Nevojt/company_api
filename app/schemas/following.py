from pydantic import BaseModel, ConfigDict, UUID4, Strict
from typing import Annotated
from datetime import datetime

class Follower(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[UUID4, Strict(False)]
    user_name: str
    avatar: str
    following_at: datetime
