from typing import List, Optional
from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import messages_model
from app.schemas import room as room_schema

from app.auth import oauth2
from app.database.database import get_db

from app.models import user_model, room_model

router = APIRouter(
    prefix="/admin_rooms",
    tags=["Admin Rooms"],
)



@router.get("/", response_model=List[room_schema.RoomBase])
async def get_rooms_info(db: Session = Depends(get_db),
                         count_messages_sort: Optional[bool] = False,
                         count_users_sort: Optional[bool] = False,
                         current_user: user_model.User = Depends(oauth2.get_current_user)):
    

    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} not admin")
    
    
    
    rooms = db.query(
        room_model.Rooms.id,
        room_model.Rooms.owner,
        room_model.Rooms.name_room,
        room_model.Rooms.image_room,
        room_model.Rooms.created_at,
        room_model.Rooms.secret_room,
        room_model.Rooms.block,
        room_model.Rooms.delete_at,
        func.count(messages_model.ChatMessages.id).label('count_messages')
    ).outerjoin(messages_model.ChatMessages, room_model.Rooms.name_room == messages_model.ChatMessages.rooms) \
    .filter(room_model.Rooms.name_room != 'Hell', room_model.Rooms.secret_room == False) \
    .group_by(room_model.Rooms.id) \
    .order_by(desc('count_messages')) \
    .all()
    # Count messages for room
    messages_count = db.query(
        messages_model.ChatMessages.rooms,
        func.count(messages_model.ChatMessages.id).label('count')
    ).group_by(messages_model.ChatMessages.rooms).filter(messages_model.ChatMessages.rooms != 'Hell').all()

    # Count users for room
    users_count = db.query(
        user_model.UserStatus.name_room,
        func.count(user_model.UserStatus.id).label('count')
    ).group_by(user_model.UserStatus.name_room).filter(user_model.UserStatus.name_room != 'Hell').all()

    # merge result
    rooms_info = []
    for room in rooms:
        
        room_info = room_schema.RoomBase(
            id=room.id,
            owner=room.owner,
            name_room=room.name_room,
            image_room=room.image_room,
            count_users=next((uc.count for uc in users_count if uc.name_room == room.name_room), 0),
            count_messages=next((mc.count for mc in messages_count if mc.rooms == room.name_room), 0),
            created_at=room.created_at,
            secret_room=room.secret_room,
            block=room.block
        )
        rooms_info.append(room_info)
        if count_messages_sort:
            rooms_info.sort(key=lambda x: x.count_messages, reverse=True)
        elif count_users_sort:
            rooms_info.sort(key=lambda x: x.count_users, reverse=True)

    return rooms_info


