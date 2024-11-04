import logging
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import messages_model, user_model
from app.schemas import private
from app.auth import oauth2

router = APIRouter(
    prefix="/direct",
    tags=['Direct'],
)

logging.basicConfig(filename='_log/private.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@router.get("/users-list", response_model=List[private.PrivateInfoRecipient])
async def get_private_recipient(current_user: user_model.User = Depends(oauth2.get_current_user),
                                db: Session = Depends(get_db)):
    """
    Fetches a list of private message recipients and senders for the current user.

    Parameters:
    - current_user (user_model.User): The current user making the request. This parameter is obtained using the `oauth2.get_current_user` dependency.
    - db (Session): The database session. This parameter is obtained using the `get_db` dependency.

    Returns:
    - List[private.PrivateInfoRecipient]: A list of private message recipients and senders. Each recipient/sender is represented by a `PrivateInfoRecipient` object.
    """
    result = []
    try:
        # Query for recipients and senders
        messages_query = db.query(messages_model.PrivateMessage, user_model.User).join(
            user_model.User, messages_model.PrivateMessage.receiver_id == user_model.User.id
        ).filter(
            (messages_model.PrivateMessage.sender_id == current_user.id) | (messages_model.PrivateMessage.receiver_id == current_user.id)
        )

        # Execute query
        messages = messages_query.all()

        # Filter and map results
        users_info = {}
        for message, user in messages:
            other_user_id = message.sender_id if message.receiver_id == current_user.id else message.receiver_id
            other_user = db.query(user_model.User).filter(user_model.User.id == other_user_id).first()

            # Determine if the message is read or not
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

        # Convert to list
        result = list(users_info.values())

        # Sort the list so that read messages (is_read = True) come first
        result.sort(key=lambda x: x.is_read, reverse=True)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Sorry, no recipients or senders found.")
    except Exception as e:
        logger.error(f"Error creating {e}", exc_info=True)
    return result
