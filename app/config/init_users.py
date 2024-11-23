<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .config import users_data
from fastapi import Depends
from app.database.async_db import get_async_session
from app.models import user_model, room_model
from app.config import utils, config



async def create_initial_users(db: AsyncSession = Depends(get_async_session)):
    users_data = config.users_data

    for user_data in users_data:
        # Check if a user with the same email or user_name already exists
        existing_user = await db.execute(
            select(user_model.User).filter(
                (user_model.User.email == user_data['email']) |
                (user_model.User.user_name == user_data['user_name'])
            )
        )
        existing_user = existing_user.scalars().first()
        if existing_user:
            print(f"User with email {user_data['email']} or username {user_data['user_name']} already exists.")
            continue  # Skip this user

        user = user_model.User(
            user_name=user_data["user_name"],
            email=user_data["email"],
            password=utils.hash_password(user_data["password"]),
            avatar=user_data["avatar"]
        )
        db.add(user)

    await db.commit()
    
    
    
async def create_room(engine_asinc):
        async with AsyncSession(engine_asinc) as session:
        # Check if the room already exists
            existing_room = await session.execute(select(room_model.Rooms).filter_by(name_room='Hell'))
            existing_room = existing_room.scalars().first()
            if existing_room is None:
                new_room = room_model.Rooms(name_room='Hell', image_room='Hell', owner=None, secret_room=True)
=======

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from _log_config.log_config import get_logger

from fastapi import Depends
from app.database.async_db import get_async_session
from app.models import user_model, room_model, company_model
from app.config import start_schema
from app.config.utils import hash, generate_access_code_uuid4
from app.config.start_schema import start_app
from app.settings.get_info import get_room_hell

init_logger = get_logger('init_logger', 'init_user.log')

company_id_uuid4 = generate_access_code_uuid4()


async def create_company(engine_asinc_db):
    try:
        async with AsyncSession(engine_asinc_db) as session:


            if await get_company(session):
                print("Company already exists. Skipping creation.")
                return

            new_company = company_model.Company(
                id=company_id_uuid4,
                name=start_app.company_name,
                subdomain=start_app.company_subdomain,
                contact_email=start_app.company_email,
                contact_phone=start_app.company_phone,
                address=start_app.company_address,
                description=start_app.company_description,
                logo_url=start_app.company_logo
            )
            session.add(new_company)
            await session.commit()
            print("New company created successfully.")
            return new_company
    except Exception as e:
        init_logger.error(f"Error in create_initial_users: {e}")
        print(f"Error in create_company: {e}")


async def create_initial_users(db: AsyncSession = Depends(get_async_session)):
    try:
        users_data = start_schema.users_data
        company_id = await get_company(db)
        hell_room = await get_room_hell(db)
        for user_data in users_data:
            # Check if a user with the same email or user_name already exists
            existing_user = await db.execute(
                select(user_model.User).where(
                    (user_model.User.email == user_data['email']) |
                    (user_model.User.user_name == user_data['user_name'])
                )
            )
            existing_user = existing_user.scalars().first()
            if existing_user:
                print(f"User with email {user_data['email']} or username {user_data['user_name']} already exists.")
                continue  # Skip this user

            user = user_model.User(
                user_name=user_data["user_name"],
                email=user_data["email"],
                password=hash(user_data["password"]),
                avatar=user_data["avatar"],
                company_id=company_id.id
            )
            db.add(user)
            await  db.flush()


            user_status = user_model.UserStatus(user_id=user.id,
                                                user_name=user.user_name,
                                                name_room=hell_room.name_room,
                                                room_id=hell_room.id)
            db.add(user_status)

        await db.commit()
    except Exception as e:
        init_logger.error(f"Error in create_initial_users: {e}")
        print(f"Error in create_initial_users: {e}")


async def create_room(engine_asinc_db):
    try:
        async with AsyncSession(engine_asinc_db) as session:
            company_id = await get_company(session)
            hell = start_app.default_user_name
            #  Create user for room Hell
            existing_user = await session.execute(select(user_model.User).where(user_model.User.user_name == hell))
            existing_user = existing_user.scalar_one_or_none()
            if existing_user is None:

                user = user_model.User(
                    user_name=start_app.default_user_name,
                    email=start_app.default_user_email,
                    password=hash(start_app.default_user_password),
                    avatar=start_app.default_user_avatar,
                    company_id=company_id.id
                )
                session.add(user)
                await  session.flush()
            else:
                print("User Hell already exist, skipping insertion.")

            # Check if the room already exists
            hell_room = await get_room_hell(session)
            if hell_room is None:
                new_room = room_model.Rooms(name_room=start_app.default_room_name,
                                            image_room=start_app.default_room_image,
                                            owner=user.id,
                                            secret_room=True,
                                            company_id=company_id.id)
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
                session.add(new_room)
                await session.commit()
            else:
                print("Room 'Hell' already exists, skipping insertion.")
<<<<<<< HEAD
            await create_initial_users(session)
=======
            await create_initial_users(session)
    except Exception as e:
        init_logger.error(f"Error in create_room: {e}")
        print(f"Error in create_room: {e}")

async def get_company(session):
    try:
        company_subdomain = start_app.company_subdomain
        company_email = start_app.company_email
        existing_company = await session.execute(
            select(company_model.Company).where(
                (company_model.Company.subdomain == company_subdomain) |
                (company_model.Company.contact_email == company_email)
            )
        )
        existing_company = existing_company.scalars().first()
        return existing_company
    except Exception as e:
        init_logger.error(f"Error getting company {e}")
        print(f"Error in get_company: {e}")

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
