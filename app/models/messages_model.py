
<<<<<<< HEAD
# from tkinter import CASCADE
=======

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from sqlalchemy import JSON, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
<<<<<<< HEAD
=======
from sqlalchemy.dialects.postgresql import UUID
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from app.database.database import Base




<<<<<<< HEAD
class Socket(Base):
    __tablename__ = 'socket'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    message = Column(String)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    rooms = Column(String, ForeignKey('rooms.name_room', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_return = Column(Integer)
    fileUrl = Column(String)
    edited = Column(Boolean, server_default='false') 
    return_message = Column(JSON, server_default=None)
    delete = Column(Boolean, server_default='false')
    
=======
class ChatMessages(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    message = Column(String)
    fileUrl = Column(String)
    voiceUrl = Column(String)
    videoUrl = Column(String)
    receiver_id = Column(UUID, ForeignKey('users.id', ondelete='SET NULL'))
    rooms = Column(String, ForeignKey('rooms.name_room', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    room_id = Column(UUID, ForeignKey('rooms.id', ondelete='CASCADE'))
    id_return = Column(Integer)

    edited = Column(Boolean, server_default='false') 
    return_message = Column(JSON, server_default=None)
    deleted = Column(Boolean, server_default='false')

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    # Relationships
    reports = relationship("Report", back_populates="message")
    notifications = relationship("Notification", back_populates="message")
    
class PrivateMessage(Base):
    __tablename__ = 'private_messages'
    
<<<<<<< HEAD
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_read = Column(Boolean, nullable=False, default=True)
    fileUrl = Column(String)
    edited = Column(Boolean, server_default='false')
    id_return = Column(Integer)
    
    
    
class Vote(Base):
    __tablename__ = 'votes'
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(Integer, ForeignKey("socket.id", ondelete="CASCADE"), primary_key=True)
=======
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'), nullable=False)
    sender_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String)
    fileUrl = Column(String)
    voiceUrl = Column(String)
    videoUrl = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_read = Column(Boolean, nullable=False, server_default='false')
    edited = Column(Boolean, server_default='false')
    id_return = Column(Integer)
    deleted = Column(Boolean, server_default='false')
    room_id = Column(UUID, nullable=True)
    is_sent = Column(Boolean, default=False)

    
    
class ChatMessageVote(Base):
    __tablename__ = 'chat_message_votes'
    
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(UUID, ForeignKey("chat_messages.id", ondelete="CASCADE"), primary_key=True)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    dir = Column(Integer)
    
    
class PrivateMessageVote(Base):
    __tablename__ = 'private_message_votes'
    
<<<<<<< HEAD
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(Integer, ForeignKey("private_messages.id", ondelete="CASCADE"), primary_key=True)
=======
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(UUID, ForeignKey("private_messages.id", ondelete="CASCADE"), primary_key=True)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    dir = Column(Integer) 