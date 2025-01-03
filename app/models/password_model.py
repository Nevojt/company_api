
<<<<<<< HEAD
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

=======
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta, timezone
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from app.database.database import Base




class PasswordReset(Base):
    __tablename__ = 'password_reset'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, index=True)
    reset_code = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_active = Column(Boolean, default=True)
<<<<<<< HEAD
=======

class MailUpdateModel(Base):
    __tablename__ = 'mail_update'

    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    user_id = Column(UUID, nullable=False)
    new_email = Column(String, index=True)
    update_code = Column(String)
    update_token = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    expires_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(minutes=15))
    is_active = Column(Boolean, default=True)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    