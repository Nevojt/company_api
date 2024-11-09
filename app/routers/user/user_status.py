from select import select
from uuid import UUID
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from _log_config.log_config import get_logger
from app.database.async_db import get_async_session
from app.models import user_model
from app.schemas import user


user_status_logger = get_logger('user_status', 'user_status.log')
router = APIRouter(
    prefix="/user_status",
    tags=['User Status'],
)


@router.get("/")
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



@router.put("/{user_id}", status_code=status.HTTP_200_OK)
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