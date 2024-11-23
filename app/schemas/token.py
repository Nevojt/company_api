
from typing import Annotated
from pydantic import BaseModel, Strict, UUID4


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
#
class TokenData(BaseModel):
    id: Annotated[UUID4, Strict(False)]