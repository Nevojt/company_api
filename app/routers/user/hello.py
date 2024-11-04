
from sqlalchemy import insert
from app.models import messages_model
from app.database.async_db import async_session_maker







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


async def say_hello_system(receiver_id: int):
    """
    Say hello to a user.

    Args:
        receiver_id (int): The ID of the recipient."""
        
    async with async_session_maker() as session:
        for message in messages:
            # await asyncio.sleep(5)
            stmt = insert(messages_model.PrivateMessage).values(message=message, sender_id=2, receiver_id=receiver_id)
            await session.execute(stmt)
            await session.commit()


async def system_notification_sayory(receiver_id: int, message: str):
    """
    Sends a system notification to a specific user.

    This function inserts a new private message into the database representing a system notification.
    The message is sent from a predefined sender (system) to the specified receiver.

    Parameters:
    - receiver_id (int): The ID of the recipient user.
    - message (str): The content of the system notification message.

    Returns:
    - None: This function does not return any value.

    Example:
    # >>> system_notification_sayory(123, "This is a system notification.")
    """

    async with async_session_maker() as session:
 
        stmt = insert(messages_model.PrivateMessage).values(message=message, sender_id=2, receiver_id=receiver_id)
        await session.execute(stmt)
        await session.commit()