import logging
from uuid import UUID
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.config.start_schema import start_app
from app.database.async_db import get_async_session

from app.models import room_model, user_model
from app.schemas import room as room_schema

from app.settings.get_info import has_verified_or_blocked_user, get_count_users, get_count_messages


logging.basicConfig(filename='_log/secret_rooms.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix='/secret',
    tags=['Secret Rooms'],
)



@router.get("/")
async def get_user_rooms_secret(db: AsyncSession = Depends(get_async_session),
                                current_user: user_model.User = Depends(oauth2.get_current_user)) -> List[room_schema.RoomFavorite]:
    """
    Retrieve a list of rooms accessible by the current user, along with their associated message and user counts.

    Args:
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[room_schema.RoomBase]: A list of room information, including name, image, user count, message count, and creation date.
    """
    hell = start_app.default_room_name
    if await has_verified_or_blocked_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")

    try:
        user_room_q = await db.execute(select(room_model.RoomsManagerSecret.room_id).where(
            room_model.RoomsManagerSecret.user_id == current_user.id))
        user_room_ids_result = user_room_q.all()

        user_room_ids = [str(room_id[0]) for room_id in user_room_ids_result]  # Extracting room IDs from the tuple

        rooms_query = await db.execute(select(room_model.Rooms, room_model.RoomsManagerSecret.favorite
                         ).where(room_model.Rooms.id.in_(user_room_ids),
                                  room_model.Rooms.name_room != hell,
                                  room_model.Rooms.secret_room,
                                  room_model.RoomsManagerSecret.room_id == room_model.Rooms.id,
                                  room_model.RoomsManagerSecret.user_id == current_user.id
                                  ))
        rooms = rooms_query.all()

        # Using separate queries for counting messages and users
        messages_count = await get_count_messages(db)

        users_count = await get_count_users(db)

        rooms_info = []
        for room, favorite in rooms:

            room_info = room_schema.RoomFavorite(
                id=room.id,
                owner=room.owner,
                name_room=room.name_room,
                image_room=room.image_room,
                count_users=next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
                count_messages=next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
                created_at=room.created_at,
                secret_room=room.secret_room,
                favorite=favorite if favorite is not None else False,
                block=room.block
            )
            rooms_info.append(room_info)
            rooms_info.sort(key=lambda x: x.favorite, reverse=True)

        return rooms_info
    except Exception as e:
        logger.error(f"Error occurred while retrieving rooms info: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Bad request")

        

@router.put('/{room_id}')
async def secret_room_update(room_id: UUID,
                            favorite: bool,
                            db: AsyncSession = Depends(get_async_session),
                            current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Updates the favorite status of a secret room for a specific user.

    Args:
        room_id (int): The ID of the room to update.
        favorite (bool): The new favorite status for the room.
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.

    Returns:
        dict: A dictionary containing the room ID and the updated favorite status.

    Raises:
        HTTPException: If the user is blocked or not verified, a 403 Forbidden error is raised.
        HTTPException: If the room is not found, a 404 Not Found error is raised.
    """
    if await has_verified_or_blocked_user(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")

    # Fetch room
    room_query = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id,
                                                     room_model.Rooms.owner == current_user.id))
    room = room_query.scalar_one_or_none()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    # Check if there is already a favorite record
    favorite_record = await db.execute(select(room_model.RoomsManagerSecret).where(
        room_model.RoomsManagerSecret.room_id == room_id,
        room_model.RoomsManagerSecret.user_id == current_user.id
    ))
    favorite_record = favorite_record.scalar_one_or_none()

    # Update if exists, else create a new record
    if favorite_record:
        favorite_record.favorite = favorite
    else:
        new_favorite = room_model.RoomsManagerSecret(
            user_id=current_user.id, 
            room_id=room_id, 
            favorite=favorite
        )
        db.add(new_favorite)

    await db.commit()
    return {"room_id": room_id, "favorite": favorite}
