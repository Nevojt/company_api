
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from app.config.config import settings


<<<<<<< HEAD
SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{settings.database_name}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_username}'
=======
SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{settings.database_name}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_username}'

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def get_db():
    """
    Creates a new database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# test session database
<<<<<<< HEAD
       
while True:   
    try:
        conn = psycopg2.connect(host=settings.database_hostname, database=settings.database_name, user=settings.database_username,
                                password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break

    except Exception as error:
            print('Connection to database failed')
            print("Error:",  error)
            time.sleep(2)
=======
#
# while True:
#     try:
#         conn = psycopg2.connect(host=settings.database_hostname_company, database=settings.database_name_company, user=settings.database_username_company,
#                                 password=settings.database_password_company, cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection was successful")
#         break
#
#     except Exception as error:
#             print('Connection to database failed')
#             print("Error:",  error)
#             time.sleep(2)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
