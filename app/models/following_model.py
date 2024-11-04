from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base




class Following(Base):
    __tablename__ = 'following'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    following_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    follower_id = Column(UUID, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    
    