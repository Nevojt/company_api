import time
from dotenv import load_dotenv

load_dotenv()
import os

from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor


from . import models
from .database import engine
from .routers import message, user, rooms, auth, user_status


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")



models.Base.metadata.create_all(bind=engine)

app = FastAPI()


    
while True:   
    try:
        conn = psycopg2.connect(host=url, database='postgres', user='postgres',
                                password=key, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break

    except Exception as error:
            print('Conection to database failed')
            print("Error:",  error)
            time.sleep(2)
    
my_post = [{"name": "big boss", "message": "content of post 1", "id": 1}, 
           {"name": "litle foot", "message":"favorite Pizza", "id": 2 }]


def find_post(id):
    for p in my_post:
        if p["id"] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_post):
        if p["id"] == id:
            return i

app.include_router(message.router)
app.include_router(rooms.router)
app.include_router(auth.router)
app.include_router(user_status.router)

app.include_router(user.router)