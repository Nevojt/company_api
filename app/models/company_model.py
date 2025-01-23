
<<<<<<< HEAD
from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from app.database.database import Base



=======
from sqlalchemy import JSON, Column, String, Enum, Integer, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from enum import Enum as PythonEnum

class StatusSubscription(str, PythonEnum):
    active = "active"
    suspended = "suspended"
    inactive = "inactive"
    wait = "wait"
    
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

class Company(Base):
    __tablename__ = 'companies'

<<<<<<< HEAD
    id = Column(Integer, primary_key=True, autoincrement=True)
=======
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'), nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    name = Column(String(255), nullable=False)
    subdomain = Column(String(255), unique=True, nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    address = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
<<<<<<< HEAD
    subscription_status = Column(String(50))
=======
    subscription_status = Column(Enum(StatusSubscription), default=StatusSubscription.wait)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
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
<<<<<<< HEAD
    rooms = relationship("Rooms", back_populates="company", cascade="all, delete")
=======
    rooms = relationship("Rooms", back_populates="company", cascade="all, delete")


class CompanyDB(Base):
    __tablename__ = 'companies_credentials'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'), nullable=False)
    company_id = Column(UUID, ForeignKey('companies.id'), nullable=False)
    database_url = Column(String)
    database_name = Column(String)
    port = Column(Integer)
    username = Column(String)
    password = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
