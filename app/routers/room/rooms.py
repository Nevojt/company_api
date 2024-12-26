<<<<<<< HEAD
from typing import List
from fastapi import File, Form, UploadFile, status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

import random

from app.models import room_model, room_model, messages_model, user_model
from app.schemas import room as room_schema
from app.config.config import settings
from app.config import utils


=======
import logging
from typing import List
from fastapi import File, Form, UploadFile, status, HTTPException, Depends, APIRouter, Response
from sqlalchemy import desc, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.auth import oauth2
from app.config.start_schema import start_app
from app.database.async_db import get_async_session

from app.models import room_model, messages_model, user_model
from app.schemas import room as room_schema
from app.config.config import settings
from app.config import utils, random_images

from app.settings.get_info import (has_verified_or_blocked_user, get_room_by_id,
                                   has_permission_to_the_room, get_room_name, get_room_hell,
                                   get_count_users, get_count_messages)

logging.basicConfig(filename='_log/rooms.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


router = APIRouter(
    prefix="/rooms",
    tags=['All Rooms'],
)

<<<<<<< HEAD

@router.get("/", response_model=List[room_schema.RoomBase])
async def get_rooms_info(db: Session = Depends(get_db)):
    
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.

    Args:
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Returns:
        List[schemas.RoomBase]: A list containing information about each room, such as room name, image, count of users, count of messages, and creation date.
    """
    
    # get info rooms and not room "Hell"
    # rooms = db.query(room_model.Rooms).filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True).order_by(asc(room_model.Rooms.id)).all()
    rooms = db.query(
        room_model.Rooms.id,
        room_model.Rooms.owner,
        room_model.Rooms.name_room,
        room_model.Rooms.image_room,
        room_model.Rooms.created_at,
        room_model.Rooms.secret_room,
        room_model.Rooms.block,
        room_model.Rooms.delete_at,
        room_model.Rooms.description,
        func.count(messages_model.Socket.id).label('count_messages')
    ).outerjoin(messages_model.Socket, room_model.Rooms.name_room == messages_model.Socket.rooms) \
    .filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True) \
    .group_by(room_model.Rooms.id) \
    .order_by(desc('count_messages')) \
    .all()
    # Count messages for room
    messages_count = db.query(
        messages_model.Socket.rooms, 
        func.count(messages_model.Socket.id).label('count')
    ).group_by(messages_model.Socket.rooms).filter(messages_model.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        user_model.User_Status.name_room, 
        func.count(user_model.User_Status.id).label('count')
    ).group_by(user_model.User_Status.name_room).filter(user_model.User_Status.name_room != 'Hell').all()

    # merge result
    rooms_info = []
    for room in rooms:
        room_info = {
            "id": room.id,
            "owner": room.owner,
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            "created_at": room.created_at,
            "secret_room": room.secret_room,
            "block": room.block,
            "description": room.description,
        }
        rooms_info.append(room_schema.RoomBase(**room_info))

    return rooms_info

 

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(room: room_schema.RoomCreate, 
                      db: AsyncSession = Depends(get_async_session), 
                      current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Create a new room.

    Args:
        room (schemas.RoomCreate): Room creation data.
        db (AsyncSession): Database session.
        current_user (str): Currently authenticated user.

    Raises:
        HTTPException: If the room already exists.

    Returns:
        room_model.Rooms: The newly created room.
    """
    
    
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
    room_get = select(room_model.Rooms).where(room_model.Rooms.name_room == room.name_room)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"Room {room.name_room} already exists")
    
    
    new_room = room_model.Rooms(owner=current_user.id, **room.model_dump())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    
    role_in_room = room_model.RoleInRoom(user_id=current_user.id, room_id=new_room.id, role="owner")
    db.add(role_in_room)
    await db.commit()
    await db.refresh(role_in_room)
    
    add_room_to_my_room = room_model.RoomsManagerMyRooms(user_id=current_user.id, room_id=new_room.id)
    db.add(add_room_to_my_room)
    await db.commit()
    await db.refresh(add_room_to_my_room)
    
    if  room.secret_room == True:
        manager_room = room_model.RoomsManager(user_id=current_user.id, room_id=new_room.id)
        db.add(manager_room)
        await db.commit()
        await db.refresh(manager_room)
    
    return new_room


@router.post("/v2", status_code=status.HTTP_201_CREATED)
async def create_room_v2(name_room: str =Form(...),
=======
@router.get("/v2", response_model=List[room_schema.RoomBase])
async def get_rooms_info(db: AsyncSession = Depends(get_async_session)):
    """
    Retrieves information about chat rooms, excluding a specific room ('Hell'), along with associated message and user counts.
    """
    hell = start_app.default_room_name
    try:
        result = await db.execute(
            select(
                room_model.Rooms.id,
                room_model.Rooms.owner,
                room_model.Rooms.name_room,
                room_model.Rooms.image_room,
                room_model.Rooms.created_at,
                room_model.Rooms.secret_room,
                room_model.Rooms.block,
                room_model.Rooms.delete_at,
                room_model.Rooms.description,
                func.count(messages_model.ChatMessages.id).label('count_messages')
            )
            .outerjoin(messages_model.ChatMessages, room_model.Rooms.name_room == messages_model.ChatMessages.rooms)
            .where(room_model.Rooms.name_room != hell, room_model.Rooms.secret_room == False)
            .group_by(room_model.Rooms.id)
            .order_by(desc('count_messages'))
        )
        rooms = result.all()

        # Using separate queries for counting messages and users
        messages_count = await get_count_messages(db)

        users_count = await get_count_users(db)

        rooms_info = []
        for room in rooms:
            room_data = room_schema.RoomBase(
                id=room.id,
                owner=room.owner,
                name_room=room.name_room,
                image_room=room.image_room,
                count_users=next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
                count_messages=next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
                created_at=room.created_at,
                secret_room=room.secret_room,
                block=room.block,
                description=room.description,
                delete_at=room.delete_at
            )
            rooms_info.append(room_data)

        return rooms_info
    except Exception as e:
        logger.error(f"Error occurred while retrieving rooms: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v2", status_code=status.HTTP_201_CREATED)
async def create_room_v2(name_room: str = Form(...),
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
                        description: str = Form(None),
                        file: UploadFile = File(None),
                        secret: bool = False,
                        db: AsyncSession = Depends(get_async_session), 
                        current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Create a new room.

    Args:
<<<<<<< HEAD
        room (schemas.RoomCreate): Room creation data.
=======
        name_room (schemas.RoomCreate): Room creation data.
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        db (AsyncSession): Database session.
        current_user (str): Currently authenticated user.

    Raises:
        HTTPException: If the room already exists.

    Returns:
        room_model.Rooms: The newly created room.
<<<<<<< HEAD
    """
    default_image = ["https://f003.backblazeb2.com/file/imagesapp/DALLE_1+.webp",
                     "https://f003.backblazeb2.com/file/imagesapp/DALLE_4.webp",
                     "https://f003.backblazeb2.com/file/imagesapp/DALLE_3.webp",
                     "https://f003.backblazeb2.com/file/imagesapp/DALLE_2.webp"]
    
    room_data = room_schema.RoomCreateV2(name_room=name_room, secret_room=secret, description=description)
    
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
    room_get = select(room_model.Rooms).where(room_model.Rooms.name_room == room_data.name_room)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"Room {room_data.name_room} already exists")
    if file is None:
        image = random.choice(default_image)
    else:
        image = await utils.upload_to_backblaze(file, settings.bucket_name_room_image)
        
    new_room = room_model.Rooms(owner=current_user.id,
                            image_room=image,
                            company_id=current_user.company_id, 
                            **room_data.model_dump())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    
    role_in_room = room_model.RoleInRoom(user_id=current_user.id, room_id=new_room.id, role="owner")
    db.add(role_in_room)
    await db.commit()
    await db.refresh(role_in_room)
    
    add_room_to_my_room = room_model.RoomsManagerMyRooms(user_id=current_user.id, room_id=new_room.id)
    db.add(add_room_to_my_room)
    await db.commit()
    await db.refresh(add_room_to_my_room)
    
    if  room_data.secret_room == True:
        manager_room = room_model.RoomsManager(user_id=current_user.id, room_id=new_room.id)
        db.add(manager_room)
        await db.commit()
        await db.refresh(manager_room)
    
    return new_room


@router.get("/{name_room}", response_model=room_schema.RoomUpdate)
async def get_room(name_room: str, db: Session = Depends(get_db)):
=======
        @param current_user:  user_model
        @param db: AsyncSession
        @param secret: bool
        @param name_room: str
        @param file: UploadFile
        @param description: str
    """
    try:


        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

        room_get = await get_room_name(name_room, db)

        if room_get:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                detail=f"Room {name_room} already exists")

        room_data = room_schema.RoomCreateV2(name_room=name_room, secret_room=secret, description=description)

        if file is None:
            image = await random_images.fetch_image_url()
        else:
            image = await utils.upload_to_backblaze(file, settings.bucket_name_room_image)

        new_room = room_model.Rooms(owner=current_user.id,
                                    image_room=image,
                                    company_id=current_user.company_id,
                                    **room_data.model_dump())
        db.add(new_room)
        await db.commit()
        await db.refresh(new_room)

        role_in_room = room_model.RoleInRoom(user_id=current_user.id,
                                             room_id=new_room.id,
                                             role="owner")
        db.add(role_in_room)
        await db.commit()
        await db.refresh(role_in_room)

        add_room_to_my_room = room_model.RoomsManagerMyRooms(user_id=current_user.id,
                                                             room_id=new_room.id)
        db.add(add_room_to_my_room)
        await db.commit()
        await db.refresh(add_room_to_my_room)

        if  room_data.secret_room:
            manager_room = room_model.RoomsManagerSecret(user_id=current_user.id,
                                                   room_id=new_room.id)
            db.add(manager_room)
            await db.commit()
            await db.refresh(manager_room)

        return new_room
    except Exception as e:
        logger.error(f"Error occurred while creating room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v2/name_room/{name_room}", response_model=room_schema.RoomUpdate)
async def get_room_by_name(name_room: str,
                            db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Get a specific room by name.

    Parameters:
    name_room (str): The name of the room to retrieve.
    db (Session): The database session.

    Returns:
    schemas.RoomPost: The room with the specified name, or a 404 Not Found error if no room with that name exists.
    """
<<<<<<< HEAD
    post = db.query(room_model.Rooms).filter(room_model.Rooms.name_room == name_room).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    return post


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db), 
                current_user: user_model.User = Depends(oauth2.get_current_user)):
=======
    try:
        query_room = await get_room_name(name_room, db)

        if not query_room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with name_room: {name_room} not found")
        return query_room
    except Exception as e:
        logger.error(f"Error occurred while retrieving room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v2/room_id/{room_id}", response_model=room_schema.RoomUpdate)
async def get_room_by_id(room_id: UUID,  # noqa: F811
                        db: AsyncSession = Depends(get_async_session)):
    """
    Get a specific room by name.

    Parameters:
    name_room (str): The name of the room to retrieve.
    db (Session): The database session.

    Returns:
    schemas.RoomPost: The room with the specified name, or a 404 Not Found error if no room with that name exists.
    """
    try:
        room_query = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id))
        room = room_query.scalar_one_or_none()

        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"post with id room: {room_id} not found")
        return room
    except Exception as e:
        logger.error(f"Error occurred while retrieving room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.put("/v2/name_room/{room_id}")
async def update_room_name(room_id: UUID,
                          name_room: str = Form(...),
                          db: AsyncSession = Depends(get_async_session),
                          current_user: user_model.User = Depends(oauth2.get_current_user)):

    """
    Update a room's name by ID.
    """
    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

        # Fetch room
        room = await get_room_by_id(room_id, db)
        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID {room_id} not found")
        if room.block:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Room is blocked")
        # Check permissions
        if not await has_permission_to_the_room(current_user, room):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not enough permissions")

        # Check if new name already exists for this room
        room_query_name = await get_room_name(name_room, db)

        if room_query_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="New name already exists for this room")

        # Update the room with new name
        room.name_room = name_room
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return {"detail": "Room name updated successfully"}
    except Exception as e:
        logger.error(f"Error occurred while updating room name: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/v2/image_room/{room_id}")
async def update_room_image(room_id: UUID,
                            file: UploadFile = File(...),
                            db: AsyncSession = Depends(get_async_session),
                            current_user: user_model.User = Depends(oauth2.get_current_user)):

    """
    Update a room's name by ID.
    """
    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

        # Fetch room
        room = await get_room_by_id(room_id, db)
        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID {room_id} not found")
        if room.block:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Room is blocked")

            # Check permissions
        if not await has_permission_to_the_room(current_user, room):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not enough permissions")

        image = await utils.upload_to_backblaze(file, settings.bucket_name_room_image)
        room.image_room = image
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return {"detail": "Room image updated successfully"}
    except Exception as e:
        logger.error(f"Error occurred while updating room image: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/v2/secret/{room_id}")
async def update_room_secret(room_id: UUID,
                              secret: bool = Form(...),
                              db: AsyncSession = Depends(get_async_session),
                              current_user: user_model.User = Depends(oauth2.get_current_user)):

    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

            # Отримання кімнати
        room = await get_room_by_id(room_id, db)
        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID {room_id} not found")

        if room.block:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Room is blocked")

        # Check permissions
        if not await has_permission_to_the_room(current_user, room):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not enough permissions")

            # Handle room secrecy logic if applicable
        manager_query = await db.execute(
                select(room_model.RoomsManagerSecret).where(room_model.RoomsManagerSecret.room_id == room_id,
                                                      room_model.RoomsManagerSecret.user_id == current_user.id))
        manager = manager_query.scalar_one_or_none()

        if secret:
            if not manager:
                # Add manager only if not already exists
                manager = room_model.RoomsManagerSecret(user_id=current_user.id,
                                                        room_id=room_id)
                db.add(manager)
        else:
            # Remove manager if exists when making room not secret
            if manager:
                await db.delete(manager)

            # Update the secret status of the room
        if room.secret_room != secret:
            room.secret_room = secret
            db.add(room)

        await db.commit()
        await db.refresh(room)

        return {"detail": "Room secret status updated successfully"}
    except Exception as e:
        logger.error(f"Error occurred while updating room secret: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.put("/v2/description/{room_id}", response_model=room_schema.RoomUpdateDescription)  # Assuming you're using room_id
async def update_room_description(room_id: UUID,
                                  description: str = Form("description"),
                                  db: AsyncSession = Depends(get_async_session),
                                  current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Update a room by ID.
    """
    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

        # Fetch room
        room = await get_room_by_id(room_id, db)

        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID {room_id} not found")

        # Check permissions
        if not await has_permission_to_the_room(current_user, room):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        # Update the room with new data provided by update_room
        room.description = description

        await db.commit()  # Commit changes
        await db.refresh(room)  # Refresh the instance to get updated values

        return room
    except Exception as e:
        logger.error(f"Error occurred while updating room description: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.delete("/v2/delete/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: UUID, db: AsyncSession = Depends(get_async_session),
                     current_user: user_model.User = Depends(oauth2.get_current_user)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """Deletes a room.

    Args:
        room_id (int): The name of the room to delete.
        db (Session): The database session.
        current_user (str): The currently authenticated user.

    Raises:
        HTTPException: If the user does not have sufficient permissions.

    Returns:
        Response: An empty response with status code 204 No Content.
    """
<<<<<<< HEAD
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
    
    room = db.query(room_model.Rooms).filter(room_model.Rooms.id == room_id).first()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")

    if current_user.role != "admin" and current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Updating user statuses
    users_in_room = db.query(user_model.User_Status).filter(user_model.User_Status.room_id == room_id).all()
    for user_status in users_in_room:
        user_status.name_room = 'Hell'
        user_status.room_id = 1  # Assuming 'Hell' room ID is 1
        db.add(user_status)
    
    # Deleting the room
    db.delete(room)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{room_id}", response_model=room_schema.RoomUpdate)  # Assuming you're using room_id
async def update_room(room_id: int, 
                      update_room: room_schema.RoomCreate, 
                      db: AsyncSession = Depends(get_async_session), 
                      current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Update a room by ID.
    """
    if current_user.blocked or not current_user.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied for user {current_user.id}")

    # Fetch room
    room_query = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id))
    room = room_query.scalar_one_or_none()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")

    # Check user permissions
    if current_user.role != "admin" and current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions to modify room")

    # Update the room with new data provided by update_room
    update_data = update_room.model_dump()
    for key, value in update_data.items():
        setattr(room, key, value)  # Dynamically set attributes based on model_dump output

    await db.commit()  # Commit changes
    await db.refresh(room)  # Refresh the instance to get updated values

    # Handle room secrecy logic if applicable
    manager_query = await db.execute(select(room_model.RoomsManager).where(room_model.RoomsManager.room_id == room_id))
    manager = manager_query.scalar_one_or_none()
    
    if update_room.secret_room:
        if manager is None:
            manager = room_model.RoomsManager(user_id=current_user.id, room_id=room_id)
            db.add(manager)
            await db.commit()
            await db.refresh(manager)

    elif update_room.secret_room == False:
        if manager is not None:
            await db.delete(manager)
            await db.commit()

    return room

@router.put("/description/{room_id}", response_model=room_schema.RoomUpdateDescription)  # Assuming you're using room_id
async def update_room_description(room_id: int, 
                      update_room: room_schema.RoomUpdateDescription, 
                      db: AsyncSession = Depends(get_async_session), 
                      current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Update a room by ID.
    """
    if current_user.blocked or not current_user.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied for user {current_user.id}")

    # Fetch room
    room_query = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id))
    room = room_query.scalar_one_or_none()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")

    # Check user permissions
    if current_user.id != room.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions to modify room")

    # Update the room with new data provided by update_room
    room.description = update_room.description

    await db.commit()  # Commit changes
    await db.refresh(room)  # Refresh the instance to get updated values

    return room



@router.put('/block/{room_id}', status_code=status.HTTP_200_OK)
async def block_room(room_id: int, 
                     db: Session = Depends(get_db), 
                     current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Blocks or unblocks a room.

    Args:
        room_id (int): The ID of the room to block or unblock.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: If the room does not exist or the user does not have sufficient permissions.

    Returns:
        JSON: A JSON object with a "message" key containing a message indicating that the room was blocked or unblocked.
    """
    if current_user.blocked == True or current_user.verified == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")

    room = db.query(room_model.Rooms).filter(room_model.Rooms.id == room_id).first()
    
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID: {room_id} not found")
        
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    room.block = not room.block
    db.commit()
    
    status_text = "unblocked" if not room.block else "blocked"
    return {"message": f"Room with ID: {room_id} has been {status_text}"}
=======
    try:
        hell = await get_room_hell(db)
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

        room = await get_room_by_id(room_id, db)

        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID {room_id} not found")

        # Check permissions
        if not await has_permission_to_the_room(current_user, room):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        # Update user statuses in the room
        users_in_room_query = await db.execute(
                                    select(user_model.UserStatus).where(user_model.UserStatus.room_id == room_id))
        users_statuses = users_in_room_query.scalars().all()

        for user_status in users_statuses:
            user_status.name_room = hell.name_room
            user_status.room_id = hell.id

        # Deleting the room
        await db.delete(room)
        await db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error occurred while deleting room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/v2/block-unblock/{room_id}', status_code=status.HTTP_200_OK)
async def block_room(room_id: UUID,
                     db: AsyncSession = Depends(get_async_session),
                     current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked or not verified")

        room = await get_room_by_id(room_id, db)

        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID: {room_id} not found")

        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        room.block = not room.block
        await db.commit()

        status_text = "unblocked" if not room.block else "blocked"
        return {"message": f"Room with ID: {room_id} has been {status_text}"}
    except Exception as e:
        logger.error(f"Error occurred while blocking/unblocking room: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#  Blocks are functionally
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824




<<<<<<< HEAD
@router.get("/company/v2/", response_model=List[room_schema.RoomBase])
async def get_rooms_info_company(current_user: user_model.User = Depends(oauth2.get_current_user),
                                 db: Session = Depends(get_db)):
=======

@router.get("/v2/company", response_model=List[room_schema.RoomBase])
async def get_rooms_info_company(current_user: user_model.User = Depends(oauth2.get_current_user),
                                 db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Retrieves a list of rooms for a specific company, excluding the 'Hell' room and rooms marked as secret.
    The function counts the number of messages and users in each room and returns a list of room information.

    Parameters:
    current_user (room_model.User): The currently authenticated user.
    db (Session): The database session.

    Returns:
    List[room_schema.RoomBase]: A list of room information, including room ID, owner, name, image, creation date,
    secret status, block status, delete status, number of messages, and number of users.
    """
<<<<<<< HEAD
    company_id = current_user.company_id 
    # get info rooms and not room "Hell"
    # rooms = db.query(room_model.Rooms).filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True).order_by(asc(room_model.Rooms.id)).all()
    rooms = db.query(
        room_model.Rooms.id,
        room_model.Rooms.owner,
        room_model.Rooms.name_room,
        room_model.Rooms.image_room,
        room_model.Rooms.created_at,
        room_model.Rooms.secret_room,
        room_model.Rooms.block,
        room_model.Rooms.delete_at,
        func.count(messages_model.Socket.id).label('count_messages')
    ).outerjoin(messages_model.Socket, room_model.Rooms.name_room == messages_model.Socket.rooms) \
    .filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True, room_model.Rooms.company_id == company_id) \
    .group_by(room_model.Rooms.id) \
    .order_by(desc('count_messages')) \
    .all()
    # Count messages for room
    messages_count = db.query(
        messages_model.Socket.rooms, 
        func.count(messages_model.Socket.id).label('count')
    ).group_by(messages_model.Socket.rooms).filter(messages_model.Socket.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        user_model.User_Status.name_room, 
        func.count(user_model.User_Status.id).label('count')
    ).group_by(user_model.User_Status.name_room).filter(user_model.User_Status.name_room != 'Hell').all()

    # merge result
    rooms_info = []
    for room in rooms:
        room_info = {
            "id": room.id,
            "owner": room.owner,
            "name_room": room.name_room,
            "image_room": room.image_room,
            "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            "created_at": room.created_at,
            "secret_room": room.secret_room,
            "block": room.block
        }
        rooms_info.append(room_schema.RoomBase(**room_info))

    return rooms_info
=======

    # get info rooms and not room "Hell"
    # rooms = db.query(room_model.Rooms).filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True).order_by(asc(room_model.Rooms.id)).all()
    try:
        result = await db.execute(
            select(
                room_model.Rooms.id,
                room_model.Rooms.owner,
                room_model.Rooms.name_room,
                room_model.Rooms.image_room,
                room_model.Rooms.created_at,
                room_model.Rooms.secret_room,
                room_model.Rooms.block,
                room_model.Rooms.delete_at,
                room_model.Rooms.description,
                func.count(messages_model.ChatMessages.id).label('count_messages')
            )
            .outerjoin(messages_model.ChatMessages, room_model.Rooms.name_room == messages_model.ChatMessages.rooms)
            .where(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room != True,
                   room_model.Rooms.company_id == current_user.company_id)
            .group_by(room_model.Rooms.id)
            .order_by(desc('count_messages'))
        )
        rooms = result.all()

        # Using separate queries for counting messages and users
        messages_count = await get_count_messages(db)

        users_count = await get_count_users(db)

        rooms_info = []
        for room in rooms:
            room_data = room_schema.RoomBase(
                id=room.id,
                owner=room.owner,
                name_room=room.name_room,
                image_room=room.image_room,
                count_users=next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
                count_messages=next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
                created_at=room.created_at,
                secret_room=room.secret_room,
                block=room.block,
                description=room.description,
                delete_at=room.delete_at
            )
            rooms_info.append(room_data)

        return rooms_info
    except Exception as e:
        logger.error(f"Error occurred while retrieving rooms info: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
