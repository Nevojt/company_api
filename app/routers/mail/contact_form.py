
<<<<<<< HEAD
from fastapi import APIRouter, HTTPException
from app.mail.send_mail import send_mail_for_contact_form
from app.schemas import mail
=======
from fastapi import APIRouter, HTTPException, status
from app.mail.send_mail import send_mail_for_contact_form
from app.schemas import mail
from _log_config.log_config import get_logger

contact_logger = get_logger('contact_form', 'contact_form.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

router = APIRouter(
    prefix="/contact-form",
    tags=["contact"],
    responses={404: {"description": "Not found"}},
)

@router.post("/send-email/")
async def send_email(contact: mail.ContactForm):
    try:
        await send_mail_for_contact_form(contact)
        return "Email sent successfully to support team"
    except Exception as e:
<<<<<<< HEAD
        raise HTTPException(status_code=500, detail=str(e))
=======
        contact_logger.error(f"Error sending contact form email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
