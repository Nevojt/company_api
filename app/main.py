
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import message, user, rooms, auth, user_status, vote, images, soket
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(message.router)
app.include_router(rooms.router)
app.include_router(auth.router)
app.include_router(user_status.router)
app.include_router(vote.router)
app.include_router(images.router)
app.include_router(soket.router)

app.include_router(user.router)

