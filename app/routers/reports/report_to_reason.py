from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.async_db import get_async_session
from app.auth import oauth2
from app.models import reports_model, user_model, room_model, messages_model
from app.schemas import report

router = APIRouter(
    prefix="/report",
    tags=['Report']
)

@router.post("/send")
async def send_report(
    report_data: report.ReportMessage,
    db: AsyncSession = Depends(get_async_session),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    
    message = await check_message_id(db=db, message_id=report_data.message_id)
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    await add_report_message(db=db, report_data=report_data, user_id=current_user.id)
    
    room_id = await get_room_id(db, report_data.message_id)
    if room_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    await send_notification_to_moderators(db, room_id, report_data.message_id)
    
    return {"message": f"Report sent successfully"}

    
    
async def check_message_id(db, message_id):
    
    check_message = select(messages_model.Socket).where(messages_model.Socket.id == message_id)
    result = await db.execute(check_message)
    message = result.scalar_one_or_none()
    return message is not None

async def add_report_message(db, report_data, user_id):
    
    new_report = reports_model.Report(
        message_id=report_data.message_id,
        reported_by_user_id=user_id,
        reason=report_data.reason,
        additional_info=report_data.additional_info
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report



async def get_all_moderators_in_room(db, room_id):
    
    role_in_room = select(room_model.RoleInRoom).where(
        room_model.RoleInRoom.room_id == room_id
    ).where(
        or_(room_model.RoleInRoom.role == "moderator", room_model.RoleInRoom.role == "owner")
    )
    result = await db.execute(role_in_room)
    moderators = result.scalars().all()
    
    return moderators


async def get_room_id(db, message_id):
    check_message = select(messages_model.Socket).where(messages_model.Socket.id == message_id)
    result = await db.execute(check_message)
    message = result.scalar_one_or_none()
    
    if not message:
        return None
    
    room_query = select(room_model.Rooms.id).where(room_model.Rooms.name_room == message.rooms)
    result = await db.execute(room_query)
    room = result.scalar_one_or_none()
    return room


async def send_notification_to_moderators(db, room_id, message_id):
    
    moderators = await get_all_moderators_in_room(db, room_id)
    for moderator in moderators:
        notification = reports_model.Notification(
            room_id=room_id,
            message_id=message_id,
            moderator_id=moderator.user_id,
            seen=False
        )
        db.add(notification)
    await db.commit()