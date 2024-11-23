

from _log_config.log_config import get_logger

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import user_model, room_model
from app.schemas import user as user_schema
from app.schemas import room as schema_room
from app.config.start_schema import start_app
from app.settings.get_info import get_count_messages, get_count_users


logger = get_logger('func_finds', 'func_search.log')



hell = start_app.default_room_name

async def get_search_users(pattern: str, db: AsyncSession):

    try:
        # Search for users
        users_query = await db.execute(select(user_model.User).where(
            func.lower(user_model.User.user_name).like(pattern)))
        users = users_query.scalars().all()

        users_info_list = []
        for user in users:
            user_info = user_schema.UserOut(
                id=user.id,
                user_name=user.user_name,
                avatar=user.avatar,
                created_at=user.created_at,
            )
            users_info_list.append(user_info)

        return users_info_list

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {e}")


async def get_search_rooms(pattern: str, db: AsyncSession):
    try:
        room_query =  await db.execute(select(room_model.Rooms).where(
            room_model.Rooms.name_room != hell,
            room_model.Rooms.secret_room == False,
            func.lower(room_model.Rooms.name_room).like(pattern),
            ))
        rooms = room_query.scalars().all()

        # Count messages for room
        messages_count = await get_count_messages(db)

        # Count users for room
        users_count = await get_count_users(db)

        rooms_info_list = []
        for room in rooms:
            room_info = schema_room.RoomBase(
                id=room.id,
                owner=room.owner,
                name_room=room.name_room,
                image_room=room.image_room,
                count_users=next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
                count_messages=next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
                created_at= room.created_at,
                secret_room=room.secret_room
            )
            rooms_info_list.append(room_info)

        return rooms_info_list
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {e}")