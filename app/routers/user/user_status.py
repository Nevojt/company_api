<<<<<<< HEAD
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ...auth import oauth2
from app.database.database import get_db
from app.models import user_model
from app.schemas import user

=======

from uuid import UUID
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from _log_config.log_config import get_logger
from app.database.async_db import get_async_session
from app.models import user_model
from app.schemas import user


user_status_logger = get_logger('user_status', 'user_status.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
router = APIRouter(
    prefix="/user_status",
    tags=['User Status'],
)


@router.get("/")
<<<<<<< HEAD
async def get_posts(db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    """
    Get a list of all user status.

    Args:
        db (Session, optional): The database session object.

    Returns:
        List[schemas.UserStatus]: A list of user status objects.
    """
    posts = db.query(user_model.User_Status).all()
    return posts


@router.get("/{user_name}")
async def get_post(user_name: str, db: Session = Depends(get_db)):  # , current_user: int = Depends(oauth2.get_current_user)
    """
    Get a single user status by their username.

    Args:
        user_name (str): The username of the user whose status is to be retrieved.
        db (Session, optional): The database session object.

    Raises:
        HTTPException: A 404 NOT FOUND error is raised if no user status is found for the given username.

    Returns:
        List[schemas.UserStatus]: A list of user status objects, or an empty list if no user status is found.
    """
    post = db.query(user_model.User_Status).filter(user_model.User_Status.user_name == user_name).all()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with user_name: {user_name} not found")
    return post

# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserStatusPost)
# async def create_posts(post: schemas.UserStatusCreate, db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)

    
#     # print(current_user.user_name)
#     post = user_model.User_Status(**post.dict())
#     db.add(post)
#     db.commit()
#     db.refresh(post)    
#     return post
=======
async def get_posts(db: AsyncSession = Depends(get_async_session)):
    try:
        status_query = await db.execute(select(user_model.UserStatus))
        status_return = status_query.scalars().all()
        return status_return
    except Exception as e:
        user_status_logger.error(f"An error occurred while reading the user statuses: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while reading the user statuses")


@router.get("/{user_name}")
async def get_status_by_name(user_name: str,
                            db: AsyncSession = Depends(get_async_session)):  # , current_user: int = Depends(oauth2.get_current_user)
    try:
        user_status_query = await db.execute(select(user_model.UserStatus).where(user_model.UserStatus.user_name == user_name))
        user_status = user_status_query.scalar_one_or_none()

        if not user_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with user_name: {user_name} not found")
        return user_status
    except Exception as e:
        user_status_logger.error(f"An error occurred while reading the user status by name: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824



@router.put("/{user_id}", status_code=status.HTTP_200_OK)
<<<<<<< HEAD
def update_post(user_id: int, update_post: user.UserStatusUpdate, db: Session = Depends(get_db)): # , current_user: int = Depends(oauth2.get_current_user)
    """
    Updates the status of a user post based on the provided user ID and updated post details.

    Args:
        user_id (int): The ID of the user whose post is to be updated.
        update_post (schemas.UserStatusUpdate): The updated post details.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 404 error if no post is found for the given user ID.

    Returns:
        user_model.User_Status: The updated user post after the changes have been committed to the database.
    """
    
    post_query = db.query(user_model.User_Status).filter(user_model.User_Status.user_id == user_id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with user_id: {user_id} not found")
    
    post_query.update(update_post.model_dump(), synchronize_session=False)
    
    db.commit()
    return post_query.first()
=======
async def update_status(user_id: UUID,
                update_post: user.UserStatusUpdate,
                db: AsyncSession = Depends(get_async_session)): # , current_user: int = Depends(oauth2.get_current_user)

    try:
        status_query = await db.execute(select(user_model.UserStatus).where(user_model.UserStatus.user_id == user_id))
        user_status = status_query.scalar_one_or_none()

        if user_status is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with user_id: {user_id} not found")

        user_status.name_room = update_post.name_room
        user_status.status = update_post.status

        await db.commit()
    except Exception as e:
        user_status_logger.error(f"An error occurred while updating the user status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return {'user_status': "Update"}
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
