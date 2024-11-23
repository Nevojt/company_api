
<<<<<<< HEAD
from typing import Optional
from pydantic import BaseModel
=======
from typing import Annotated
from pydantic import BaseModel, Strict, UUID4
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    
class TokenData(BaseModel):
<<<<<<< HEAD
    id: Optional[int] = None
=======
    id: Annotated[UUID4, Strict(False)]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
