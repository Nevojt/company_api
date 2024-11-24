
from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import async_db

from ...config import utils
from ...auth import oauth2
from app.config.config import settings
from app.models import user_model
from app.schemas.token import Token
from _log_config.log_config import get_logger

# import redis.asyncio as redis
# from contextlib import asynccontextmanager
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

auth_logger = get_logger('auth', "authentication.log")


# @asynccontextmanager
# async def lifespan(_: APIRouter):
#     redis_connection = redis.from_url(f"redis://{settings.redis_url}", encoding="utf8")
#     await FastAPILimiter.init(redis_connection)
#     yield
#     await redis_connection.close()


# router = APIRouter(lifespan=lifespan,
#                 tags=['Authentication'])
# @router.post('/login', response_model=Token, dependencies=[Depends(RateLimiter(times=3, seconds=10)),
#                                                                 Depends(RateLimiter(times=5, minutes=1)),
#                                                                 Depends(RateLimiter(times=10, minutes=10))])
router = APIRouter(
                tags=['Authentication'])



@router.post('/login', response_model=Token)
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: AsyncSession = Depends(async_db.get_async_session)):
#
    """
    OAuth2-compatible token login, get an access token for future requests.

    Args:
    user_credentials (OAuth2PasswordRequestForm): The OAuth2 password request form data.
    db (Session): Dependency that gets the database session.

    Returns:
    JSON object with the access token and the token type.

    Raises:
    HTTPException: 403 Forbidden error if the credentials are invalid.

    The function performs the following steps:
    - Extracts the username and password from the OAuth2PasswordRequestForm.
    - Verifies that a user with the provided email exists in the database.
    - Checks if the provided password is correct.
    - Generates an access token using the user's ID.
    - Returns the access token and the token type as a JSON object.
    """
    try:
        query = select(user_model.User).where(user_model.User.email == user_credentials.username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid Credentials")

        if user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {user.id} is blocked")

        if not user.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {user.id} is not active")
        
        if not utils.verify(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid Credentials")

        access_token = await oauth2.create_access_token(user_id=user.id,
                                                        db=db)
        
        refresh_token = await oauth2.create_refresh_token(user_id=user.id,
                                                          db=db)
        user.refresh_token = refresh_token
        await db.commit()

        # Return the token
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}
        
    except HTTPException as ex_error:
        auth_logger.error(f"Error processing Authentication {ex_error}", exc_info=True)
        # Re-raise HTTPExceptions without modification
        raise
    except Exception as e:
        # Log the exception or handle it as you see fit
        auth_logger.error(f"An error occurred: Authentication {e}", exc_info=True)
        # print(f"An error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while processing the request.")

@router.post("/refresh")
async def refresh_access_token(refresh_token: str,
                               db: AsyncSession = Depends(async_db.get_async_session)):
    """
    Endpoint to refresh an access token using a refresh token.

    Args:
        refresh_token (str): The refresh token to use for refreshing the access token.
        db (AsyncSession): The database session to use for accessing the database.

    Returns:
        JSON: The new access token and its type.

    Raises:
        HTTPException: If the refresh token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("user_id")

        if user_id_str is None:
            raise credentials_exception

        user_id = UUID(user_id_str)
        
        query = select(user_model.User).where(user_model.User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if user is None or user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {user_id} is blocked or does not exist")
        
        if user_id is None:
            raise credentials_exception
        
        new_access_token = await oauth2.create_access_token(user_id=user_id, db=db)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        auth_logger.error(f"Invalid refresh token: {refresh_token}", exc_info=True)
        raise credentials_exception
