

from fastapi import APIRouter, HTTPException, Form, Depends, status, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from sqlalchemy.future import select



from app.mail.send_mail import send_mail_for_change_email
from app.schemas import mail
from app.database.async_db import get_async_session

from ...auth import oauth2
from app.models import user_model, password_model
from app.config import utils
from app.config.config import settings


router = APIRouter(
    prefix="/update-mail",
    tags=["Update Mail"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def update_email(email: EmailStr = Form(...),
                       password: str = Form(...),
                       db: AsyncSession = Depends(get_async_session),
                       current_user: user_model.User = Depends(oauth2.get_current_user)):

    existing_user = await db.execute(
        select(user_model.User).where(user_model.User.email == email)
    )
    if existing_user.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already in use."
        )

    if current_user.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User is blocked!")
    if not current_user.verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User is not verified!")

    if not utils.verify(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )

    token = utils.generate_access_code()
    new_update_request = password_model.MailUpdateModel(
        user_id=current_user.id,
        new_email=email,
        update_token=token,
        update_code=utils.generate_random_code(),  # Реалізуйте функцію для генерації коду
        is_active=True
    )
    db.add(new_update_request)
    await db.commit()

    update_linc = f"https://127.0.0.1:8000/api/update-mail/success_update?token={token}"
    await send_mail_for_change_email("Changing your account email", current_user.email,
                                                  {
                                                      "title": "Changing your account email.",
                                                      "name": current_user.user_name,
                                                      "update_link": update_linc,
                                                  }
                                                  )

    print(password)
    return "Update test"


templates = Jinja2Templates(directory="templates")


@router.get("/success_update")
async def update_email_link(
                    request: Request,
                    token: str = Query(...),
                    db: AsyncSession = Depends(get_async_session)
                ):
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
        @param db:
        @param email:
        @param token:
        @param request:
    """
    # Query for a user with the matching token_verify field
    # Construct the query
    # Отримати запис з таблиці MailUpdateModel за токеном
    query = select(password_model.MailUpdateModel).where(
        password_model.MailUpdateModel.update_token == token,
        password_model.MailUpdateModel.is_active == True  # Переконайтеся, що запит активний
    )
    result = await db.execute(query)
    mail_update_record = result.scalar_one_or_none()

    if not mail_update_record:
        return templates.TemplateResponse("error_page.html", {"request": request})

    # Отримати користувача за user_id
    user_query = select(user_model.User).where(user_model.User.id == mail_update_record.user_id)
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Оновити електронну адресу користувача
    user.email = mail_update_record.new_email
    await db.commit()

    # Деактивувати запис у MailUpdateModel
    mail_update_record.is_active = False
    await db.commit()

    return templates.TemplateResponse("success_registration.html", {"request": request})

# @router.post("/request/", status_code=status.HTTP_202_ACCEPTED, response_description="Update Email")
# async def reset_password(request: EmailStr = Form(...),
#                          db: AsyncSession = Depends(get_async_session)):
#     """
#     Handles the password reset request. Validates the user's email and initiates the password reset process.
#
#     Args:
#         request (PasswordResetRequest): The request payload containing the user's email.
#         db (Session, optional): Database session dependency. Defaults to Depends(get_db).
#
#     Raises:
#         HTTPException: Raises a 404 error if no user is found with the provided email.
#         HTTPException: Raises a 404 error if the user's details are not found or the email address is invalid.
#
#     Returns:
#         dict: A message confirming that an email has been sent for password reset instructions.
#     """
#     # Func
#     user_q = select(user_model.User).where(user_model.User.email == request.email)
#     result = await db.execute(user_q)
#     user = result.scalar_one_or_none()
#
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"User with email: {request.email} not found")
#
#     if user.verified is False:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail=f"User with email: {request.email} not verification")
#     if user is not None:
#         token = await oauth2.create_access_token(data={"user_id": user.id}, db=db)
#         reset_link = f"https://{settings.url_address_dns}/api/reset?token={token}"
#
#         await password_reset(subject="Password Reset",
#                              email_to=user.email,
#                              body={
#                                  "title": "Password Reset",
#                                  "name": user.user_name,
#                                  "reset_link": reset_link
#                              }
#                              )
#
#         return {"msg": "Email has been sent with instructions to reset your password."}
#
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Your details not found, invalid email address"
#         )


# @router.put("/reset", response_description="Reset password")
# async def reset(token: str, new_password: PasswordReset, db: AsyncSession = Depends(get_async_session)):
#     """
#     Handles the actual password reset using a provided token. Validates the token and updates the user's password.
#
#     Args:
#         token (str): The token for user verification, used to ensure the password reset request is valid.
#         new_password (PasswordReset): The payload containing the new password.
#         db (AsyncSession, optional): Asynchronous database session. Defaults to Depends(get_async_session).
#
#     Raises:
#         HTTPException: Raises a 404 error if no user is found associated with the provided token.
#
#     Returns:
#         dict: A message confirming that the password has been successfully reset.
#     """
#
#     user = await oauth2.get_current_user(token, db)
#
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     current_time_utc = datetime.now(pytz.UTC)
#     # hashed new password
#     hashed_password = utils.hash_password(new_password.password)
#
#     # Update password to database
#     user.password = hashed_password
#     user.blocked = False
#     user.password_changed = current_time_utc
#     db.add(user)
#     await db.commit()