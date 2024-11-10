
from uuid import UUID
from fastapi import APIRouter, HTTPException, Form, Depends, status, Request, Query, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from sqlalchemy.future import select
from  datetime import datetime, timezone

from _log_config.log_config import get_logger

from app.mail.send_mail import send_mail_for_change_email, send_registration_mail

from app.database.async_db import get_async_session

from ...auth import oauth2
from app.models import user_model, password_model
from app.config import utils, crypto_encrypto
from app.config.config import settings

update_logger = get_logger('update_mail', 'update_mail.log')

router = APIRouter(
    prefix="/update-mail",
    tags=["Update Mail"]
)

@router.post("/")
async def update_email(email: EmailStr = Form(...),
                       password: str = Form(...),
                       db: AsyncSession = Depends(get_async_session),
                       current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
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
                                detail="User is blocked!")

        if not current_user.verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User is not verified!")

        if not utils.verify(password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )

        # token = utils.generate_access_code()
        token = await crypto_encrypto.generate_encrypted_token(email)
        update_code = utils.generate_reset_code()
        new_update_request = password_model.MailUpdateModel(
            user_id=current_user.id,
            new_email=email,
            update_token=token,
            update_code=update_code,
            is_active=True
        )
        db.add(new_update_request)
        await db.commit()

        update_linc = f"https://{settings.url_address_dns}/api/update-mail/success_update_linc?token={token}"
        # update_linc = f"http://127.0.0.1:8000/api/update-mail/success_update_linc?token={token}"
        await send_mail_for_change_email("Changing your account email", current_user.email,
                                                      {
                                                          "title": "Changing your account email.",
                                                          "name": current_user.user_name,
                                                          "update_link": update_linc,
                                                          "reset_code": update_code
                                                      }
                                                      )


        return "Send email confirmation"

    except Exception as e:
        update_logger.error(f"Error updating email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


templates = Jinja2Templates(directory="templates")


@router.get("/success_update_linc")
async def update_email_link(background_tasks: BackgroundTasks,
                            request: Request,
                            token: str = Query(...),
                            db: AsyncSession = Depends(get_async_session)
                        ):

    try:
        mail_update_record = await get_data_for_token(token, db)
        if not mail_update_record:
            return templates.TemplateResponse("error_page.html", {"request": request})

        if mail_update_record.expires_at < datetime.now(timezone.utc):
            return templates.TemplateResponse("error_page.html", {"request": request})

        background_tasks.add_task(get_and_update_user_email,
                                  user_id=mail_update_record.user_id,
                                  new_email=mail_update_record.new_email,
                                  db=db)

        # Деактивувати запис у MailUpdateModel
        # mail_update_record.is_active = False
        await db.commit()


        return templates.TemplateResponse("success_registration.html", {"request": request})
    except Exception as e:
        update_logger.error(f"Error in success_update_linc: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/success_update_code", response_description="Update Email Code")
async def update_email_code(background_tasks: BackgroundTasks,
                            code: str,
                            db: AsyncSession = Depends(get_async_session)
                           ):
    try:
        query = await db.execute(select(password_model.MailUpdateModel).where(
            password_model.MailUpdateModel.update_code == code,
            password_model.MailUpdateModel.is_active
        ))

        mail_update_record = query.scalar_one_or_none()

        if not mail_update_record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Update code not found.")

        if mail_update_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Update code expired.")

        background_tasks.add_task(get_and_update_user_email,
                                user_id=mail_update_record.user_id,
                                new_email=mail_update_record.new_email,
                                db=db)
        # await get_and_update_user_email(user_id=mail_update_record.user_id,
        #                                 new_email=mail_update_record.new_email,
        #                                 db=db)

        # mail_update_record.is_active = False
        await db.commit()
    except Exception as e:
        update_logger.error(f"Error in update_email_code: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



async def get_data_for_token(token: str,
                             db: AsyncSession = Depends(get_async_session)):
    try:
        query = await db.execute(select(password_model.MailUpdateModel).where(
            password_model.MailUpdateModel.update_token == token,
            password_model.MailUpdateModel.is_active
        ))
        mail_update_record = query.scalar_one_or_none()
        return mail_update_record
    except Exception as e:
        update_logger.error(f"Error get data token {e}")

async def get_data_for_mail(email: str,
                            db: AsyncSession = Depends(get_async_session)):
    try:
        query = await db.execute(select(password_model.MailUpdateModel).where(
            password_model.MailUpdateModel.new_email == email,
            password_model.MailUpdateModel.is_active
        ))
        mail_update_record = query.scalar_one_or_none()
        return mail_update_record
    except Exception as e:
        update_logger.error(f"Error get data for mail {e}")




async def get_and_update_user_email(user_id: UUID,
                                    new_email: str,
                                    db: AsyncSession = Depends(get_async_session)):
    try:
        user_query = await db.execute(select(user_model.User).where(user_model.User.id == user_id))
        user = user_query.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        token_verify = await crypto_encrypto.generate_encrypted_token(new_email)
        user.token_verify = token_verify

        verification_link = f"https://{settings.url_address_dns}/api/success_registration?token={token_verify}"
        # verification_link = f"http://127.0.0.1:8000/api/success_registration?token={token_verify}"
        await send_registration_mail( "Please verify your email!", new_email,
                                  {
                                      "title": "Registration",
                                      "name": user.user_name,
                                      "registration_link": verification_link
                                  })

        await db.commit()
        return {"msg": "Email has been updated successfully."}
    except Exception as e:
        update_logger.error(f"Error in get_and_update_user_email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



