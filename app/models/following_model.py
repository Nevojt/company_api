from sqlalchemy import JSON, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.database.database import Base




class Following(Base):
    __tablename__ = 'following'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    following_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    follower_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    
    