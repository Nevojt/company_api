from _log_config.log_config import get_logger
from uuid import UUID

from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.config.start_schema import start_app

from app.database.async_db import get_async_session

from app.models import user_model, room_model
from app.schemas import room as room_schema

from .get_tabs_info import get_tabs_user, get_one_tab_user, get_room_tab, get_favorite_record, get_room_tab_id
from app.settings.get_info import get_count_users, get_count_messages, get_room_by_id

logger = get_logger('tabs_rooms', 'tabs_rooms.log')
router = APIRouter(
    prefix='/tabs',
    tags=['Tabs User'],
)


@router.post('/')
async def create_user_tab(tab: room_schema.RoomTabsCreate, 
                          db: AsyncSession = Depends(get_async_session), 
                          current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Create a new tab for the current user.

    Args:
        tab (room_schema.RoomTabsCreate): A dictionary containing the details of the new tab.
        db (AsyncSession): The database session.
        current_user (user_model.User): The currently authenticated user.

    Raises:
        HTTPException: If the tab already exists or if there is an internal server error.

    Returns:
        JSON: A JSON object containing the details of the newly created tab.
    """
    if current_user.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked or not verified")
        
    try: 
        # Check the number of tabs the user already owns
        tab_count_query = select(func.count()).where(room_model.RoomTabsInfo.owner_id == current_user.id)
        tab_count = await db.scalar(tab_count_query)
        
        if tab_count >= 10:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Maximum tab limit reached. You can only have 10 tabs.")
        
        # Create a new tab
        new_tab = room_model.RoomTabsInfo(owner_id=current_user.id, **tab.model_dump())
        db.add(new_tab)
        await db.commit()
        await db.refresh(new_tab)
        return new_tab

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating new tab: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


    


@router.get("/")
async def get_user_all_rooms_in_all_tabs(db: AsyncSession = Depends(get_async_session),
                                         current_user: user_model.User = Depends(oauth2.get_current_user)) -> list:
    """
    Get all tabs for the current user.

    Args:
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.

    Returns:
        List[room_schema.RoomTabs]: A list of tabs for the current user.
    """
    try:
        hell = start_app.default_room_name
        # Fetch all tabs for the current user
        user_tabs = await get_tabs_user(current_user.id, db)

        # Initialize a list to store tabs along with their rooms
        tabs_with_rooms = []

        # Fetch rooms and tabs details for the current user
        rooms_and_tabs_query = await db.execute(select(room_model.Rooms, room_model.RoomsTabs
            ).join(room_model.RoomsTabs, room_model.Rooms.id == room_model.RoomsTabs.room_id
            ).filter(room_model.RoomsTabs.user_id == current_user.id))
        rooms_and_tabs = rooms_and_tabs_query.all()


        # Using separate queries for counting messages and users
        messages_count = await get_count_messages(db)

        users_count = await get_count_users(db)

        # Organize rooms into the appropriate tabs
        room_dict = {tab_id: [] for tab_id in [tab.id for tab in user_tabs]}
        for room, tab in rooms_and_tabs:
            room_info = {
                "id": room.id,
                "owner": room.owner,
                "name_room": room.name_room,
                "image_room": room.image_room,
                "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
                "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
                "created_at": room.created_at,
                "secret_room": room.secret_room,
                "favorite": tab.favorite,
                "block": room.block
            }
            room_dict[tab.tab_id].append(room_info)

        # Create the final list of tabs with sorted rooms
        for tab in user_tabs:
            tab_info = {
                "name_tab": tab.name_tab,
                "image_tab": tab.image_tab,
                "id": tab.id,
                "rooms": sorted(room_dict[tab.id], key=lambda x: x['favorite'], reverse=True)
            }
            tabs_with_rooms.append(tab_info)

        return tabs_with_rooms
    except Exception as e:
        logger.error(f"Error fetching user tabs: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")





@router.get('/{tab_id}')
async def get_rooms_in_one_tab(tab_id: int = None,
                                db: AsyncSession = Depends(get_async_session),
                                current_user: user_model.User = Depends(oauth2.get_current_user)
                              ):
    """
    Get all rooms in a specific tab.

    Args:
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.
        tab_id (str): The name of the tab.

    Returns:
        List[room_schema.RoomTabs]: A list of rooms in the specified tab.

    Raises:
        HTTPException: If the tab does not exist.
    """
    try:
        tab_exists = await get_one_tab_user(current_user.id, tab_id, db)
        if not tab_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tab {tab_id} not found"
            )

        # Fetch rooms and tabs details for the current user in the specified tab
        rooms_and_tabs_query = await db.execute(select(room_model.Rooms, room_model.RoomsTabs
            ).join(room_model.RoomsTabs, room_model.Rooms.id == room_model.RoomsTabs.room_id
            ).filter(room_model.RoomsTabs.user_id == current_user.id,
                     room_model.RoomsTabs.tab_id == tab_id))
        rooms_and_tabs = rooms_and_tabs_query.all()

        # Using separate queries for counting messages and users
        messages_count = await get_count_messages(db)

        users_count = await get_count_users(db)


        # Initialize an empty dictionary to store tabs with their associated rooms
         # Prepare room details
        room_details = []
        for room, tab_info in rooms_and_tabs:
            room_info = {
                "id": room.id,
                "owner": room.owner,
                "name_room": room.name_room,
                "image_room": room.image_room,
                "count_users": next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
                "count_messages": next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
                "created_at": room.created_at,
                "secret_room": room.secret_room,
                "favorite": tab_info.favorite,
                "block": room.block
            }

            # Append room info to the list
            room_details.append(room_info)

        # Optionally, sort rooms by a specific criterion
        room_details.sort(key=lambda x: x['favorite'], reverse=True)

        return room_details
    except Exception as e:
        logger.error(f"Error fetching rooms in tab: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")



@router.post('/add-room-to-tab/{tab_id}')
async def add_rooms_to_tab(tab_id: int, room_ids: List[UUID],
                           db: AsyncSession = Depends(get_async_session),
                           current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Add multiple rooms to a tab, remove them from other tabs if they exist.

    Args:
        tab_id (int): The ID of the tab to add the rooms to.
        room_ids (List[int]): A list of room IDs to add.
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.

    Returns:
        dict: Confirmation of the rooms added to the tab.

    Raises:
        HTTPException: If the tab does not exist, any room does not exist, or if any room is already in the specified tab.
    """
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        # Check if the tab exists and belongs to the current user
        tab = await get_one_tab_user(current_user.id, tab_id, db)

        if not tab:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

        # Process each room
        for room_id in room_ids:
            room = await get_room_by_id(room_id, db)
            if not room:
                continue

            existing_link_query = await db.execute(select(room_model.RoomsTabs).where(room_model.RoomsTabs.room_id == room_id,
                                                              room_model.RoomsTabs.tab_id == tab_id))
            existing_link = existing_link_query.scalar_one_or_none()
            if existing_link:
                continue  # Skip if room is already in the tab

            # Remove the room from any other tab
            room_tab = await get_room_tab(room_id, db)
            if room_tab:
                await db.delete(room_tab)

            # Add the room to the tab
            new_room_tab = room_model.RoomsTabs(room_id=room_id, tab_id=tab_id,
                                                user_id=current_user.id, tab_name=tab.name_tab)
            db.add(new_room_tab)

        await db.commit()

        return {"message": f"Rooms {room_ids} added to tab {tab_id}"}
    except Exception as e:
        logger.error(f"Error adding rooms to tab: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")



@router.put('/', status_code=status.HTTP_200_OK)
async def update_tab(tab_id: int,
                     update: room_schema.TabUpdate,
                     db: AsyncSession = Depends(get_async_session),
                     current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        tab = await get_one_tab_user(current_user.id, tab_id, db)
        if not tab:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

            # Update fields if provided in the request
        if update.name_tab is not None:
            tab.name_tab = update.name_tab
        if update.image_tab is not None:
            tab.image_tab = update.image_tab
        await db.commit()
        return {"message": "Tab updated successfully"}
    except Exception as e:
        logger.error(f"Error updating tab: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")


@router.put('/{room_id}')
async def room_update_to_favorites(room_id: UUID,
                                favorite: bool,
                                db: AsyncSession = Depends(get_async_session),
                                current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Updates the favorite status of a room in tab for a specific user.

    Args:
        room_id (int): The ID of the room to update.
        favorite (bool): The new favorite status for the room.
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.

    Returns:
        dict: A dictionary containing the room ID and the updated favorite status.

    Raises:
        HTTPException: If the user is blocked or not verified, a 403 Forbidden error is raised.
        HTTPException: If the room is not found, a 404 Not Found error is raised.
    """
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        # Fetch room
        room = await get_room_by_id(room_id, db)
        if room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

        # Check if there is already a favorite record
        favorite_record = await get_favorite_record(current_user.id,
                                                    room_id, db)

        # Update if exists, else create a new record
        if favorite_record:
            favorite_record.favorite = favorite
        else:
            new_favorite = room_model.RoomsTabs(
                favorite=favorite
            )
            db.add(new_favorite)

        await db.commit()
        return {"room_id": room_id, "favorite": favorite}
    except Exception as e:
        logger.error(f"Error updating room favorite: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")




@router.delete('/')
async def deleted_tab(tab_id: int,
                      db: AsyncSession = Depends(get_async_session),
                      current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Delete a tab.

    Args:
        tab_id: int
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.

    Raises:
        HTTPException: If the tab does not exist or the user does not have sufficient permissions.

    Returns:
        Response: An empty response with status code 204 if the tab was deleted successfully.

    """
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")
        tab = await get_one_tab_user(current_user.id, tab_id, db)
        if not tab:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

        await db.delete(tab)
        await db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting tab: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")
    
    
@router.delete('/delete-room-in-tab/{tab_id}')
async def delete_room_from_tab(tab_id: int, room_ids: List[UUID],
                               db: AsyncSession = Depends(get_async_session),
                               current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Remove rooms from a tab.

    Args:
        tab_id (int): The ID of the tab to remove rooms from.
        room_ids (List[int]): List of room IDs to remove.
        db (Session): The database session.
        current_user (user_model.User): The currently authenticated user.

    Returns:
        Response: HTTP status indicating the outcome.
    """

    # Check if the tab exists and belongs to the current user
    try:
        tab = await get_one_tab_user(current_user.id, tab_id, db)
        if not tab:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tab not found")

        # Remove specified rooms from the tab
        for room_id in room_ids:
            room_link = await get_room_tab_id(room_id, tab_id, db)
            if not room_link:
                continue  # If room not found in the tab, skip it

            await db.delete(room_link)

        await db.commit()  # Commit all changes at once

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting rooms from tab: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error {e}")