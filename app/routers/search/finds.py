

from _log_config.log_config import get_logger
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.async_db import get_async_session
from app.config.start_schema import start_app

from app.routers.search.func_search import get_search_users, get_search_rooms

logger = get_logger('finds', 'finds.log')

router = APIRouter(
    prefix="/search",
    tags=['Search'],
)

hell = start_app.default_room_name

@router.get('/{substring}')
async def search_users_and_rooms(substring: str,
                                db: AsyncSession = Depends(get_async_session)):
    """
    Search for users and rooms based on a substring.

    Parameters:
    - `substring`: The substring to filter by. This parameter is case-insensitive.
    - `db`: The database session. It is injected by the `get_db` function.

    Returns:
    - A dictionary containing a list of users and rooms that match the search criteria.
      Each user is represented as a dictionary with the following keys:
      - `id`: The user's unique identifier.
      - `user_name`: The user's name.
      - `avatar`: The user's avatar URL.
      - `created_at`: The date and time when the user was created.
      Each room is represented as a dictionary with the following keys:
      - `id`: The room's unique identifier.
      - `owner`: The room's owner.
      - `name_room`: The room's name.
      - `image_room`: The room's image URL.
      - `count_users`: The number of users in the room.
      - `count_messages`: The number of messages in the room.
      - `created_at`: The date and time when the room was created.
      - `secret_room`: A boolean indicating whether the room is a secret room.

    The function uses SQLAlchemy's ORM to query the database and filter users and rooms based on the provided substring.
    It also counts the number of users and messages in each room.
    """
    pattern = f"%{substring.lower()}%"

    try:
        # Search for users
        users_info_list = await get_search_users(pattern, db)

        # Search for rooms
        rooms_info_list = await get_search_rooms(pattern, db)

        # Return the results
        return {
            "users": users_info_list,
            "rooms": rooms_info_list
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {e}")
    
@router.get("/users/{substring}")
async def search_users(substring: str,
                 db: AsyncSession = Depends(get_async_session)):
    """
    Search for users based on a substring.

    Parameters:
    - `substring`: The substring to filter by. This parameter is case-insensitive.
    - `db`: The database session. It is injected by the `get_db` function.

    Returns:
    - A dictionary containing a list of users that match the search criteria.
      Each user is represented as a dictionary with the following keys:
      - `id`: The user's unique identifier.
      - `user_name`: The user's name.
      - `avatar`: The user's avatar URL.
      - `created_at`: The date and time when the user was created.

    The function uses SQLAlchemy's ORM to query the database and filter users based on the provided substring.
    """
    pattern = f"%{substring.lower()}%"

    try:
        # Search for users
        user_list = await get_search_users(pattern, db)

        return {"users": user_list}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {e}")


@router.get("/rooms/{substring}")
async def search_rooms(substring: str,
                        db: AsyncSession = Depends(get_async_session)):
    """
    Search for users based on a substring.

    Parameters:
    - `substring`: The substring to filter by. This parameter is case-insensitive.
    - `db`: The database session. It is injected by the `get_db` function.

    Returns:
    - A dictionary containing a list of users that match the search criteria.
      Each user is represented as a dictionary with the following keys:
      - `id`: The user's unique identifier.
      - `user_name`: The user's name.
      - `avatar`: The user's avatar URL.
      - `created_at`: The date and time when the user was created.

    The function uses SQLAlchemy's ORM to query the database and filter users based on the provided substring.
    """
    pattern = f"%{substring.lower()}%"

    try:
        rooms_info_list = await get_search_rooms(pattern, db)

        # Return the results
        return {"rooms": rooms_info_list}

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {e}",
        )