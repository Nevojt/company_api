<<<<<<< HEAD
import logging
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.database import get_db
from app.database.async_db import get_async_session
from app.models import messages_model, user_model
from app.schemas import private
from app.config.crypto_encrypto import async_decrypt
from app.auth import oauth2

=======

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
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)

<<<<<<< HEAD
logging.basicConfig(filename='_log/private.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@router.get("/{user_id}", response_model=List[private.PrivateInfoRecipient])
async def get_private_recipient(user_id: int, db: Session = Depends(get_db)):
    """
    Get a list of recipients in a private chat.

    Args:
        user_id (int): The ID of the user whose recipients you want to retrieve.
        db (Session): The database session.

    Returns:
        List[schemas.PrivateInfoRecipient]: A list of recipients in the private chat.

    Raises:
        HTTPException: If the user does not have any recipients or senders in the chat.
    """
    try:
        # Query for recipients and senders
        messages_query = db.query(messages_model.PrivateMessage, user_model.User).join(
            user_model.User, messages_model.PrivateMessage.receiver_id == user_model.User.id
        ).filter(
            (messages_model.PrivateMessage.sender_id == user_id) | (messages_model.PrivateMessage.receiver_id == user_id)
        )

        # Execute query
        messages = messages_query.all()

        # Filter and map results
        users_info = {}
        for message, user in messages:
            other_user_id = message.sender_id if message.receiver_id == user_id else message.receiver_id
            other_user = db.query(user_model.User).filter(user_model.User.id == other_user_id).first()

            # Determine if the message is read or not
            is_read = message.is_read if message.receiver_id == user_id else False

            # Update or add the user info
            if other_user_id not in users_info or not users_info[other_user_id].is_read:
                users_info[other_user_id] = private.PrivateInfoRecipient(
                    receiver_id=other_user_id,
                    receiver_name=other_user.user_name,
                    receiver_avatar=other_user.avatar,
                    verified=other_user.verified,
                    is_read=is_read
                )

        # Convert to list
        result = list(users_info.values())

        # Sort the list so that read messages (is_read = True) come first
=======

@router.get("/users-list", response_model=List[private.PrivateInfoRecipient])
async def get_private_recipient(
    current_user: user_model.User = Depends(oauth2.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Fetches a list of private message recipients and senders for the current user.
    """

    try:
        # Query for recipients and senders
        result = []
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
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        result.sort(key=lambda x: x.is_read, reverse=True)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Sorry, no recipients or senders found.")
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"Error creating {e}", exc_info=True)
    return result


@router.get("/message_id/{message_id}")
async def private_fetch_message_by_id(message_id: int,
                                    session: AsyncSession = Depends(get_async_session),
                                    current_user: user_model.User = Depends(oauth2.get_current_user)):

    # Formulate the query
    message_query = select(
        messages_model.PrivateMessage, 
        user_model.User
    ).outerjoin(
        user_model.User, messages_model.PrivateMessage.receiver_id == user_model.User.id

    ).filter(
        messages_model.PrivateMessage.id == message_id
    ).group_by(
        messages_model.PrivateMessage.id, user_model.User.id
    )

    # Execute the query
    result = await session.execute(message_query)
    message_data = result.first()
    
    if message_data:
        message, user = message_data
        
        if not (message.sender_id == current_user.id or message.receiver_id == current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This message not you!")

        decrypted_message = await async_decrypt(message.message) if message.message else None

        # Create a privateReturnMessage instance
        return_message = private.PrivateReturnMessage(
            created_at=message.created_at,
            receiver_id=message.receiver_id,
            id=message.id,
            message=decrypted_message,
            fileUrl=message.fileUrl,
            user_name=user.user_name if user else "USER DELETE",
            avatar=user.avatar if user else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp"
        )

        return return_message

    else:
        return None
=======
        private_logger.error(f"Error retrieving recipients: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {e}")

    return result
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
