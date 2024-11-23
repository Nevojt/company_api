from _log_config.log_config import get_logger
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import room_model
from app.settings.get_info import start_app

logger = get_logger('tabs_info', 'tabs_info.log')

async def get_tabs_user(user_id: UUID,
                        db: AsyncSession):
    try:
        # Fetch all tabs for the current user
        user_tabs_query = await db.execute(select(room_model.RoomTabsInfo).where(
                                                room_model.RoomTabsInfo.owner_id == user_id))
        user_tabs = user_tabs_query.scalars().all()
        return user_tabs
    except Exception as e:
        logger.error(f"Error getting tabs for user {e}")



async def get_one_tab_user(user_id: UUID, tab_id: int,
                            db: AsyncSession):
    try:
        tab_exists = await db.execute(select(room_model.RoomTabsInfo).where(
                                                room_model.RoomTabsInfo.owner_id == user_id,
                                                            room_model.RoomTabsInfo.id == tab_id))
        tab_exists = tab_exists.scalar_one_or_none()
        return tab_exists
    except Exception as e:
        logger.error(f"Error getting tab for user {user_id} with ID {tab_id}: {e}")



async def get_room_tab(room_id: UUID, db: AsyncSession):
    try:
        room_tab_query = await db.execute(select(room_model.RoomsTabs).where(
                                    room_model.RoomsTabs.room_id == room_id))
        room_tab = room_tab_query.scalar_one_or_none()
        return room_tab
    except Exception as e:
        logger.error(f"Error getting room tab for room {room_id}: {e}")



async def get_favorite_record(user_id: UUID, room_id: UUID,
                               db: AsyncSession):
    try:
        favorite_record_query = await db.execute(select(room_model.RoomsTabs).where(
            room_model.RoomsTabs.room_id == room_id,
            room_model.RoomsTabs.user_id == user_id
        ))
        favorite_record = favorite_record_query.scalar_one_or_none()
        return favorite_record
    except Exception as e:
        logger.error(f"Error getting favorite record for user {user_id} in room {room_id}: {e}")


async def get_room_tab_id(room_id: UUID, tab_id: int, db:AsyncSession):
    try:
        room_link = await db.execute(select(room_model.RoomsTabs).where(
                                    room_model.RoomsTabs.room_id == room_id,
                                                room_model.RoomsTabs.tab_id == tab_id))
        room_link_id = room_link.scalar_one_or_none()
        return room_link_id
    except Exception as e:
        logger.error(f"Error getting room tab ID for room {room_id} with ID {tab_id}: {e}")


