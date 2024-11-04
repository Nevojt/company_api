
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Strict, UUID4

from typing import Annotated



class TokenFCMCreate(BaseModel):

    id: int
    user_id: Annotated[UUID4, Strict(False)]
    fcm_token: str
    platform: str
    created_at: datetime
    updated_at: datetime


class TokenFCM(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fcm_token: str
    platform: str