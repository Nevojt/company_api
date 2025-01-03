from fastapi import APIRouter
<<<<<<< HEAD
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
=======
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from jinja2 import Environment, FileSystemLoader
from app.config.config import settings
from app.schemas import mail

<<<<<<< HEAD
=======
from _log_config.log_config import get_logger

mail_logger = get_logger('mail', 'send_mail.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
router = APIRouter()

# Налаштування конфігурації
conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)


# # Налаштування Jinja2
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('password_reset.html')

async def password_reset(subject: str, email_to: str, body: dict):
    """
    This function is used to send a password reset email to the user.

    Args:
        subject (str): The subject of the email.
        email_to (str): The email address of the user.
        body (dict): The body of the email, which includes the reset link.

    Returns:
        dict: A dictionary containing a message indicating that the email was sent.

    Raises:
        Exception: An exception is raised if there is an error sending the email.
    """
<<<<<<< HEAD

    html_content = template.render(body)

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='password_reset.html')

    return {"message": "Email has been sent."}
=======
    try:
        html_content = template.render(body)

        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='password_reset.html')

        return {"message": "Email has been sent."}

    except Exception as e:
        mail_logger.error(f"Error sending password reset email: {str(e)}")
        raise Exception("Error sending password reset email.")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


template_mobile = env.get_template('password_reset_mobile.html')
async def password_reset_mobile(subject: str, email_to: str, body: dict):
    """
    This function is used to send a password reset email to the user.

    Args:
        subject (str): The subject of the email.
        email_to (str): The email address of the user.
        body (dict): The body of the email, which includes the reset link.

    Returns:
        dict: A dictionary containing a message indicating that the email was sent.

    Raises:
        Exception: An exception is raised if there is an error sending the email.
    """
<<<<<<< HEAD

    html_content = template_mobile.render(body)

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='password_reset_mobile.html')

    return {"message": "Email has been sent."}
=======
    try:
        html_content = template_mobile.render(body)

        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='password_reset_mobile.html')

        return {"message": "Email has been sent."}

    except Exception as e:
        mail_logger.error(f"Error sending password reset email: {str(e)}")
        raise Exception("Error sending password reset email.")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

template_mail_registration = env.get_template('email.html')

async def send_registration_mail(subject: str, email_to: str, body: dict):
    """
    This function is used to send a registration email to the user.

    Args:
        subject (str): The subject of the email.
        email_to (str): The email address of the user.
        body (dict): The body of the email, which includes the activation link.

    Returns:
        dict: A dictionary containing a message indicating that the email was sent.

    Raises:
        Exception: An exception is raised if there is an error sending the email.
    """
<<<<<<< HEAD
    
    html_content = template_mail_registration.render(body)
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=html_content,
        subtype='html',
    )
    
    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')
=======
    try:
        html_content = template_mail_registration.render(body)
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='email.html')
    except Exception as e:
        mail_logger.error(f"Error sending registration email: {str(e)}")
        raise Exception("Error sending registration email.")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


mail_change_password = env.get_template('mail_change_password.html')
async def send_mail_for_change_password(subject: str, email_to: str, body: dict):
<<<<<<< HEAD
    html_content = mail_change_password.render(body)

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='mail_change_password.html')
    
    
async def send_mail_for_contact_form(contact: mail.ContactForm):
    support_email = "stivax@gmail.com"  # Email служби підтримки
    
    
    html_content = f"""
    <html>
        <body>
            <h1>New Contact Form Submission</h1>
            <p><strong>Name:</strong> {contact.name}</p>
            <p><strong>Email:</strong> {contact.email}</p>
            <p><strong>Subject:</strong> {contact.subject}</p>
            <p><strong>Message:</strong> {contact.message}</p>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject=f"New Contact Message from {contact.name}",
        recipients=[support_email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
=======
    try:
        html_content = mail_change_password.render(body)

        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='mail_change_password.html')
    except Exception as e:
        mail_logger.error(f"Error sending password change email: {str(e)}")
        raise Exception("Error sending password change email.")
    
    
async def send_mail_for_contact_form(contact: mail.ContactForm):
    try:
        support_email = "stivax@gmail.com"  # Email служби підтримки


        html_content = f"""
        <html>
            <body>
                <h1>New Contact Form Submission</h1>
                <p><strong>Name:</strong> {contact.name}</p>
                <p><strong>Email:</strong> {contact.email}</p>
                <p><strong>Subject:</strong> {contact.subject}</p>
                <p><strong>Message:</strong> {contact.message}</p>
            </body>
        </html>
        """

        message = MessageSchema(
            subject=f"New Contact Message from {contact.name}",
            recipients=[support_email],
            body=html_content,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        mail_logger.error(f"Error sending contact form email: {str(e)}")
        raise Exception("Error sending contact form email.")


mail_change_email = env.get_template('email_update.html')
async def send_mail_for_change_email(subject: str,
                                     email_to: str, body: dict):

    try:
        html_content = mail_change_email.render(body)

        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name='mail_change_password.html')

    except Exception as e:
        mail_logger.error(f"Error sending email change email: {str(e)}")
        raise Exception("Error sending email change email.")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
