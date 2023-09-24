from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint
        
        
class MessageBase(BaseModel):
    message: str
    is_privat: bool = False
    receiver: Optional[int]
    rooms: str
    
    
class MessageCreate(MessageBase):
    pass


class UserOut(BaseModel):
    id: int
    user_name: str
    avatar: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        

class MessagePost(MessageBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    
    class Config:
        from_attributes = True
        
class MessageOut(BaseModel):
    Message: MessagePost
    votes: int
    
    class Config:
        from_attributes = True
        
        
        
        
        
class RoomBase(BaseModel):
    name_room: str
    image_room: str
    
    
class RoomCreate(RoomBase):
    pass

class RoomPost(RoomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        



        
class UserStatus(BaseModel):
    room_name: str
    user_name: str
    user_id: int
    status: bool = True
    
class UserStatusCreate(UserStatus):
    pass

class UserStatusPost(UserStatus):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
    
        
        
        
class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    avatar: str
    
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: Optional[int] = None
    
    
class Vote(BaseModel):
    message_id: int
    dir: conint(le=1)