

from sqlalchemy import JSON, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.database import Base




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
    id_return = Column(UUID, nullable=True)

    edited = Column(Boolean, server_default='false') 
    return_message = Column(JSON, server_default=None)
    deleted = Column(Boolean, server_default='false')

    # Relationships
    reports = relationship("Report", back_populates="message")
    notifications = relationship("Notification", back_populates="message")
    
class PrivateMessage(Base):
    __tablename__ = 'private_messages'
    
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
    id_return = Column(UUID, nullable=True)
    deleted = Column(Boolean, server_default='false')
    room_id = Column(UUID, nullable=True)
    is_sent = Column(Boolean, default=False)

    
    
class ChatMessageVote(Base):
    __tablename__ = 'chat_message_votes'
    
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(UUID, ForeignKey("chat_messages.id", ondelete="CASCADE"), primary_key=True)
    dir = Column(Integer)
    
    
class PrivateMessageVote(Base):
    __tablename__ = 'private_message_votes'
    
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    message_id = Column(UUID, ForeignKey("private_messages.id", ondelete="CASCADE"), primary_key=True)
    dir = Column(Integer) 