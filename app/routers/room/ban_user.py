<<<<<<< HEAD
=======

from uuid import UUID
from _log_config.log_config import get_logger
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database.async_db import get_async_session
from datetime import datetime, timedelta
import pytz
from app.auth import oauth2
from app.models import user_model, room_model
<<<<<<< HEAD



=======
from app.settings.get_info import get_room_by_id


logger = get_logger('mute_user', 'mute_user.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
router = APIRouter(
    prefix="/mute",
    tags=['Mute Users']
)


@router.get('/mute-users/{room_id}')
<<<<<<< HEAD
async def list_mute_users(room_id: int, db: AsyncSession = Depends(get_async_session), 
                          current_user: user_model.User = Depends(oauth2.get_current_user)):

    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    room_query = select(room_model.Rooms).where(room_model.Rooms.id == room_id)
    room_result = await db.execute(room_query)
    room = room_result.scalar_one_or_none()
    
    role_room = select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room_id,
                                                room_model.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_room)
    role_in_room = result.scalar_one_or_none()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")

    if (room.owner != current_user.id and (role_in_room is None or role_in_room.role != "moderator")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to view banned users in this room.")

    mute_users_query = select(room_model.Ban).options(joinedload(room_model.Ban.user)).where(room_model.Ban.room_id == room_id)
    result = await db.execute(mute_users_query)
    bans = result.scalars().all()

    if not bans:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No banned users found in room ID: {room_id}")

    users_info = [{
        "id": ban.user.id,
        "user_name": ban.user.user_name,
        "avatar": ban.user.avatar,
    } for ban in bans if ban.user]

    return users_info
=======
async def list_mute_users(room_id: UUID,
                          db: AsyncSession = Depends(get_async_session),
                          current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        get_room = await get_room_by_id(room_id, db)
        if get_room.owner != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You do not have permission to mute users in this room.")

        if not get_room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID: {room_id} not found")

        role_room = await db.execute(select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room_id,
                                                    room_model.RoleInRoom.user_id == current_user.id))
        role_in_room = role_room.scalar_one_or_none()

        if not role_in_room or role_in_room.role != "moderator":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not the owner or a moderator of this room.")

        mute_users_query = select(room_model.Ban).options(joinedload(room_model.Ban.users)).where(room_model.Ban.room_id == room_id)
        result = await db.execute(mute_users_query)
        bans = result.scalars().all()

        if not bans:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No banned users found in room ID: {room_id}")
        current_time_utc = datetime.now(pytz.timezone('UTC'))
        current_time_naive = current_time_utc.replace(tzinfo=None)
        users_info = [{
            "id": ban.users.id,
            "user_name": ban.users.user_name,
            "avatar": ban.users.avatar,
            "mute_minutes": (ban.end_time - current_time_naive) / 60
        } for ban in bans if ban.users]

        return users_info

    except Exception as e:
        logger.error(f"An error occurred while retrieving mute users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824



@router.post('/mute-user')
<<<<<<< HEAD
async def mute_user(user_id: int, room_id: int, duration_minutes: int, 
=======
async def mute_user(user_id: UUID, room_id: UUID, duration_minutes: int,
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Mute a user in a specific room.

    Parameters:
    user_id (int): The ID of the user to be muted.
    room_id (int): The ID of the room where the user is to be muted.
    duration_minutes (int): The duration in minutes for which the user will be muted.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (user_model.User): The current user making the request.

    Returns:
    dict: A dictionary containing a success message and the ID of the muted user.

    Raises:
    HTTPException: If the room does not exist, the user is not a moderator or owner of the room, or the user_id is not valid.
    """
<<<<<<< HEAD
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
    
    if duration_minutes < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Duration must be a positive integer.")
        
    current_time_utc = datetime.now(pytz.timezone('UTC'))
    current_time_naive = current_time_utc.replace(tzinfo=None)
    
    room_get = select(room_model.Rooms).where(room_model.Rooms.id == room_id)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    role_room = select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room_id,
                                                room_model.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_room)
    role_in_room = result.scalar_one_or_none()
    
    # Check if the role exists and is a moderator or owner
    if not existing_room or (existing_room.owner != current_user.id and (role_in_room is None or role_in_room.role != "moderator")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner or a moderator of this room.")
                
    end_time = current_time_naive + timedelta(minutes=duration_minutes)
    ban = room_model.Ban(user_id=user_id, room_id=room_id, start_time=current_time_naive, end_time=end_time)
    
    db.add(ban)
    await db.commit()
    
    return {"message": f"User {user_id} has been muted for {duration_minutes} minutes"}


@router.delete('/un-mute-user')
async def un_mute_user(user_id: int, room_id: int, 
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Un-mute a user in a specific room.

    Parameters:
    user_id (int): The ID of the user to be un-muted.
    room_id (int): The ID of the room where the user is to be un-muted.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (user_model.User): The current user making the request.

    Returns:
    dict: A dictionary containing a success message.

    Raises:
    HTTPException: If the room does not exist, the user is not a moderator or owner of the room, or the user is not muted in the room.
    """
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    room_query = select(room_model.Rooms).where(room_model.Rooms.id == room_id)
    room_result = await db.execute(room_query)
    room = room_result.scalar_one_or_none()
=======
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        if duration_minutes < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Duration must be a positive integer.")

        current_time_utc = datetime.now(pytz.timezone('UTC'))
        current_time_naive = current_time_utc.replace(tzinfo=None)

        room_get = await get_room_by_id(room_id, db)
        if not room_get:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID: {room_id} not found")

        if current_user.id != room_get.owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not the owner of this room.")


        role_room = select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room_id,
                                                    room_model.RoleInRoom.user_id == current_user.id)
        result = await db.execute(role_room)
        role_in_room = result.scalar_one_or_none()

        if not role_in_room or role_in_room.role != "moderator":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not the owner or a moderator of this room.")

        end_time = current_time_naive + timedelta(minutes=duration_minutes)
        ban = room_model.Ban(user_id=user_id, room_id=room_id, start_time=current_time_naive, end_time=end_time)

        db.add(ban)
        await db.commit()

        return {"message": f"User {user_id} has been muted for {duration_minutes} minutes"}

    except Exception as e:
        logger.error(f"An error occurred while muting user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.delete('/un-mute-user')
async def un_mute_user(user_id: UUID, room_id: UUID,
                    db: AsyncSession = Depends(get_async_session), 
                    current_user: user_model.User = Depends(oauth2.get_current_user)):

    # Check if the role exists and is a moderator or owner
    if current_user.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    room = await get_room_by_id(room_id, db)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")

    if current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of this room.")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
    role_room = select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room_id,
                                                room_model.RoleInRoom.user_id == current_user.id)
    result = await db.execute(role_room)
    role_in_room = result.scalar_one_or_none()

<<<<<<< HEAD
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")
        
    # Check if the role exists and is a moderator or owner
    if (room.owner != current_user.id and (role_in_room is None or role_in_room.role != "moderator")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner or a moderator of this room.")

    
    delete_ban = select(room_model.Ban).where(room_model.Ban.user_id == user_id, room_model.Ban.room_id == room_id)
    result = await db.execute(delete_ban)
    existing_ban = result.scalar()
=======
    if not role_in_room or role_in_room.role != "moderator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner or a moderator of this room.")

    delete_ban = await db.execute(select(room_model.Ban).where(
        room_model.Ban.user_id == user_id, room_model.Ban.room_id == room_id))
    existing_ban = delete_ban.scalar_one_or_none()
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    
    if not existing_ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {user_id} is not muted in room {room_id}")
        
    await db.delete(existing_ban)
    await db.commit()
    
    return {"message": f"User {user_id} has been un-muted in room {room_id}"}