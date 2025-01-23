<<<<<<< HEAD
from sqlalchemy import JSON, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
=======
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

from app.database.database import Base




class Following(Base):
    __tablename__ = 'following'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    following_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
<<<<<<< HEAD
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    follower_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
=======
    user_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    follower_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
    