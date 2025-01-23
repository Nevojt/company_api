<<<<<<< HEAD
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database.database import get_db
from app.models import messages_model, user_model
from app.schemas import room
=======

from _log_config.log_config import get_logger
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.future import select
from typing import List

from app.database.async_db import get_async_session
from app.models import messages_model, user_model
from app.schemas import room
from app.config.start_schema import start_app

from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger('count', 'count_users_messages.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

router = APIRouter(
    prefix="/count",
    tags=['Count']
    )


<<<<<<< HEAD

@router.get("/messages", response_model=List[room.CountMessages])
async def get_count_messages(db: Session = Depends(get_db)):
=======
hell = start_app.default_room_name

@router.get("/messages", response_model=List[room.CountMessages])
async def get_count_messages(db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Get the count of messages in each room.

    Parameters:
        db (Session): The database session.

    Returns:
        List[schemas.CountMessages]: A list of count messages.

    Raises:
        HTTPException: If no messages found.
    """
<<<<<<< HEAD
    query_result = db.query(messages_model.Socket.rooms, func.count(messages_model.Socket.id).label('count')).group_by(
        messages_model.Socket.rooms).filter(messages_model.Socket.rooms != 'Hell').all()
    
    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No messages found in any room.")
    counts = [{"rooms": rooms, "count": count} for rooms, count in query_result]

    return counts
=======
    try:
        query_result = await db.execute(select(
            messages_model.ChatMessages.rooms, func.count(messages_model.ChatMessages.id).label('count')).group_by(
            messages_model.ChatMessages.rooms).filter(messages_model.ChatMessages.rooms != hell))
        result = query_result.scalars().all()

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No messages found in any room.")
        counts = [{"rooms": rooms, "count": count} for rooms, count in query_result]

        return counts
    except Exception as e:
        logger.error(f"Error in get_count_messages: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824



@router.get("/users", response_model=List[room.CountUsers])
<<<<<<< HEAD
async def get_count_users(db: Session = Depends(get_db)):
=======
async def get_count_users(db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Get the count of users in each room.

    Parameters:
        db (Session): The database session.

    Returns:
        List[schemas.CountUsers]: A list of count users.

    Raises:
        HTTPException: If no users found.
    """
<<<<<<< HEAD
    query_result = db.query(user_model.User_Status.name_room, func.count(user_model.User_Status.id).label('count')).group_by(
        user_model.User_Status.name_room).filter(user_model.User_Status.name_room != 'Hell').all()
    
    if not query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No users found in any room.")
    counts = [{"rooms": name_room, "count": count} for name_room, count in query_result]
    
    return counts
=======
    try:
        query_result = await db.execute(select(
            user_model.UserStatus.name_room, func.count(user_model.UserStatus.id).label('count')).group_by(
            user_model.UserStatus.name_room).filter(user_model.UserStatus.name_room != hell))
        result = query_result.scalars().all()

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No users found in any room.")
        counts = [{"rooms": name_room, "count": count} for name_room, count in query_result]

        return counts
    except Exception as e:
        logger.error(f"Error in get_count_users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
