
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import Depends
from app.database.async_db import get_async_session
from app.models import user_model, room_model, company_model
from app.config import utils, start_schema
from app.config.start_schema import start_app

company_id_uuid4 = utils.generate_access_code_uuid4()


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
        print(f"Error in create_company: {e}")


async def create_initial_users(db: AsyncSession = Depends(get_async_session)):
    users_data = start_schema.users_data
    company_id = await get_company(db)
    hell_room = await get_room_hell(db)
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
            avatar=user_data["avatar"],
            company_id=company_id.id
        )
        db.add(user)
        await  db.flush()


        user_status = user_model.User_Status(user_id=user.id,
                                             user_name=user.user_name,
                                             name_room=hell_room.name_room,
                                             room_id=hell_room.id)
        db.add(user_status)

    await db.commit()


async def create_room(engine_asinc_db):
    try:
        async with AsyncSession(engine_asinc_db) as session:
            company_id = await get_company(session)
            hell = start_app.default_user_name
            #  Create user for room Hell
            existing_user = await session.execute(select(user_model.User).filter_by(user_name=hell))
            existing_user = existing_user.scalars().first()
            if existing_user is None:

                user = user_model.User(
                    user_name=start_app.default_user_name,
                    email=start_app.default_user_email,
                    password=utils.hash_password(start_app.default_user_password),
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
                session.add(new_room)
                await session.commit()
            else:
                print("Room 'Hell' already exists, skipping insertion.")
            await create_initial_users(session)
    except Exception as e:
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
        print(f"Error in get_company: {e}")

async def get_room_hell(session):
    hell = start_app.default_room_name
    existing_room = await session.execute(select(room_model.Rooms).filter_by(name_room=hell))
    existing_room = existing_room.scalars().first()
    return existing_room
