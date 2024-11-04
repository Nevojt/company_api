
from pydantic import BaseModel, ConfigDict, UUID4, Strict    #, HttpUrl
from datetime import datetime
from typing import Optional, List, Annotated




class RoomBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Annotated[UUID4, Strict(False)]
    owner: Annotated[UUID4, Strict(False)]
    name_room: str
    image_room: str
    count_users: int
    count_messages: int
    created_at: datetime
    secret_room: bool
    block: Optional[bool] = None
    description: Optional[str] = None
    delete_at: Optional[datetime] = None
        
class RoomFavorite(RoomBase):
    favorite: bool
    
    
class RoomCreate(BaseModel):
    name_room: str
    image_room: str
    secret_room: bool = False
    
class RoomCreateV2(BaseModel):
    name_room: str
    secret_room: bool = False
    description: Optional[str] = None

class RoomPost(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

        
class RoomUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Annotated[UUID4, Strict(False)]
    name_room: str
    image_room: str
    owner: Annotated[UUID4, Strict(False)]
    created_at: datetime
    secret_room: Optional[Optional[bool]]
    block: bool
    description: Optional[str] = None
    delete_at: Optional[datetime] = None
       
class RoomUpdateDescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    description: Optional[str] = None
        
class RoomManager(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    room_id: Annotated[UUID4, Strict(False)]
    
        
class RoomTabsCreate(BaseModel):
    name_tab: Optional[str] = None
    image_tab: Optional[str] = None
    
class TabUpdate(RoomTabsCreate):
    pass 
    
    
class Tab(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    rooms: List[RoomBase]
    



class CountMessages(BaseModel):
    rooms: str
    count: int
    
class CountUsers(BaseModel):
    rooms: str
    count: int