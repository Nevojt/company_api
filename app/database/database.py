
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from app.config.config import settings


SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{settings.database_username}:{settings.database_password_test}@{settings.database_hostname_test}:{settings.database_port}/{settings.database_name}'



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
       
while True:   
    try:
        conn = psycopg2.connect(host=settings.database_hostname_company, database=settings.database_name, user=settings.database_username,
                                password=settings.database_password_company, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break

    except Exception as error:
            print('Conection to database failed')
            print("Error:",  error)
            time.sleep(2)