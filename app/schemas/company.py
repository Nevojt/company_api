<<<<<<< HEAD
from pydantic import BaseModel, EmailStr, ConfigDict, Field, constr

from typing import Dict, Optional


=======

from pydantic import BaseModel, EmailStr, ConfigDict, Field, Strict, UUID4

from typing import Dict, Optional, Annotated
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


class CompanyCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., max_length=255)
    subdomain: str = Field(..., max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
<<<<<<< HEAD
    subscription_status: Optional[str] = Field(None, max_length=50)
=======
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    subscription_end_date: Optional[str] = None
    subscription_type: Optional[str] = Field(None, max_length=50)
    paid_services: Optional[str] = None
    company_code: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    services: Optional[str] = None
    additional_contacts: Optional[str] = None
    settings: Optional[Dict] = None


class CompanySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
<<<<<<< HEAD
    id: int
    name: str
    subdomain: str
    subscription_status: str
    subscription_end_date: str
=======
    id: Annotated[UUID4, Strict(False)]
    name: str
    subdomain: str
    subscription_status: str
    subscription_end_date: Optional[str] = None
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

class CompanyUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(None, max_length=255)
<<<<<<< HEAD
    subdomain: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    subscription_status: Optional[str] = Field(None, max_length=50)
=======
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    company_code: Optional[str] = Field(None, max_length=50)
    logo_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    additional_contacts: Optional[str] = None

class CompanyUpdateSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subdomain: str = Field(..., max_length=255)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    subscription_end_date: Optional[str] = None
    subscription_type: Optional[str] = Field(None, max_length=50)
    paid_services: Optional[str] = None
    company_code: Optional[str] = Field(None, max_length=50)
<<<<<<< HEAD
    logo_url: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    services: Optional[str] = None
    additional_contacts: Optional[str] = None
    settings: Optional[Dict] = None
=======
    services: Optional[str] = None
    settings: Optional[Dict] = None

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
class CompanyCodeVerification(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    code_verification: str