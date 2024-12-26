
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
<<<<<<< HEAD
=======
from sqlalchemy.dialects.postgresql import UUID
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

from app.database.database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
<<<<<<< HEAD
    message_id = Column(Integer, ForeignKey('socket.id'), nullable=False)
    reported_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
=======
    message_id = Column(UUID, ForeignKey('chat_messages.id'), nullable=False)
    reported_by_user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    reason = Column(String, nullable=False)
    additional_info = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Pending")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
<<<<<<< HEAD
    responsive_id = Column(Integer, nullable=True)
=======
    responsive_id = Column(UUID, nullable=True)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    reaction_at = Column(TIMESTAMP(timezone=True), nullable=True)
    

    # Relationships
<<<<<<< HEAD
    message = relationship("Socket", back_populates="reports")
=======
    message = relationship("ChatMessages", back_populates="reports")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    reported_by_user = relationship("User", back_populates="reports")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
<<<<<<< HEAD
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    message_id = Column(Integer, ForeignKey('socket.id'), nullable=False)
    moderator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
=======
    room_id = Column(UUID, ForeignKey('rooms.id'), nullable=False)
    message_id = Column(UUID, ForeignKey('chat_messages.id'), nullable=False)
    moderator_id = Column(UUID, ForeignKey('users.id'), nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    seen = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)

    # Relationships
<<<<<<< HEAD
    room = relationship("Rooms", back_populates="notifications")
    message = relationship("Socket", back_populates="notifications")
=======
    rooms = relationship("Rooms", back_populates="notifications")
    message = relationship("ChatMessages", back_populates="notifications")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    moderator = relationship("User", back_populates="notifications")