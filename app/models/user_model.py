from datetime import timedelta
<<<<<<< HEAD
from sqlalchemy import JSON, Column, Integer, Interval, String, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql.expression import text
=======

from sqlalchemy import JSON, Column, Integer, Interval, String, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.postgresql import UUID
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from enum import Enum as PythonEnum
from app.database.database import Base



class UserRole(str, PythonEnum):
    super_admin = "super_admin"
    admin = "admin"
    user = "user"
	
    
 
 
 
class User(Base):
    __tablename__ = 'users'
    
<<<<<<< HEAD
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    user_name = Column(String, nullable=False, unique=True)
=======
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'), nullable=False)
    email = Column(String, nullable=False, unique=True)
    user_name = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=True)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    verified = Column(Boolean, nullable=False, server_default='false')
    token_verify = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user)
    blocked = Column(Boolean, nullable=False, server_default='false')
    password_changed = Column(TIMESTAMP(timezone=True), nullable=True)
<<<<<<< HEAD
    company_id = Column(Integer, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    active = Column(Boolean, nullable=False, server_default='True')
    description = Column(String)
    
    company = relationship("Company", back_populates="users")
    bans = relationship("Ban", back_populates="user")
=======
    company_id = Column(UUID, ForeignKey('companies.id', ondelete="CASCADE"), nullable=True)
    active = Column(Boolean, nullable=False, server_default='True')
    description = Column(String)

    
    company = relationship("Company", back_populates="users")
    bans = relationship("Ban", back_populates="users")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    # Relationships
    reports = relationship("Report", back_populates="reported_by_user")
    notifications = relationship("Notification", back_populates="moderator")
    
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('user_name', name='uq_user_name'),
    )
    
<<<<<<< HEAD
class User_Status(Base):
    __tablename__ = 'user_status' 
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name_room = Column(String, ForeignKey("rooms.name_room", ondelete="CASCADE", onupdate='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False)
=======
class UserStatus(Base):
    __tablename__ = 'user_status' 
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    room_id = Column(UUID, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name_room = Column(String, ForeignKey("rooms.name_room", ondelete="CASCADE", onupdate='CASCADE'), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    user_name = Column(String, nullable=False)
    status = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
 
    
class UserOnlineTime(Base):
    __tablename__ = 'user_online_time'

    id = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
=======
    user_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    session_start = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    session_end = Column(TIMESTAMP(timezone=True), nullable=True)
    total_online_time = Column(Interval, nullable=True, default=timedelta())
    
    
class UserDeactivation(Base):
    __tablename__ = 'user_deactivation'
    
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    deactivated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    reason = Column(String, nullable=True)
    roles = Column(JSON)
<<<<<<< HEAD
    company_id = Column(Integer, nullable=False)
=======
    company_id = Column(UUID, nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
    __table_args__ = (
        UniqueConstraint('email', name='uq_deactivation_email'),
        UniqueConstraint('user_name', name='uq_deactivation_user_name'),
    )

<<<<<<< HEAD
    
=======
class FCMTokenManager(Base):
    __tablename__ = 'fcm_token_manager'

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    fcm_token = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
 