import logging
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.models import company_model, room_model, user_model, messages_model
from app.config.start_schema import start_app


logging.basicConfig(filename='_log/get_info.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

hell = start_app.default_room_name


async def get_company(subdomain: str, db: AsyncSession):
    try:
        company_query = await db.execute(select(company_model.Company).where(
            company_model.Company.subdomain == subdomain))

        company = company_query.scalar_one_or_none()
        return company
    except Exception as e:
        logger.error(f"Error in get_company: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error in get_company")

async def get_room_hell(db: AsyncSession):
    try:
        room_query = await db.execute((select(room_model.Rooms).where(room_model.Rooms.name_room == hell)))
        room = room_query.scalar_one_or_none()
        return room
    except Exception as e:
        logger.error(f"Error in get_room_hell: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error in get_room_hell")

async def get_user(user_id: UUID, db: AsyncSession):
    try:
        user_query = await db.execute(select(user_model.User).where(user_model.User.id == user_id))
        user_result = user_query.scalar_one_or_none()
        return user_result
    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error in get_user")

async def get_user_for_email(email: str, db: AsyncSession):
    try:
        email_query = await db.execute(select(user_model.User).where(user_model.User.email == email))
        existing_email_user = email_query.scalar_one_or_none()
        return existing_email_user
    except Exception as e:
        logger.error(f"Error in get_user_for_email: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error in get_user_for_email")

async def get_user_for_username(user_name: str, db: AsyncSession):
    try:
        username_query = await db.execute(select(user_model.User).where(user_model.User.email == user_name))
        existing_username = username_query.scalar_one_or_none()
        return existing_username
    except Exception as e:
        logger.error(f"Error in get_user_for_username: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Error in get_user_for_username")

async def check_deactivation_user(email: str, user_name: str, db: AsyncSession):
    try:
        existing_deactivated_user = await db.execute(select(user_model.UserDeactivation).where(
            (user_model.UserDeactivation.email == email) |
            (user_model.UserDeactivation.user_name == user_name)))

        existing_deactivated = existing_deactivated_user.scalar_one_or_none()
        return existing_deactivated
    except Exception as e:
        logger.error(f"Error in check_deactivation_user: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Error in check_deactivation_user")



async def get_room_name(name_room: str, db: AsyncSession):
    try:
        query_room = await db.execute(select(room_model.Rooms).where(room_model.Rooms.name_room == name_room))
        room = query_room.scalar_one_or_none()
        return room
    except Exception as e:
        logger.error(f"Error occurred while retrieving room name: {e}")
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(e))


async def get_room_by_id(room_id: UUID, db: AsyncSession):
    try:
        result = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id))
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error occurred while retrieving room by ID: {e}")
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(e))

async def has_permission_to_the_room(current_user: user_model.User, room: room_model.Rooms):
    try:
        return current_user.role == "admin" or current_user.id == room.owner
    except Exception as e:
        logger.error(f"Error occurred while checking permissions: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

async def has_verified_or_blocked_user(current_user: user_model.User):
    try:
        return not current_user.verified or current_user.blocked
    except Exception as e:
        logger.error(f"Error occurred while checking user verification and block status: {e}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


async def get_count_messages(db: AsyncSession):
    try:
        messages_count = await db.execute(
            select(
                messages_model.ChatMessages.rooms,
                func.count(messages_model.ChatMessages.id).label('count')
            )
            .group_by(messages_model.ChatMessages.rooms)
            .where(messages_model.ChatMessages.rooms != hell)
        )
        messages_count = messages_count.all()
        return messages_count
    except Exception as e:
        logger.error(f"Error occurred while retrieving messages count: {e}")
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(e))

async def get_count_users(db: AsyncSession):
    try:
        users_count = await db.execute(
            select(
                user_model.UserStatus.name_room,
                func.count(user_model.UserStatus.id).label('count')
            )
            .group_by(user_model.UserStatus.name_room)
            .where(user_model.UserStatus.name_room != hell)
        )
        users_count = users_count.all()
        return users_count
    except Exception as e:
        logger.error(f"Error occurred while retrieving users count: {e}")
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY, detail=str(e))