<<<<<<< HEAD
from datetime import datetime

from fastapi import status, HTTPException, Depends, APIRouter, Request
from fastapi.templating import Jinja2Templates
import pytz
from sqlalchemy.future import select
=======
from _log_config.log_config import get_logger
from datetime import datetime
from fastapi import status, HTTPException, Depends, APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi import BackgroundTasks
import pytz
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from sqlalchemy.ext.asyncio import AsyncSession

from app.mail import send_mail
from ...config import utils
from app.config.config import settings
<<<<<<< HEAD
from app.config.hello import system_notification_sayory
=======
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from ...auth import oauth2
from ...database.async_db import get_async_session
from app.models import user_model
from app.schemas import user
<<<<<<< HEAD
=======
from app.settings.get_info import get_user, has_verified_or_blocked_user

logger = get_logger('manipulation', 'change_and_block.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

router = APIRouter(
    prefix="/manipulation",
    tags=["Change password and blocked account"],
)


@router.put("/password", response_description="Reset password")
<<<<<<< HEAD
async def reset(password: user.UserUpdatePassword,
=======
async def reset(background_tasks: BackgroundTasks,
                password: user.UserUpdatePassword,
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
                db: AsyncSession = Depends(get_async_session),
                current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Reset user password.

    Parameters:
    password (user.UserUpdatePassword): The new password and old password.
    db (AsyncSession): The database session.
    current_user (user_model.User): The current user.

    Returns:
    dict: A dictionary with a success message.

    Raises:
    HTTPException: If the user is not verified or blocked.
    HTTPException: If the user is not found.
    HTTPException: If the old password is incorrect.
    """
<<<<<<< HEAD
    if current_user.verified == False or current_user.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is not verified or blocked")
        
    query = select(user_model.User).where(user_model.User.id == current_user.id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not utils.verify(password.old_password, existing_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
  
    current_time_utc = datetime.now(pytz.UTC)
    # hashed new password
    hashed_password = utils.hash_password(password.new_password)

    # Update password to database
    current_user.password = hashed_password
    current_user.password_changed = current_time_utc
    db.add(current_user)
    await db.commit()
    
    token = current_user.refresh_token
    blocked_link = f"https://{settings.url_address_dns}/api/manipulation/blocked?token={token}"
    await send_mail.send_mail_for_change_password("Changing your account password", current_user.email,
            {
                "title": "Changing your account password",
                "name": current_user.user_name,
                "blocked_link": blocked_link
            }
        )
    message_password = "Your password has been changed 🔐"
    await system_notification_sayory(current_user.id, message_password)
    
    return {"msg": "Password has been reset successfully."}

templates = Jinja2Templates(directory="templates")
@router.get("/blocked")
async def block_account(token: str, request: Request, db: AsyncSession = Depends(get_async_session)):
=======
    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is not verified or blocked")

        query_user = await get_user(current_user.id, db)

        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not utils.verify(password.old_password, query_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )

        current_time_utc = datetime.now(pytz.UTC)
        # hashed new password
        hashed_password = utils.hash(password.new_password)

        # Update password to database
        current_user.password = hashed_password
        current_user.password_changed = current_time_utc
        db.add(current_user)
        await db.commit()

        token = current_user.refresh_token
        blocked_link = f"https://{settings.url_address_dns_company}/api/manipulation/blocked?token={token}"

        background_tasks.add_task(send_mail.send_mail_for_change_password,
                                  "Changing your account password",
                                  current_user.email,
                                  {
                                      "title": "Changing your account password",
                                      "name": current_user.user_name,
                                      "blocked_link": blocked_link
                                  })

        return {"msg": "Password has been reset successfully."}

    except Exception as e:
        logger.error(f"An error occurred while resetting password: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))

templates = Jinja2Templates(directory="templates")
@router.get("/blocked")
async def block_account(token: str, request: Request,
                        db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    This function is responsible for blocking a user's account.
    It retrieves the user from the database using the provided token.
    If the user is found, it sets the 'blocked' attribute to True and commits the changes to the database.
    Finally, it renders a template response for the blocked account page.

    Parameters:
    token (str): The token used to authenticate and retrieve the user.
    request (Request): The FastAPI request object, used to access the request context.
    db (AsyncSession): The database session, used to interact with the database.

    Returns:
    TemplateResponse: A FastAPI TemplateResponse object, rendering the "blocked_account.html" template.

    Raises:
    HTTPException: If the user is not found in the database.
    """
<<<<<<< HEAD
    user = await oauth2.get_current_user(token, db)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.blocked = True
    db.add(user)
    await db.commit()
    
    return templates.TemplateResponse("blocked_account.html", {"request": request})
=======
    try:
        get_user = await oauth2.get_current_user(token, db)

        if not get_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        get_user.blocked = True
        db.add(get_user)
        await db.commit()

        return templates.TemplateResponse("blocked_account.html", {"request": request})
    except Exception as e:
        logger.error(f"An error occurred while blocking user: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
