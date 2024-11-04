
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(UUID, ForeignKey('chat_messages.id'), nullable=False)
    reported_by_user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    reason = Column(String, nullable=False)
    additional_info = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Pending")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    responsive_id = Column(UUID, nullable=True)
    reaction_at = Column(TIMESTAMP(timezone=True), nullable=True)
    

    # Relationships
    message = relationship("ChatMessages", back_populates="reports")
    reported_by_user = relationship("User", back_populates="reports")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(UUID, ForeignKey('rooms.id'), nullable=False)
    message_id = Column(UUID, ForeignKey('chat_messages.id'), nullable=False)
    moderator_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    seen = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)

    # Relationships
    rooms = relationship("Rooms", back_populates="notifications")
    message = relationship("ChatMessages", back_populates="notifications")
    moderator = relationship("User", back_populates="notifications")