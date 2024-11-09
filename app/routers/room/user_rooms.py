import logging
from uuid import UUID
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy import asc
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2

from app.database.async_db import get_async_session
from app.models import user_model, room_model
from app.schemas import room as room_schema
from app.routers.AI.hello import system_notification_change_owner
from app.settings.get_info import get_count_messages, get_count_users

from app.config.start_schema import start_app

logging.basicConfig(filename='_log/user_rooms.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/user_rooms',
    tags=['User rooms'],
)
hell = start_app.default_room_name


@router.get("/", response_model=List[room_schema.RoomFavorite])
async def get_user_rooms(db: AsyncSession = Depends(get_async_session),
                         current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.
    """
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        # Fetch rooms
        rooms = await db.execute(select(
            room_model.Rooms,
            room_model.RoomsManagerMyRooms.favorite.label('favorite')
        ).outerjoin(
            room_model.RoomsManagerMyRooms,
            (room_model.RoomsManagerMyRooms.room_id == room_model.Rooms.id) & (room_model.RoomsManagerMyRooms.user_id == current_user.id)
        ).where(room_model.Rooms.name_room != hell, room_model.Rooms.owner == current_user.id)
        .order_by(asc(room_model.Rooms.id)))
        rooms = rooms.all()

        # Fetch messages count
        messages_count = await get_count_messages(db)

        # Fetch users count
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

        # Sorting the rooms by 'favorite' flag
        rooms_info.sort(key=lambda x: x.favorite, reverse=True)

        return rooms_info
    except Exception as e:
        logger.error(f"Error retrieving user rooms: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")

    
    
    
    
@router.put("/{room_id}")  # Assuming you're using room_id
async def update_room_favorite(room_id: UUID,
                                favorite: bool, 
                                db: AsyncSession = Depends(get_async_session),
                                current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Updates the favorite status of a room for a specific user.

    Args:
        room_id (int): The ID of the room to update.
        favorite (bool): The new favorite status for the room.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (user_model.User, optional): The current user. Defaults to Depends(oauth2.get_current_user).

    Raises:
        HTTPException: If the user is blocked or not verified.
        HTTPException: If the room is not found.

    Returns:
        dict: A dictionary containing the room ID and the new favorite status.
    """
    try:
        if current_user.blocked: # or not current_user.verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Access denied for user {current_user.id}")

        # Fetch room
        room = await get_room_for_user(current_user.id, room_id, db)

        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

        # Check if there is already a favorite record
        favorite_record_query = await db.execute(select(room_model.RoomsManagerMyRooms).where(
            room_model.RoomsManagerMyRooms.room_id == room_id,
            room_model.RoomsManagerMyRooms.user_id == current_user.id
        ))
        favorite_record = favorite_record_query.scalar_one_or_none()

        # Update if exists, else create a new record
        if favorite_record:
            favorite_record.favorite = favorite
        else:
            new_favorite = room_model.RoomsManagerMyRooms(
                user_id=current_user.id,
                room_id=room_id,
                favorite=favorite
            )
            db.add(new_favorite)

        await db.commit()
        return {"room_id": room_id, "favorite": favorite}
    except Exception as e:
        logger.error(f"Error updating room favorite: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")
    


@router.put("/change-owner/{room_id}")
async def change_room_owner(room_id: UUID,
                            new_owner_id: UUID,
                            db: AsyncSession = Depends(get_async_session),
                            current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        room_query = await get_room_for_user(current_user.id, room_id, db)

        if room_query is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

        if room_query.block:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Room is blocked")

        user_query = await db.execute(select(user_model.User).where(user_model.User.id == new_owner_id))
        new_user = user_query.scalar_one_or_none()

        if new_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not new_user.verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")

        room_query.owner = new_owner_id
        db.add(room_query)
        await db.commit()

        role_query = await db.execute(select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room_id))
        role_query = role_query.scalar_one_or_none()


        role_query.user_id = new_owner_id
        db.add(role_query)
        await db.commit()

        message = f"Room {room_query.name_room} is now owned by {new_user.user_name}"

        await system_notification_change_owner(new_owner_id, message)

        return {"room_id": room_id, "new_owner_id": new_owner_id}
    except Exception as e:
        logger.error(f"Error changing room owner: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")


async def get_room_for_user(user_id: UUID, room_id: UUID,
                            db: AsyncSession):
    try:
        room_query = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id,
                                                                     room_model.Rooms.owner == user_id))
        room = room_query.scalar_one_or_none()
        return room
    except Exception as e:
        print(f"Error getting room for user: {e}")
        logger.error(f"Error getting room for user: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Room not found")