
from sqlalchemy import JSON, Column, String, Enum
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from enum import Enum as PythonEnum

class StatusSubscription(str, PythonEnum):
    active = "active"
    suspend = "suspended"
    inactive = "inactive"
    wait = "wait"
    

class Company(Base):
    __tablename__ = 'companies'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'), nullable=False)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(255), unique=True, nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    address = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    subscription_status = Column(Enum(StatusSubscription), default=StatusSubscription.wait)
    subscription_end_date = Column(String)
    subscription_type = Column(String(50))
    paid_services = Column(String)
    company_code = Column(String(50))
    logo_url = Column(String(255))
    description = Column(String)
    services = Column(String)
    additional_contacts = Column(String)
    settings = Column(JSON)
    code_verification = Column(String(255))
    
    users = relationship("User", back_populates="company", cascade="all, delete")
    rooms = relationship("Rooms", back_populates="company", cascade="all, delete")