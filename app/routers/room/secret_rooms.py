<<<<<<< HEAD
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

from app.models import room_model, user_model, messages_model
from app.schemas import room as room_schema

=======
from _log_config.log_config import get_logger
from uuid import UUID
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.config.start_schema import start_app
from app.database.async_db import get_async_session

from app.models import room_model, user_model
from app.routers.reports.functions_report import get_room_id
from app.schemas import room as room_schema

from app.settings.get_info import has_verified_or_blocked_user, get_count_users, get_count_messages, get_room_by_id

logger = get_logger('secret_rooms', 'secret_rooms.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
router = APIRouter(
    prefix='/secret',
    tags=['Secret Rooms'],
)



@router.get("/")
<<<<<<< HEAD
async def get_user_rooms_secret(db: Session = Depends(get_db), 
                              current_user: user_model.User = Depends(oauth2.get_current_user)) -> List[room_schema.RoomFavorite]:
=======
async def get_user_rooms_secret(db: AsyncSession = Depends(get_async_session),
                                current_user: user_model.User = Depends(oauth2.get_current_user)) -> List[room_schema.RoomFavorite]:
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Retrieve a list of rooms accessible by the current user, along with their associated message and user counts.

    Args:
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[room_schema.RoomBase]: A list of room information, including name, image, user count, message count, and creation date.
    """
<<<<<<< HEAD
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
    # Fetch room IDs for the current user
    user_room_ids = db.query(room_model.RoomsManager.room_id).filter(room_model.RoomsManager.user_id == current_user.id).all()
    user_room_ids = [str(room_id[0]) for room_id in user_room_ids]  # Extracting room IDs from the tuple

    # Query rooms details based on user_room_ids, excluding 'Hell'
    rooms = db.query(room_model.Rooms, room_model.RoomsManager.favorite
                     ).filter(room_model.Rooms.id.in_(user_room_ids), 
                    room_model.Rooms.name_room != 'Hell',
                    room_model.Rooms.secret_room == True,
                    room_model.RoomsManager.room_id == room_model.Rooms.id,  # Ensure the mapping between Rooms and RoomsManager
                    room_model.RoomsManager.user_id == current_user.id  # Ensure we're getting the favorite status for the current user
    ).all()

    # Fetch message count for each user-associated room
    messages_count = db.query(
        messages_model.Socket.rooms, 
        func.count(messages_model.Socket.id).label('count')
    ).group_by(messages_model.Socket.rooms).filter(messages_model.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        user_model.User_Status.name_room, 
        func.count(user_model.User_Status.id).label('count')
    ).group_by(user_model.User_Status.name_room).filter(user_model.User_Status.name_room != 'Hell').all()

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
=======
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
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

        

@router.put('/{room_id}')
<<<<<<< HEAD
async def secret_room_update(room_id: int,
                            favorite: bool,
                            db: Session = Depends(get_db), 
=======
async def secret_room_update(room_id: UUID,
                            favorite: bool,
                            db: AsyncSession = Depends(get_async_session),
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
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
<<<<<<< HEAD
    if current_user.blocked == True or current_user.verified == False:
=======
    if await has_verified_or_blocked_user(current_user):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")

    # Fetch room
<<<<<<< HEAD
    room = db.query(room_model.Rooms).filter(room_model.Rooms.id == room_id, room_model.Rooms.owner == current_user.id).first()
=======
    room = await get_room_by_id(room_id, db)

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    # Check if there is already a favorite record
<<<<<<< HEAD
    favorite_record = db.query(room_model.RoomsManager).filter(
        room_model.RoomsManager.room_id == room_id,
        room_model.RoomsManager.user_id == current_user.id
    ).first()
=======
    favorite_record = await db.execute(select(room_model.RoomsManagerSecret).where(
        room_model.RoomsManagerSecret.room_id == room_id,
        room_model.RoomsManagerSecret.user_id == current_user.id
    ))
    favorite_record = favorite_record.scalar_one_or_none()
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

    # Update if exists, else create a new record
    if favorite_record:
        favorite_record.favorite = favorite
    else:
<<<<<<< HEAD
        new_favorite = room_model.RoomsManager(
=======
        new_favorite = room_model.RoomsManagerSecret(
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
            user_id=current_user.id, 
            room_id=room_id, 
            favorite=favorite
        )
        db.add(new_favorite)

<<<<<<< HEAD
    db.commit()
=======
    await db.commit()
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    return {"room_id": room_id, "favorite": favorite}
