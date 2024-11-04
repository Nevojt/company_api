
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from app.config.config import settings





ASINC_SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{settings.database_name_company}:{settings.database_password_company}@{settings.database_hostname_company}:{settings.database_port}/{settings.database_username_company}'

engine_asinc = create_async_engine(ASINC_SQLALCHEMY_DATABASE_URL)
async_session_maker = sessionmaker(bind=engine_asinc,
                                   class_=AsyncSession,
                                   expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session