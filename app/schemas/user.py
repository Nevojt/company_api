
<<<<<<< HEAD
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
=======
from pydantic import BaseModel, EmailStr, UUID4, ConfigDict, Strict
from datetime import datetime
from typing import Optional, Annotated
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        
        
        
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
<<<<<<< HEAD
    id: int
=======
    id: Annotated[UUID4, Strict(False)]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    user_name: str
    avatar: str
    created_at: datetime
        
        
class UserStatus(BaseModel):
    room_name: str
    user_name: str
<<<<<<< HEAD
    user_id: int
    status: bool = True
    room_id: int
=======
    user_id: Annotated[UUID4, Strict(False)]
    status: bool = True
    room_id: Annotated[UUID4, Strict(False)]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
   
    
class UserStatusCreate(UserStatus):
    pass


class UserStatusUpdate(BaseModel):
    name_room: str
    status: bool = True


class UserStatusPost(UserStatus):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
     
           
class UserCreate(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    avatar: str

   
class UserCreateV2(BaseModel):
    email: EmailStr
    user_name: str
    password: str
<<<<<<< HEAD
    
class UserCreateDel(UserCreate):
    verified: bool
    company_id: int
=======
    company_id: Annotated[UUID4, Strict(False)]
    
class UserCreateDel(UserCreate):
    verified: bool
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_name: str
    avatar: str
        
class UserUpdateAvatar(BaseModel):
    avatar: str
        
class UserUpdateUsername(BaseModel):
    user_name: str
    
class UserUpdateDescription(BaseModel):
    description: str
            
class UserLogin(BaseModel):
    email: EmailStr
    password: str
      
      
class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
<<<<<<< HEAD
    id: int
    email: str
    user_name: str
=======
    id: Annotated[UUID4, Strict(False)]
    email: str
    user_name: str
    full_name: Optional[str] = None
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    avatar: str
    description: Optional[str]
    created_at: datetime
    role: Optional[str]
    verified: bool
    blocked: bool
    token_verify: Optional[str] = None
<<<<<<< HEAD
    company_id: Optional[int] = None
=======
    company_id: Annotated[UUID4, Strict(False)] = None
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
class UserInfoLights(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
<<<<<<< HEAD
    id: int
=======
    id: Annotated[UUID4, Strict(False)]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    email: str
    user_name: str
    avatar: str
    verified: bool
<<<<<<< HEAD
    company_id: Optional[int] = None
=======
    company_id: Annotated[UUID4, Strict(False)] = None
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    active: bool
    
class UserDelete(BaseModel):
    password: str
    
class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str