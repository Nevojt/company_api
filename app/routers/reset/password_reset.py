from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
import pytz
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import user_model
from app.schemas.reset import PasswordReset, PasswordResetRequest
from app.auth import oauth2
from app.config import utils
from app.mail.send_mail import password_reset
# from app.database.database import get_db
from app.database.async_db import get_async_session
from app.config.config import settings




router = APIRouter(
    prefix="/password",
    tags=["Password reset"]
)


@router.post("/request/", status_code=status.HTTP_202_ACCEPTED, response_description="Reset password")
async def reset_password(request: PasswordResetRequest, db: AsyncSession = Depends(get_async_session)):
    """
    Handles the password reset request. Validates the user's email and initiates the password reset process.

    Args:
        request (PasswordResetRequest): The request payload containing the user's email.
        db (Session, optional): Database session dependency. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raises a 404 error if no user is found with the provided email.
        HTTPException: Raises a 404 error if the user's details are not found or the email address is invalid.

    Returns:
        dict: A message confirming that an email has been sent for password reset instructions.
    """
    # Func
    user_q = select(user_model.User).where(user_model.User.email == request.email)
    result = await db.execute(user_q)
    user = result.scalar_one_or_none()
    
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with email: {request.email} not found")
    
    if user.verified is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with email: {request.email} not verification")
    if user is not None:
        token = await oauth2.create_access_token(data={"user_id": user.id}, db=db)
        reset_link = f"https://{settings.url_address_dns}/api/reset?token={token}"
        
        await password_reset("Password Reset", user.email,
            {
                "title": "Password Reset",
                "name": user.user_name,
                "reset_link": reset_link
            }
        )
        return {"msg": "Email has been sent with instructions to reset your password."}
        
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your details not found, invalid email address"
        )
        
        
@router.put("/reset", response_description="Reset password")
async def reset(token: str, new_password: PasswordReset, db: AsyncSession = Depends(get_async_session)):
    """
    Handles the actual password reset using a provided token. Validates the token and updates the user's password.

    Args:
        token (str): The token for user verification, used to ensure the password reset request is valid.
        new_password (PasswordReset): The payload containing the new password.
        db (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).

    Raises:
        HTTPException: Raises a 404 error if no user is found associated with the provided token.

    Returns:
        dict: A message confirming that the password has been successfully reset.
    """
    
    user = await oauth2.get_current_user(token, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    current_time_utc = datetime.now(pytz.UTC)
    # hashed new password
    hashed_password = utils.hash(new_password.password)

    # Update password to database
    user.password = hashed_password
    user.blocked = False
    user.password_changed = current_time_utc
    db.add(user)
    await db.commit()