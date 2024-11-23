
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.async_db import get_async_session
from datetime import datetime


from app.models import user_model
from app.schemas import firebase
from app.auth import oauth2
from _log_config.log_config import get_logger

firebase_logger = get_logger('firebase', 'user_tokens.log.log')

router = APIRouter(
    prefix="/firebase",
    tags=["Notification Token FCM"]
)


@router.post("/write_token")
async def add_or_update_fcm_token(data: firebase.TokenFCM,
                                  db: AsyncSession = Depends(get_async_session),
                                  current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    This function adds or updates the FCM token of a user.
    """
    # Find or create the user in the database
    try:
        result_query = await db.execute(select(user_model.FCMTokenManager).where(
                                         user_model.FCMTokenManager.user_id==current_user.id,
                                            user_model.FCMTokenManager.platform==data.platform))
        fcm_token_manager = result_query.scalar_one_or_none()

        if fcm_token_manager:
            fcm_token_manager.fcm_token = data.fcm_token
            fcm_token_manager.updated_at = datetime.now()
        else:
            fcm_token_manager = user_model.FCMTokenManager(user_id=current_user.id,
                                                          platform=data.platform,
                                                          fcm_token=data.fcm_token,
                                                          created_at=datetime.now(),
                                                          updated_at=datetime.now())
            db.add(fcm_token_manager)
        await db.commit()
        return fcm_token_manager
    except Exception as e:
        firebase_logger.error(f"Error occurred while adding or updating FCM token: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error occurred while adding or updating FCM token")