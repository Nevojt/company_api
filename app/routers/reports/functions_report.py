from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import reports_model, room_model, messages_model
from app.schemas import report
from uuid import UUID
from app.config.crypto_encrypto import async_decrypt
from app.schemas.report import ReportMessage

from _log_config.log_config import get_logger

func_report_logger = get_logger('func_report_log', 'func_report_log.log')

async def check_message_id(message_id: UUID, db: AsyncSession):
    check_message = await db.execute(select(messages_model.ChatMessages).where(
        messages_model.ChatMessages.id == message_id
    ))
    message = check_message.scalar_one_or_none()
    return message is not None


async def add_report_message(report_data: ReportMessage, user_id: UUID, db: AsyncSession):
    try:
        new_report = reports_model.Report(
            message_id=report_data.message_id,
            reported_by_user_id=user_id,
            reason=report_data.reason,
            additional_info=report_data.additional_info,
        )
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        return new_report
    except Exception as e:
        func_report_logger.error(f"Error adding report: {e}")
        raise


async def get_all_moderators_in_room(room_id: UUID, db: AsyncSession):
    try:
        role_in_room = (
            select(room_model.RoleInRoom)
            .where(room_model.RoleInRoom.room_id == room_id)
            .where(
                or_(
                    room_model.RoleInRoom.role == "moderator",
                    room_model.RoleInRoom.role == "owner",
                )
            )
        )
        result = await db.execute(role_in_room)
        moderators = result.scalars().all()

        return moderators
    except Exception as e:
        func_report_logger.error(f"Error getting moderators in room: {e}")
        raise


async def get_message(message_id: UUID, db: AsyncSession):
    try:
        check_message = await db.execute(select(messages_model.ChatMessages).where(
            messages_model.ChatMessages.id == message_id
        ))

        message = check_message.scalar_one_or_none()
        return message
    except Exception as e:
        func_report_logger.error(f"Error getting message: {e}")
        raise


async def get_room_id(message_id: UUID, db: AsyncSession):
    try:
        message = await get_message(message_id, db)

        if not message:
            return None

        room_query = await db.execute(select(room_model.Rooms.id).where(
            room_model.Rooms.name_room == message.rooms
        ))
        room = room_query.scalar_one_or_none()
        return room
    except Exception as e:
        func_report_logger.error(f"Error getting room id: {e}")
        raise


async def send_notification_to_moderators(room_id: UUID, message_id: UUID, report_id: int, db: AsyncSession):
    try:
        moderators = await get_all_moderators_in_room(room_id, db)
        for moderator in moderators:
            notification = reports_model.Notification(
                room_id=room_id,
                message_id=message_id,
                moderator_id=moderator.user_id,
                seen=False,
                report_id=report_id,
            )
            db.add(notification)
        await db.commit()
    except Exception as e:
        func_report_logger.error(f"Error sending notification to moderators: {e}")
        raise


async def get_reports(user_id: UUID, db: AsyncSession):
    try:

        get_notifications_query = await db.execute(select(reports_model.Notification).where(
            reports_model.Notification.moderator_id == user_id
        ))
        notifications = get_notifications_query.scalars().all()

        report_notifications = []

        for notification in notifications:
            message = await get_message(notification.message_id, db)
            decrypt_message = await async_decrypt(message.message)
            get_reports_query = await db.execute(select(reports_model.Report).where(
                reports_model.Report.id == notification.report_id
            ))
            report_records = get_reports_query.scalars().all()

            for report_record in report_records:
                report_notification = report.ReportsGetNotification(
                    report_id=report_record.id,
                    reporter_by_user_id=report_record.reported_by_user_id,
                    message_id=report_record.message_id,
                    message=decrypt_message,
                    room_id=notification.room_id,
                    room=message.rooms,
                    reason=report_record.reason,
                    additional_info=report_record.additional_info,
                    status=report_record.status,
                    seen=notification.seen,
                    created_at=report_record.created_at,
                )

                report_notifications.append(report_notification)

        return report_notifications
    except Exception as e:
        func_report_logger.error(f"Error getting reports: {e}")
        raise
