
from fastapi import status, HTTPException, Depends, APIRouter
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.auth import oauth2
from app.database.async_db import get_async_session
from app.models import user_model, messages_model
from app.schemas import message
from app.schemas.message import wrap_message
from sqlalchemy.future import select
from typing import List

from app.config.crypto_encrypto import async_decrypt
from app.settings.get_info import get_room_by_id

router = APIRouter(
    prefix="/messages",
    tags=['Message'],
)



@router.get("/{room_id}/{message_id}")
async def get_count_message_room(room_id: UUID,
                                 message_id: UUID,
                                 session: AsyncSession = Depends(get_async_session)):
    """
    Retrieves the count of messages in a specific room that have an ID greater than a given message ID.

    Args:
        room_id (int): The ID of the room.
        message_id (int): The ID of the message.
        session (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).

    Returns:
        int: The count of messages in the room that have an ID greater than the given message ID.
    """
    message_date = await session.execute(select(messages_model.ChatMessages.created_at)
        .where(messages_model.ChatMessages.id == message_id, messages_model.ChatMessages.room_id == room_id)
    )
    message_date = message_date.scalar_one_or_none()

    # Якщо повідомлення не знайдено, повертаємо 0
    if message_date is None:
        return 0

    # Запит на підрахунок кількості повідомлень після вказаного повідомлення за датою
    count_messages_after = await session.execute(
        select(func.count())
        .where(messages_model.ChatMessages.room_id == room_id,
               messages_model.ChatMessages.created_at > message_date)
    )
    count = count_messages_after.scalar()
    return count


@router.get("/message_id")
async def fetch_message_by_id(message_id: UUID,
                              session: AsyncSession = Depends(get_async_session)):
    """
    Fetches a message by its ID along with user information and returns it as a SocketReturnMessage object.

    Parameters:
    session (AsyncSession): The database session to use for querying the database.
    message_id (int): The ID of the message to fetch.

    Returns:
    Optional[SocketReturnMessage]: A SocketReturnMessage object representing the message, or None if no message is found.
    """
    # Formulate the query
    message_query = select(
        messages_model.ChatMessages,
        user_model.User
    ).outerjoin(
        user_model.User, messages_model.ChatMessages.receiver_id == user_model.User.id

    ).filter(
        messages_model.ChatMessages.id == message_id
    ).group_by(
        messages_model.ChatMessages.id, user_model.User.id
    )

    # Execute the query
    result = await session.execute(message_query)
    message_data = result.first()

    if message_data:
        messages, user = message_data
        decrypted_message = await async_decrypt(messages.message) if messages.message else None

        # Create a SocketReturnMessage instance
        return_message = message.ChatReturnMessage(
            created_at=messages.created_at,
            receiver_id=messages.receiver_id,
            id=messages.id,
            message=decrypted_message,
            fileUrl=messages.fileUrl,
            voiceUrl=messages.voiceUrl,
            videoUrl=messages.videoUrl,
            user_name=user.user_name if user else "Unknown user",
            avatar=user.avatar if user else "https://media.giphy.com/media/9Y01tydkHUVvhxNVKR/giphy.gif?cid=ecf05e47xvp40pbs2k84kiq9qyo4h7c37yuixsylgd9l8c0h&ep=v1_gifs_search&rid=giphy.gif&ct=g",
            deleted=messages.deleted,
            room_id=messages.room_id
        )

        return return_message

    else:
        return None




@router.get("/{room_id}")
async def get_messages_room(room_id: UUID,
                            session: AsyncSession = Depends(get_async_session), 
                            limit: int = 50, skip: int = 0):
    """
    Retrieves a list of socket messages with associated user details, paginated by a limit and offset.

    Args:
        room_id (str): The rooms of the message.
        session (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 50.
        skip (int, optional): Number of messages to skip for pagination. Defaults to 0.

    Returns:
        List[schemas.SocketModel]: A list of socket messages along with user details, structured as per SocketModel schema.
    """
    existing_room = await get_room_by_id(session, room_id)
    if existing_room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    if existing_room.block:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Room is blocked")

    
    query = await session.execute(select(
    messages_model.ChatMessages,
    user_model.User,
    func.coalesce(func.sum(messages_model.ChatMessageVote.dir), 0).label('votes')
    ).outerjoin(
        messages_model.ChatMessageVote, messages_model.ChatMessages.id == messages_model.ChatMessageVote.message_id
    ).outerjoin(
        user_model.User, messages_model.ChatMessages.receiver_id == user_model.User.id
    ).filter(
        messages_model.ChatMessages.room_id == existing_room.id
    ).group_by(
        messages_model.ChatMessages.id, user_model.User.id
    ).order_by(
        desc(messages_model.ChatMessages.created_at)
    ).limit(limit))

    raw_messages = query.all()

    # Convert raw messages to ChatMessagesSchema

    wrapped_messages = []
    for messages, user, votes in raw_messages:
        decrypted_message = await async_decrypt(messages.message)
        socket_model = message.ChatMessagesSchema(
            created_at=messages.created_at,
            receiver_id=messages.receiver_id,
            message=decrypted_message,
            fileUrl=messages.fileUrl,
            voiceUrl=messages.voiceUrl,
            videoUrl=messages.voiceUrl,
            user_name=user.user_name if user is not None else "Unknown user",
            avatar=user.avatar if user is not None else "https://media.giphy.com/media/9Y01tydkHUVvhxNVKR/giphy.gif?cid=ecf05e47xvp40pbs2k84kiq9qyo4h7c37yuixsylgd9l8c0h&ep=v1_gifs_search&rid=giphy.gif&ct=g",
            verified=user.verified,
            id=messages.id,
            vote=votes,
            id_return=messages.id_return,
            edited=messages.edited,
            deleted=messages.deleted,
            room_id=messages.room_id
        )
        wrapped_message = await wrap_message(socket_model)
        wrapped_messages.append(wrapped_message)

    return wrapped_messages




@router.put("/{id}", include_in_schema=False)
async def change_message(id_message: UUID, message_update: message.ChatUpdateMessage,
                         current_user: user_model.User = Depends(oauth2.get_current_user), 
                         session: AsyncSession = Depends(get_async_session)):
    
    
    message_query = await session.execute(select(messages_model.ChatMessages).where(messages_model.ChatMessages.id == id_message,
                                                messages_model.ChatMessages.receiver_id == current_user.id))
    messages = message_query.scalar_one_or_none()

    if messages is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found or you don't have permission to edit this message")

    messages.message = message_update.message
    session.add(message)
    await session.commit()

    return {"message": "Message updated successfully"}
    


# Old functions

@router.get("/", response_model=List[message.ChatMessagesSchema], include_in_schema=False)
async def get_posts(session: AsyncSession = Depends(get_async_session), 
                    limit: int = 50, skip: int = 0):
    
    """
    Retrieves a list of socket messages with associated user details, paginated by a limit and offset.

    Args:
        session (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 50.
        skip (int, optional): Number of messages to skip for pagination. Defaults to 0.

    Returns:
        List[schemas.SocketModel]: A list of socket messages along with user details, structured as per SocketModel schema.
    """

    query = select(
        messages_model.ChatMessages,
        user_model.User, 
        func.coalesce(func.sum(messages_model.ChatMessageVote.dir), 0).label('votes')
    ).outerjoin(
        messages_model.ChatMessageVote, messages_model.ChatMessages.id == messages_model.ChatMessageVote.message_id
    ).join(
        user_model.User, messages_model.ChatMessages.receiver_id == user_model.User.id
    ).group_by(
        messages_model.ChatMessages.id, user_model.User.id
    ).order_by(
        desc(messages_model.ChatMessages.created_at)
    ).limit(50)

    result = await session.execute(query)
    raw_messages = result.all()

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = []
    for messages, user, votes in raw_messages:
        decrypted_message = await async_decrypt(messages.message)
        messages.append(
            messages.ChatMessagesSchema(
                created_at=messages.created_at,
                receiver_id=messages.receiver_id,
                message=decrypted_message,
                fileUrl=messages.fileUrl,
                user_name=user.user_name if user is not None else "Unknown user",
                avatar=user.avatar if user is not None else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/photo_2024-06-14_19-20-40.jpg",
                verified=user.verified if user is not None else None,
                id=messages.id,
                vote=votes,
                id_return=messages.id_return,
                edited=messages.edited,
                deleted=messages.deleted,
                room_id=messages.room_id
            )
        )
    messages.reverse()
    return messages