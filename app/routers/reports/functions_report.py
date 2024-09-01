

from sqlalchemy.future import select
from sqlalchemy import or_
from app.models import reports_model, room_model, messages_model
from app.schemas import report
   
from app.config.crypto_encrypto import async_decrypt  

    
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

async def get_message(db, message_id):
    
    check_message = select(messages_model.Socket).where(messages_model.Socket.id == message_id)
    result = await db.execute(check_message)
    message = result.scalar_one_or_none()
    return message

async def get_room_id(db, message_id):
    message = await get_message(db, message_id)
    
    if not message:
        return None
    
    room_query = select(room_model.Rooms.id).where(room_model.Rooms.name_room == message.rooms)
    result = await db.execute(room_query)
    room = result.scalar_one_or_none()
    return room


async def send_notification_to_moderators(db, room_id, message_id, report_id):
    
    moderators = await get_all_moderators_in_room(db, room_id)
    for moderator in moderators:
        notification = reports_model.Notification(
            room_id=room_id,
            message_id=message_id,
            moderator_id=moderator.user_id,
            seen=False,
            report_id=report_id
        )
        db.add(notification)
    await db.commit()
    
    
async def get_reports(db, user_id):
    get_notifications_query = select(reports_model.Notification).where(reports_model.Notification.moderator_id == user_id)
    result = await db.execute(get_notifications_query)
    notifications = result.scalars().all()

    report_notifications = []
 
    for notification in notifications:
        message = await get_message(db, notification.message_id)
        decript_message = await async_decrypt(message.message)
        get_reports_query = select(reports_model.Report).where(reports_model.Report.id == notification.report_id)
        result = await db.execute(get_reports_query)
        report_records = result.scalars().all()

        for report_record in report_records:
            
            report_notification = report.ReportsGetNotification(
                report_id=report_record.id,
                reporter_by_user_id=report_record.reported_by_user_id,
                message_id=report_record.message_id,
                message=decript_message,
                room_id=notification.room_id,
                room=message.rooms,
                reason=report_record.reason,
                additional_info=report_record.additional_info,
                status=report_record.status,
                seen=notification.seen,
                created_at=report_record.created_at
            )

            report_notifications.append(report_notification)
    
    return report_notifications



