

<<<<<<< HEAD
from sched import scheduler
=======
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .mail import send_mail

<<<<<<< HEAD
from .routers.user import auth, finds, user, verify_user, user_status, company_user
from .routers.messages import message, private_messages, vote
from .routers.images import images, upload_file_google, upload_file_supabase, upload_and_return, upload_file_backblaze
from .routers.room import rooms, count_users_messages, secret_rooms, tabs_rooms, user_rooms, ban_user, role_in_room
=======
from .routers.user import auth, user, verify_user, user_status, company_user
from .routers.search import finds
from .routers.firebase import user_tokens
from .routers.messages import message, private_messages, vote
from .routers.images import upload_file_backblaze
from .routers.room import rooms, count_users_messages, secret_rooms, user_rooms, ban_user, role_in_room
from .routers.tabs import tabs_rooms
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from .routers.invitations import invitation_secret_room
from .routers.following import following
from .routers.token_test import ass
from .routers.reset import password_reset, password_reset_mobile, change_and_block
<<<<<<< HEAD
from .routers.mail import contact_form
from .routers.company import company
from .routers.reports import report_to_reason

from .config.scheduler import setup_scheduler#, scheduler
from app.config.init_users import create_room
from .database.database import engine
from app.database.async_db import async_session_maker, engine_asinc
from app.models import following_model, user_model, room_model, image_model, password_model, company_model, messages_model, reports_model

from app.admin import user as admin_user
from app.admin import room as admin_room

from app.routers.AI import sayory_router


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.async_db import get_async_session
from .config import config, utils
=======
from .routers.mail import contact_form, update_mail
# from .superAdmin import company
from .routers.reports import report_to_reason

from .config.scheduler import setup_scheduler#, scheduler
from app.config.init_users import create_room, create_company

from app.database.async_db import async_session_maker, engine_async
from app.models import user_model, room_model, password_model, company_model, messages_model
from app.models import following_model, reports_model

from app.admin.company import company as admin_company
from app.admin.room import room as admin_room

from app.routers.AI import sayory_router

# import sentry_sdk
# from app.config.config import settings
#
#
# sentry_sdk.init(
#     dsn=settings.sentry_url,
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )


>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824



async def init_db():
<<<<<<< HEAD
    async with engine_asinc.begin() as conn:
        try:
            await conn.run_sync(user_model.Base.metadata.create_all)
            await conn.run_sync(room_model.Base.metadata.create_all)
            await conn.run_sync(image_model.Base.metadata.create_all)
=======
    async with engine_async.begin() as conn:
        try:
            await conn.run_sync(user_model.Base.metadata.create_all)
            await conn.run_sync(room_model.Base.metadata.create_all)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
            await conn.run_sync(password_model.Base.metadata.create_all)
            await conn.run_sync(company_model.Base.metadata.create_all)
            await conn.run_sync(messages_model.Base.metadata.create_all)
            await conn.run_sync(following_model.Base.metadata.create_all)
            await conn.run_sync(reports_model.Base.metadata.create_all)
            print("All tables created successfully.")
        except Exception as e:
            print(f"Error during table creation: {e}")
<<<<<<< HEAD

        await create_room(engine_asinc)
        
    
    
# Setup Scheduler    
def startup_event():
    setup_scheduler(async_session_maker)
    
async def on_shutdown():
    scheduler.shutdown()
=======
        try:
            await create_company(engine_async)
            await create_room(engine_async)

        except Exception as e:
            print(f"Error during table creation: {e}")
        

def startup_event():
    setup_scheduler(async_session_maker)
    
# async def on_shutdown():
#     scheduler.shutdown()
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

app = FastAPI(
    root_path="/api",
    docs_url="/docs",
<<<<<<< HEAD
    title="Chat",
    description="Chat documentation",
    version="0.1.5",
    on_startup=[init_db, startup_event],
    # on_shutdown=[on_shutdown]
)

=======
    redoc_url="/new-redoc-url",
    title="Chat Company",
    description="Chat documentation Company",
    version="0.1.5.1.4",
    on_startup=[init_db, startup_event],
    # on_shutdown=[on_shutdown]
    license_info={
        "name": "Apache License",
        "version": "2.0.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)


>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD



=======
# Setup Scheduler

# @app.get("/sentry-debug")
# async def trigger_error():
#     division_by_zero = 1 / 0
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


app.include_router(message.router)

app.include_router(report_to_reason.router)
<<<<<<< HEAD

=======
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
app.include_router(rooms.router)
app.include_router(user_rooms.router)
app.include_router(secret_rooms.router)
app.include_router(invitation_secret_room.router)
app.include_router(tabs_rooms.router)
app.include_router(ban_user.router)
app.include_router(role_in_room.router)

app.include_router(following.router)

app.include_router(user.router)
<<<<<<< HEAD
=======
app.include_router(user_tokens.router)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
app.include_router(auth.router)
app.include_router(finds.router)
app.include_router(user_status.router)
app.include_router(vote.router)

<<<<<<< HEAD
app.include_router(images.router)
app.include_router(upload_file_backblaze.router)
app.include_router(upload_file_supabase.router)
app.include_router(upload_file_google.router)
app.include_router(upload_and_return.router)
=======
app.include_router(upload_file_backblaze.router)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

app.include_router(private_messages.router)
app.include_router(count_users_messages.router)
app.include_router(password_reset.router)
app.include_router(password_reset_mobile.router)

app.include_router(change_and_block.router)

app.include_router(send_mail.router)
app.include_router(contact_form.router)
<<<<<<< HEAD
=======
app.include_router(update_mail.router)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

app.include_router(verify_user.router)

# Check token
app.include_router(ass.router)

# Company routes
<<<<<<< HEAD
app.include_router(company.router)
app.include_router(company_user.router)

# Admin routes
app.include_router(admin_user.router)
=======
# app.include_router(company.router)
app.include_router(company_user.router)

# Admin routes
app.include_router(admin_company.router)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
app.include_router(admin_room.router)

# AI routes
app.include_router(sayory_router.router)




app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("home_page.html", {"request": request})


@app.get("/reset", include_in_schema=False)
async def read_reset(request: Request):
    return templates.TemplateResponse("window_new_password.html", {"request": request})

@app.get("/success-page", include_in_schema=False)
async def finally_reset(request: Request):
    return templates.TemplateResponse("success-page.html", {"request": request})

@app.get('/privacy-policy', include_in_schema=False)
async def privacy_policy():
    return RedirectResponse(url="https://sayorama.eu/chat#/PrivacyPolicy", status_code=307)

app.mount("/contact-form", StaticFiles(directory="contact-form"), name="contact-form")
templates_form = Jinja2Templates(directory="contact-form")

@app.get('/contact-form', include_in_schema=False)
async def contact_form(request: Request):
    return templates_form.TemplateResponse("index.html", {"request": request})



def get_company_from_subdomain(request: Request):
    host = request.headers.get("host")
    subdomain = host.split(".")[0]
    
    return subdomain

@app.get("/company")
async def get_company(company: str = Depends(get_company_from_subdomain)):
    return {"company": company}

