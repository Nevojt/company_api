from fastapi import HTTPException, status
from sqlalchemy import insert
from app.models import messages_model
from app.database.async_db import async_session_maker
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import user_model
from app.config.crypto_encrypto import async_encrypt


messages = ["👋 Вітаю! Я тут, щоб розповісти про можливості нашого додатку.",
            "Цей чат – приватний, тому твоє спілкування відбувається в режимі 1-to-1.",
            "🕵️‍♂️ Всі повідомлення шифруються і надсилаються через безпечний канал зв'язку.",
            "Ти можеш надсилати повідомлення, посилання, ставити лайки (подвійний тап) та відповідати на вибране повідомлення (свайп). 👍",
            "Такі опції доступні в кожному чаті, форумі чи кімнаті.",
            "Ми створили різноманітні публічні кімнати, де ти можеш долучатися до обговорення будь-яких тем. Знайди своє улюблене місце та приєднуйся до спільноти! 🗣️🌍,",
            "Ще більше! Ти можеш створити власну кімнату, вибрати для неї назву та обкладинку. 🖼️ Також ти можеш додати вибрану кімнату до свого списку улюблених місць. 📝,",
            "Під час створення кімнати ти можеш обрати її приватність.",
            "Створивши приватну кімнату, ти, як власник, зможеш додавати до неї користувачів або видаляти їх. Така кімната буде вашим маленьким таємним куточком! 🤫🔐",
            "Зверни увагу, оскільки додаток ще в розробці, можливі деякі технічні проблеми (вибачте за незручності). 🛠️",
            "Ми завжди раді чути твої пропозиції та побажання! 💬",
            "З любов'ю, команда розробників. 💖"]


async def say_hello_system(receiver_id: UUID):

    async with async_session_maker() as session:
        sayory = await get_sayory(db=session)
        for message in messages:
            encrypted_message = await async_encrypt(message)
            await insert_sayory(message=encrypted_message,
                                receiver_id=receiver_id,
                                sender_id=sayory.id,
                                session=session)


async def system_notification_change_owner(receiver_id: UUID,
                                           message: str):
    try:
        async with async_session_maker() as session:
            sayory = await get_sayory(db=session)
            encrypted_message = await async_encrypt(message)
            await insert_sayory(message=encrypted_message,
                                receiver_id=receiver_id,
                                sender_id=sayory.id,
                                session=session)
    except Exception as e:
        print(f"Error in system_notification_change_owner: {e}")
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT,
                            detail="Error in system_notification_change_owner")


async  def get_sayory(db: AsyncSession):
    try:
        sayory_query = await db.execute(select(user_model.User).where(user_model.User.user_name == "SayOry"))
        sayory = sayory_query.scalar_one()
        return sayory
    except Exception as e:
        print(f"Error in get_sayory: {e}")
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT,
                            detail="Error in get_sayory")


async def insert_sayory(message: str,
                        receiver_id: UUID,
                        sender_id: UUID,
                        session: AsyncSession):
    try:
        stmt = insert(messages_model.PrivateMessage).values(message=message,
                                                            sender_id=sender_id,
                                                            receiver_id=receiver_id)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        print(f"Error in insert_sayory: {e}")
        raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT,
                            detail="Error in insert_sayory")
