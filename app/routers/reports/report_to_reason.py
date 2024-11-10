from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.async_db import get_async_session
from app.auth import oauth2
from app.models import user_model
from app.schemas import report
from _log_config.log_config import get_logger

from .functions_report import (
    check_message_id,
    add_report_message,
    get_room_id,
    send_notification_to_moderators,
    get_reports,
)


report_logger = get_logger('report', 'report.log')

router = APIRouter(prefix="/report", tags=["Report"])


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_report(
    report_data: report.ReportMessage,
    db: AsyncSession = Depends(get_async_session),
    current_user: user_model.User = Depends(oauth2.get_current_user),
):
    """
    Handles the submission of a report for a specific message.
    """
    # Check if the message exists
    try:
        message = await check_message_id(message_id=report_data.message_id, db=db)
        if message is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
            )

        # Add the report to the database
        report_entry = await add_report_message(
            report_data=report_data, user_id=current_user.id, db=db
        )

        # Retrieve the room ID associated with the message
        room_id = await get_room_id(report_data.message_id, db)
        if room_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )

        # Send a notification to moderators about the new report
        await send_notification_to_moderators(
            room_id=room_id, message_id=report_data.message_id, report_id=report_entry.id, db=db
        )

        return {"message": "Report sent successfully"}

    except Exception as e:
        report_logger.error(f"Error sending report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
        )


@router.get("/get_report")
async def get_report(
    db: AsyncSession = Depends(get_async_session),
    current_user: user_model.User = Depends(oauth2.get_current_user),
):
    try:
        reports = await get_reports(current_user.id, db)

        return reports

    except Exception as e:
        report_logger.error(f"Error retrieving reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
        )
