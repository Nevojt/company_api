from typing import List
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.sql.expression import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.models import user_model, following_model
from app.schemas import following
from app.database.async_db import get_async_session
from ...database.database import get_db

router = APIRouter(
    prefix="/followers",
    tags=["Followers"],
)


@router.get("/search/{substring}", response_model=List[following.Follower])
def search_users(substring: str,
                 current_user: user_model.User = Depends(oauth2.get_current_user),
                 db: Session = Depends(get_db)):
    """
    Search for users that the current user is following and match the given substring.

    Parameters:
    substring (str): The substring to search for in the user names.
    current_user (user_model.User): The current user making the request. This parameter is obtained through dependency injection.
    db (Session): The database session. This parameter is obtained through dependency injection.

    Returns:
    List[following.Follower]: A list of Follower objects representing the users that match the search criteria.
    Each Follower object contains the user's id, user_name, avatar, and the timestamp of when the user was followed.
    """
    # Search for users
    pattern = f"%{substring.lower()}%"

    # Search for users that the current user is following and match the substring
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

    result = db.execute(query)
    users = result.all()

    users_info = []
    for user in users:
        user_info = {
            "id": user.id,
            "user_name": user.user_name,
            "avatar": user.avatar,
            "following_at": user.following_at
        }
        users_info.append(following.Follower(**user_info))

    return users_info


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

@router.post("/add")
async def add_follower(follower_id: int, 
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
    if current_user.verified is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User must be verified to follow other users")
    
    if current_user.id == follower_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

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

@router.delete("/delete")
async def delete_follower(followers_id: List[int], 
                          db: AsyncSession = Depends(get_async_session), 
                          current_user: user_model.User = Depends(oauth2.get_current_user)):
    
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching followers found to delete")

    return {"message": f"Successfully deleted {result.rowcount} follower(s)"}