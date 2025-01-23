from fastapi import APIRouter, Depends, Request
<<<<<<< HEAD
=======

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates
from app.models import user_model
from app.database.async_db import get_async_session
<<<<<<< HEAD

=======
from app.config import  crypto_encrypto
from app.routers.mail import update_mail
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/success_registration", include_in_schema=False)
<<<<<<< HEAD
async def verify_email(token: str, request: Request, db: AsyncSession = Depends(get_async_session)):
=======
async def verify_email(token: str, request: Request,
                       db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Verifies the user's email address using the provided token.
    
    Verifies the user's email address using the provided token.

    Args:
        token (str): The token received from the user's email.
        db (AsyncSession): Asynchronous database session.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        dict: A message confirming email verification.
<<<<<<< HEAD
=======
        @param token:
        @param db:
        @param request:
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    # Query for a user with the matching token_verify field
    # Construct the query
    query = select(user_model.User).where(user_model.User.token_verify == token)

    # Execute the query
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse("error_page.html", {"request": request})
<<<<<<< HEAD
        

    # Update the user's verified status
    user.verified = True
    user.token_verify = None  # Clear the token once verified
=======

    #  decryption for token
    email = await crypto_encrypto.decrypt_token(token)
    # print(f"decryption verify_email {email}")

    user.email = email
    # Update the user's verified status
    user.verified = True
    user.token_verify = None  # Clear the token once verified

    update_mail_data = await update_mail.get_data_for_mail(email, db)
    if update_mail_data:
        update_mail_data.is_active = False

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    await db.commit()

    return templates.TemplateResponse("success_registration.html", {"request": request})