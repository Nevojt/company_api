
from app.config.start_schema import start_app
from app.models import user_model, room_model

from sqlalchemy.future import select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from _log_config.log_config import get_logger

default_logger = get_logger('default', 'default_info.log')

async def get_default_user(db: AsyncSession):
    try:
        default_user = start_app.default_user

        query_user = await db.execute(select(user_model.User).where(
            user_model.User.user_name == default_user))

        user_default = query_user.scalar_one_or_none()
        if user_default is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user_default
    except Exception as e:
        default_logger.error(f"Error in get_default_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_default_room(db: AsyncSession):
    try:
        default_room = start_app.default_room

        query_room = await db.execute(select(room_model.Rooms).where(
            room_model.Rooms.name_room == default_room))

        room_default = query_room.scalar_one_or_none()
        if room_default is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

        return room_default
    except Exception as e:
        default_logger.error(f"Error in get_default_room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))