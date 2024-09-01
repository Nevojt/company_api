
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

from app.database.database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('socket.id'), nullable=False)
    reported_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(String, nullable=False)
    additional_info = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Pending")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relationships
    message = relationship("Socket", back_populates="reports")
    reported_by_user = relationship("User", back_populates="reports")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    message_id = Column(Integer, ForeignKey('socket.id'), nullable=False)
    moderator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    seen = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)

    # Relationships
    room = relationship("Rooms", back_populates="notifications")
    message = relationship("Socket", back_populates="notifications")
    moderator = relationship("User", back_populates="notifications")