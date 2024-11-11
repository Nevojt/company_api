from _log_config.log_config import get_logger
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.async_db import get_async_session
from app.auth import oauth2
from app.models import user_model, room_model
from uuid import UUID

logger = get_logger('role_in_room', 'role_in_room.log')

router = APIRouter(
    prefix="/role-in-room",
    tags=['Role In Rooms']
)


@router.get('/')
async def list_role_in_room(db: AsyncSession = Depends(get_async_session), 
                          current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Retrieves the role in room for the authenticated user.

    Parameters:
    db (AsyncSession): The database session for asynchronous operations.
    current_user (user_model.User): The current user making the request.

    Returns:
    List[room_model.RoleInRoom]: A list of RoleInRoom objects for the specified user.

    Raises:
    HTTPException: If the user with the given ID is not found in the database.
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only admins can access this endpoint")
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        role_query = select(room_model.RoleInRoom).where(room_model.RoleInRoom.user_id == current_user.id)
        result = await db.execute(role_query)
        role_in_room = result.scalars().all()

        if not role_in_room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID: {current_user.id} not found")

        return role_in_room
    except Exception as e:
        logger.error(f"Failed to retrieve role in room for user: {current_user.id}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to retrieve role in room: {e}")

# Get info user role admin option
@router.get('/admin/{user_id}')
async def list_role_in_room_admin(user_id: UUID,
                                  db: AsyncSession = Depends(get_async_session),
                                  current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Admin option to get role in room for a specific user.

    Parameters:
    user_id (int): The ID of the user whose role in room needs to be fetched.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (user_model.User): The current user making the request.

    Returns:
    List[room_model.RoleInRoom]: A list of RoleInRoom objects for the specified user.

    Raises:
    HTTPException: If the user with the given ID is not found in the database.
    HTTPException: If the current user is not an admin.
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Only admins can access this endpoint")

        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        role_query = select(room_model.RoleInRoom).where(room_model.RoleInRoom.user_id == user_id)
        result = await db.execute(role_query)
        role_in_room = result.scalars().all()

        if not role_in_room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID: {user_id} not found")
        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        return role_in_room
    except Exception as e:
        logger.error(f"Failed to retrieve role in room for user: {user_id}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to retrieve role in room: {e}")

@router.post('/to_moderator/{user_id}')
async def to_moderator(user_id: UUID, room_id: UUID,
                       db: AsyncSession = Depends(get_async_session),
                       current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Endpoint to toggle a user's role from moderator to regular user or vice versa in a specific room.
    Only the room owner can perform this action.

    Parameters:
    user_id (int): The ID of the user whose role needs to be toggled.
    room_id (int): The ID of the room where the role needs to be toggled.
    db (AsyncSession): The database session for asynchronous operations.
    current_user (user_model.User): The current user making the request.

    Returns:
    dict: A dictionary with a success message indicating the role change.

    Raises:
    HTTPException: If the current user is not the owner of the room.
    """
    try:

        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        # Check if the current user is the owner of the room
        room_owner_query = select(room_model.Rooms).where(room_model.Rooms.owner == current_user.id,
                                                      room_model.Rooms.id == room_id)
        result = await db.execute(room_owner_query)
        room_owner = result.scalar_one_or_none()

        user_verification = select(user_model.User).where(user_model.User.id == user_id)
        result = await db.execute(user_verification)
        user_verification = result.scalar_one_or_none()

        if user_verification.verified is False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with ID: {user_id} not verification")

        if room_owner is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this room.")

        # Request to check the existing user role in the room
        role_query = select(room_model.RoleInRoom).where(room_model.RoleInRoom.user_id == user_id,
                                                     room_model.RoleInRoom.room_id == room_id)
        result = await db.execute(role_query)
        role_in_room = result.scalar_one_or_none()

        if role_in_room is None:
            # If the role does not exist, add the user as a moderator
            add_role_moderator = room_model.RoleInRoom(user_id=user_id, room_id=room_id, role="moderator")
            db.add(add_role_moderator)
            await db.commit()
            return {"msg": f"User with ID: {user_id} is now a moderator in room with ID: {room_id}"}
        else:
            # If the role exists, delete it
            await db.delete(role_in_room)
            await db.commit()
            return {"msg": f"User with ID: {user_id} is no longer a moderator in room with ID: {room_id}"}
    except Exception as e:
        logger.error(f"Failed to toggle role in room for user: {user_id}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to toggle role in room: {e}")
    