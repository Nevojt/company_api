
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy import desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.auth import oauth2
from app.database.async_db import get_async_session
from app.models import user_model, room_model, messages_model
from app.schemas import message
from sqlalchemy.future import select
from typing import List

from app.config.crypto_encrypto import async_decrypt

router = APIRouter(
    prefix="/messages",
    tags=['Message'],
)


async def check_room_blocked(room_id: int, session: AsyncSession):
    query = select(room_model.Rooms).where(room_model.Rooms.id == room_id, room_model.Rooms.block.is_(True))
    try:
        result = await session.execute(query)
        room_record = result.scalar_one()
        return True
    except NoResultFound:
        return False

@router.get("/{room_id}/{message_id}")
async def get_count_message_room(room_id: int,
                                 message_id: int, 
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
    get_room_and_message = (
        select(room_model.Rooms.name_room, messages_model.Socket.id)
        .join(messages_model.Socket, 
              and_(
                  room_model.Rooms.name_room == messages_model.Socket.rooms,
                  messages_model.Socket.id == message_id
              ), isouter=True)
        .where(room_model.Rooms.id == room_id)
    )
    result = await session.execute(get_room_and_message)
    room_message_data = result.first()
    
    if room_message_data is None or room_message_data[0] is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    name_room, message_id_check = room_message_data

    if message_id_check is None:
        return 0

    count_query = (
        select(func.count())
        .select_from(messages_model.Socket)
        .where(
            and_(
                messages_model.Socket.rooms == name_room,
                messages_model.Socket.id > message_id
            )
        )
    )
    result = await session.execute(count_query)
    count_messages_after = result.scalar()
    return count_messages_after


@router.get("/message_id")

async def fetch_message_by_id(message_id: int,
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
        messages_model.Socket, 
        user_model.User
    ).outerjoin(
        user_model.User, messages_model.Socket.receiver_id == user_model.User.id

    ).filter(
        messages_model.Socket.id == message_id
    ).group_by(
        messages_model.Socket.id, user_model.User.id
    )

    # Execute the query
    result = await session.execute(message_query)
    message_data = result.first()

    if message_data:
        socket, user = message_data
        decrypted_message = await async_decrypt(socket.message) if socket.message else None

        # Create a SocketReturnMessage instance
        return_message = message.SocketReturnMessage(
            created_at=socket.created_at,
            receiver_id=socket.receiver_id,
            id=socket.id,
            message=decrypted_message,
            fileUrl=socket.fileUrl,
            user_name=user.user_name if user else "USER DELETE",
            avatar=user.avatar if user else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/boy_1.webp"
        )

        return return_message

    else:
        return None




@router.get("/{room_id}", response_model=List[message.SocketModel])
async def get_messages_room(room_id: int, 
                            session: AsyncSession = Depends(get_async_session), 
                            limit: int = 50, skip: int = 0):
    """
    Retrieves a list of socket messages with associated user details, paginated by a limit and offset.

    Args:
        rooms (str): The rooms of the message.
        session (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).
        limit (int, optional): Maximum number of messages to retrieve. Defaults to 50.
        skip (int, optional): Number of messages to skip for pagination. Defaults to 0.

    Returns:
        List[schemas.SocketModel]: A list of socket messages along with user details, structured as per SocketModel schema.
    """
    room_blocked = await check_room_blocked(room_id, session)  
    if room_blocked:
        raise HTTPException(status_code=403, detail="Room is blocked")
    
    room = select(room_model.Rooms).where(room_model.Rooms.id == room_id)
    result = await session.execute(room)
    existing_room = result.scalar_one_or_none()
    if existing_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    
    query = select(
    messages_model.Socket, 
    user_model.User, 
    func.coalesce(func.sum(messages_model.Vote.dir), 0).label('votes')
    ).outerjoin(
        messages_model.Vote, messages_model.Socket.id == messages_model.Vote.message_id
    ).outerjoin( 
        user_model.User, messages_model.Socket.receiver_id == user_model.User.id
    ).filter(
        messages_model.Socket.rooms == existing_room.name_room
    ).group_by(
        messages_model.Socket.id, user_model.User.id
    ).order_by(
        desc(messages_model.Socket.created_at)
    )

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = []
    for socket, user, votes in raw_messages:
        decrypted_message = await async_decrypt(socket.message)
        messages.append(
            message.SocketModel(
                created_at=socket.created_at,
                receiver_id=socket.receiver_id,
                message=decrypted_message,
                fileUrl=socket.fileUrl,
                user_name=user.user_name if user is not None else "Unknown user",
                avatar=user.avatar if user is not None else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/photo_2024-06-14_19-20-40.jpg",
                verified=user.verified if user is not None else None,
                id=socket.id,
                vote=votes,
                id_return=socket.id_return,
                edited=socket.edited,
                return_message=socket.return_message
            )
        )
    messages.reverse()
    return messages




@router.put("/{id}", include_in_schema=False)
async def change_message(id_message: int, message_update: message.SocketUpdate,
                         current_user: user_model.User = Depends(oauth2.get_current_user), 
                         session: AsyncSession = Depends(get_async_session)):
    
    
    query = select(messages_model.Socket).where(messages_model.Socket.id == id_message, messages_model.Socket.receiver_id == current_user.id)
    result = await session.execute(query)
    message = result.scalar()

    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found or you don't have permission to edit this message")

    message.message = message_update.message
    session.add(message)
    await session.commit()

    return {"message": "Message updated successfully"}
    


# Old functions

@router.get("/", response_model=List[message.SocketModel], include_in_schema=False)
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
        messages_model.Socket, 
        user_model.User, 
        func.coalesce(func.sum(messages_model.Vote.dir), 0).label('votes')
    ).outerjoin(
        messages_model.Vote, messages_model.Socket.id == messages_model.Vote.message_id
    ).join(
        user_model.User, messages_model.Socket.receiver_id == user_model.User.id
    ).group_by(
        messages_model.Socket.id, user_model.User.id
    ).order_by(
        desc(messages_model.Socket.created_at)
    ).limit(50)

    result = await session.execute(query)
    raw_messages = result.all()

    result = await session.execute(query)
    raw_messages = result.all()

    # Convert raw messages to SocketModel
    messages = []
    for socket, user, votes in raw_messages:
        decrypted_message = await async_decrypt(socket.message)
        messages.append(
            message.SocketModel(
                created_at=socket.created_at,
                receiver_id=socket.receiver_id,
                message=decrypted_message,
                fileUrl=socket.fileUrl,
                user_name=user.user_name if user is not None else "Unknown user",
                avatar=user.avatar if user is not None else "https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/inne/image/photo_2024-06-14_19-20-40.jpg",
                verified=user.verified if user is not None else None,
                id=socket.id,
                vote=votes,
                id_return=socket.id_return,
                edited=socket.edited
            )
        )
    messages.reverse()
    return messages