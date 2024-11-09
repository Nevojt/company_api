from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from uuid import UUID
from _log_config.log_config import get_logger
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.sql.expression import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.models import user_model, following_model
from app.schemas import following
from app.database.async_db import get_async_session

following_logger = get_logger('following', 'following.log')

router = APIRouter(
    prefix="/followers",
    tags=["Followers"],
)


@router.get("/search/{substring}", response_model=List[following.Follower])
async def search_users(
    substring: str,
    current_user: user_model.User = Depends(oauth2.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Search for users that the current user is following and match the given substring.

    Parameters:
    substring (str): The substring to search for in the user names.
    current_user (user_model.User): The current user making the request. This parameter is obtained through dependency injection.
    db (AsyncSession): The asynchronous database session. This parameter is obtained through dependency injection.

    Returns:
    List[following.Follower]: A list of Follower objects representing the users that match the search criteria.
    Each Follower object contains the user's id, user_name, avatar, and the timestamp of when the user was followed.
    """
    # Створення шаблону для пошуку
    pattern = f"%{substring.lower()}%"
    try:
        # Побудова асинхронного запиту
        query = (
            select(
                user_model.User.id,
                user_model.User.user_name.label("user_name"),
                user_model.User.avatar,
                following_model.Following.following_at.label("following_at")
            )
            .join(following_model.Following, user_model.User.id == following_model.Following.follower_id)
            .where(following_model.Following.user_id == current_user.id)
            .where(func.lower(user_model.User.user_name).like(pattern))
        )

        # Виконання запиту та отримання результатів
        result = await db.execute(query)
        users = result.fetchall()

        # Формування списку результатів
        users_info = [
            following.Follower(
                id=user.id,
                user_name=user.user_name,
                avatar=user.avatar,
                following_at=user.following_at
            ) for user in users
        ]

        return users_info
    except Exception as e:
        following_logger.error(f"Error searching for users following {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/following", response_model=List[following.Follower])
async def get_following_users(
        db: AsyncSession = Depends(get_async_session),
        current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Retrieve a list of users that the current user is following.

    Parameters:
    db (AsyncSession): An asynchronous database session provided by the dependency injection.
    current_user (user_model.User): The current user making the request, obtained through dependency injection.

    Returns:
    List[following.Follower]: A list of Follower objects representing the users the current user is following.
    Each Follower object contains the user's id, user_name, avatar, and the timestamp of when the user was followed.
    """
    # Get users following
    try:
        query = (
            select(
                user_model.User.id,
                user_model.User.user_name.label("user_name"),
                user_model.User.avatar,
                following_model.Following.following_at
            )
            .join(following_model.Following, user_model.User.id == following_model.Following.follower_id)
            .where(following_model.Following.user_id == current_user.id)
        )

        result = await db.execute(query)
        following_users = result.all()

        # Convert the query result to a list of Follower objects
        return [following.Follower(**row._asdict()) for row in following_users]
    except Exception as e:
        following_logger.error(f"Error retrieving following users for {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/add/{follower_id}")
async def add_follower(follower_id: UUID,
                       db: AsyncSession = Depends(get_async_session),
                       current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Adds a follower for the current user.

    Parameters:
    follower_id (int): The id of the user to be followed.
    db (AsyncSession): An asynchronous database session provided by the dependency injection.
    current_user (user_model.User): The current user making the request, obtained through dependency injection.

    Returns:
    dict: A dictionary containing a success message.
    """
    try:
        if not current_user.verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User must be verified to follow other users")

        if current_user.id == follower_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Cannot follow yourself")

        #
        query = select(
            user_model.User,
            following_model.Following
        ).outerjoin(
            following_model.Following,
            (following_model.Following.follower_id == follower_id) &
            (following_model.Following.user_id == current_user.id)
        ).where(user_model.User.id == follower_id)

        result = await db.execute(query)
        result = result.one_or_none()

        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or other error")

        user, existing_follower = result

        if existing_follower:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already following this user")

        #
        new_follower = following_model.Following(
            follower_id=follower_id,
            user_id=current_user.id
        )
        db.add(new_follower)
        await db.commit()

        return {"message": "Successfully followed user"}
    except Exception as e:
        following_logger.error(f"Error adding follower for {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/delete")
async def delete_follower(followers_id: List[UUID],
                          db: AsyncSession = Depends(get_async_session),
                          current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        if not followers_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No followers specified for deletion")

        delete_stmt = (
            delete(following_model.Following)
            .where(following_model.Following.follower_id.in_(followers_id))
            .where(following_model.Following.user_id == current_user.id)
        )

        result = await db.execute(delete_stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No matching followers found to delete")

        return {"message": f"Successfully deleted {result.rowcount} follower(s)"}
    except Exception as e:
        following_logger.error(f"Error deleting followers: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))