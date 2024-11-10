
from fastapi import status, HTTPException, Depends, APIRouter

from typing import List
from app.database.async_db import get_async_session
from app.models import messages_model, user_model
from app.schemas import private
from app.auth import oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from _log_config.log_config import get_logger

private_logger = get_logger('private', 'private.log')
router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)


@router.get("/users-list", response_model=List[private.PrivateInfoRecipient])
async def get_private_recipient(
    current_user: user_model.User = Depends(oauth2.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Fetches a list of private message recipients and senders for the current user.
    """
    result = []
    try:
        # Query for recipients and senders
        messages_query = select(messages_model.PrivateMessage, user_model.User).join(
            user_model.User, messages_model.PrivateMessage.receiver_id == user_model.User.id
        ).filter(
            (messages_model.PrivateMessage.sender_id == current_user.id) |
            (messages_model.PrivateMessage.receiver_id == current_user.id)
        )

        # Execute query asynchronously
        messages = await db.execute(messages_query)
        messages = messages.all()

        # Filter and map results asynchronously
        users_info = {}
        for message, user in messages:
            other_user_id = message.sender_id if message.receiver_id == current_user.id else message.receiver_id
            other_user_query = select(user_model.User).filter(user_model.User.id == other_user_id)
            other_user_result = await db.execute(other_user_query)
            other_user = other_user_result.scalar_one_or_none()

            if other_user:
                is_read = message.is_read if message.receiver_id == current_user.id else False

                # Update or add the user info
                if other_user_id not in users_info or not users_info[other_user_id].is_read:
                    users_info[other_user_id] = private.PrivateInfoRecipient(
                        receiver_id=other_user_id,
                        receiver_name=other_user.user_name,
                        receiver_avatar=other_user.avatar,
                        verified=other_user.verified,
                        is_read=is_read
                    )

        # Convert to list and sort
        result = list(users_info.values())
        result.sort(key=lambda x: x.is_read, reverse=True)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Sorry, no recipients or senders found.")
    except Exception as e:
        private_logger.error(f"Error retrieving recipients: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    return result
