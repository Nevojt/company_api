

from sched import scheduler
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .mail import send_mail

from .routers.user import auth, finds, user, verify_user, user_status, company_user
from .routers.messages import message, private_messages, vote
from .routers.images import images, upload_file_supabase, upload_and_return, upload_file_backblaze
from .routers.room import rooms, count_users_messages, secret_rooms, tabs_rooms, user_rooms, ban_user, role_in_room
from .routers.invitations import invitation_secret_room
from .routers.token_test import ass
from .routers.reset import password_reset, password_reset_mobile, change_and_block
from .routers.mail import contact_form, update_mail
from .routers.company import company
from .routers.reports import report_to_reason
from .routers.mail import contact_form
from .superAdmin import company

from .config.scheduler import setup_scheduler#, scheduler
from app.config.init_users import create_room, create_company

from app.config.init_users import create_room, create_company
from app.database.async_db import async_session_maker, engine_asinc
from app.models import user_model, room_model, image_model, password_model, company_model, messages_model
from app.models import following_model, reports_model

from app.admin import user as admin_user
from app.admin import room as admin_room

from app.routers.AI import sayory_router


async def init_db():
    async with engine_asinc.begin() as conn:
        try:
            await conn.run_sync(user_model.Base.metadata.create_all)
            await conn.run_sync(room_model.Base.metadata.create_all)
            await conn.run_sync(image_model.Base.metadata.create_all)
            await conn.run_sync(password_model.Base.metadata.create_all)
            await conn.run_sync(company_model.Base.metadata.create_all)
            await conn.run_sync(messages_model.Base.metadata.create_all)
            await conn.run_sync(following_model.Base.metadata.create_all)
            await conn.run_sync(reports_model.Base.metadata.create_all)
            print("All tables created successfully.")
        except Exception as e:
            print(f"Error during table creation: {e}")
        try:
            await create_company(engine_asinc)
            await create_room(engine_asinc)

        except Exception as e:
            print(f"Error during table creation: {e}")
        

def startup_event():
    setup_scheduler(async_session_maker)
    
async def on_shutdown():
    scheduler.shutdown()

app = FastAPI(
    root_path="/api",
    docs_url="/docs",
    redoc_url="/new-redoc-url",
    title="Chat Public",
    description="Chat documentation Public",
    version="0.1.5.1",
    on_startup=[init_db, startup_event],
    # on_shutdown=[on_shutdown]
)

# origins = ["31.220.75.30:8000"]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Scheduler




app.include_router(message.router)

app.include_router(report_to_reason.router)

app.include_router(rooms.router)
app.include_router(user_rooms.router)
app.include_router(secret_rooms.router)
app.include_router(invitation_secret_room.router)
app.include_router(tabs_rooms.router)
app.include_router(ban_user.router)
app.include_router(role_in_room.router)

app.include_router(following.router)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(finds.router)
app.include_router(user_status.router)
app.include_router(vote.router)

app.include_router(images.router)
app.include_router(upload_file_backblaze.router)
app.include_router(upload_file_supabase.router)
# app.include_router(upload_file_google.router)
app.include_router(upload_and_return.router)

app.include_router(private_messages.router)
app.include_router(count_users_messages.router)
app.include_router(password_reset.router)
app.include_router(password_reset_mobile.router)

app.include_router(change_and_block.router)

app.include_router(send_mail.router)
app.include_router(contact_form.router)
app.include_router(update_mail.router)

app.include_router(verify_user.router)

# Check token
app.include_router(ass.router)

# Company routes
app.include_router(company.router)
app.include_router(company_user.router)

# Admin routes
app.include_router(admin_user.router)
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
async def get_company(company_name: str = Depends(get_company_from_subdomain)):
    return {"company": company_name}

