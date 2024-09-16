from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
            password=utils.hash(user_data["password"]),
            avatar=user_data["avatar"],
            company_id=1
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
                session.add(new_room)
                await session.commit()
            else:
                print("Room 'Hell' already exists, skipping insertion.")
            await create_initial_users(session)