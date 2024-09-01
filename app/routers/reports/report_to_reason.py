from fastapi import status, HTTPException, Depends, APIRouter

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.async_db import get_async_session
from app.auth import oauth2
from app.models import user_model
from app.schemas import report

from .functions_report import check_message_id, add_report_message, get_room_id, send_notification_to_moderators, get_reports

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
    
    report = await add_report_message(db=db, report_data=report_data, user_id=current_user.id)
    
    room_id = await get_room_id(db, report_data.message_id)
    if room_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    
    await send_notification_to_moderators(db, room_id, report_data.message_id, report.id)
    
    return {"message": f"Report sent successfully"}

@router.get("/get_report")
async def get_report(
    db: AsyncSession = Depends(get_async_session),
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    
    reports = await get_reports(db, current_user.id)
    
    return reports

