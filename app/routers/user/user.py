from datetime import datetime
from typing import List
from _log_config.log_config import get_logger
import pytz

from fastapi import Form, Response, status, HTTPException, Depends, APIRouter, UploadFile, File, Path
from fastapi import BackgroundTasks
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from app.config.config import settings
from app.config.default_info import get_default_user
from app.routers.AI.hello import say_hello_system, system_notification_change_owner
from app.mail import send_mail
from app.models import user_model, room_model
from app.schemas import user

from app.settings.get_info import (get_company, get_user, get_room_hell,
                                   get_user_for_email, get_user_for_username, check_deactivation_user,
                                   has_verified_or_blocked_user)

from app.config.created_image import generate_image_with_letter
from ...auth import oauth2
from ...config import utils, crypto_encrypto
from ...config.start_schema import start_app
from ...database.async_db import get_async_session

user_logger = get_logger('user', 'user.log')

router = APIRouter(
    prefix="/users",
    tags=['Users'],
)


@router.post("/v2", status_code=status.HTTP_201_CREATED, response_model=user.UserOut)
async def created_user_v2(background_tasks: BackgroundTasks,
                          company: str = Form("sayorama"),
                          email: EmailStr = Form(...),
                          user_name: str = Form(...),
                          full_name: str = Form(None),
                          password: str = Form(...),
                          file: UploadFile = File(None),
                          description: str = Form(None),
                          db: AsyncSession = Depends(get_async_session)):
    try:
        start = datetime.now()
        company = await get_company(company, db)
        hell = await get_room_hell(db)

        deactivated_user = await check_deactivation_user(email, user_name, db)

        if deactivated_user:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                detail=f"User with email {email} or user_name {user_name} is deactivated")

        # Check if a user with the given email already exists
        existing_email_user = await get_user_for_email(email, db)

        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                detail=f"User with email {existing_email_user} already exists")

        # Check if a user with the given user_name already exists
        username_query = await get_user_for_username(user_name, db)

        if username_query:
            raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                                detail=f"User with user_name {username_query} already exists")

        user_data = user.UserCreateV2(email=email,
                                      user_name=user_name,
                                      password=password,
                                      company_id=company.id)


        # Hash the user's password
        hashed_password = utils.hash(user_data.password)
        user_data.password = hashed_password

        verification_token = await crypto_encrypto.generate_encrypted_token(user_data.email)

        if file is None:
            generate_image_with_letter(user_name)
            avatar = await utils.upload_to_backblaze(settings.rout_image, settings.bucket_name_user_avatar)
        else:
            avatar = await utils.upload_to_backblaze(file, settings.bucket_name_user_avatar)

        # Create a new user and add it to the database
        new_user = user_model.User(**user_data.model_dump(),
                               avatar=avatar,
                               description=description,
                                full_name=full_name,
                               token_verify=verification_token)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Create a User_Status entry for the new user
        post = user_model.UserStatus(user_id=new_user.id,
                                     user_name=new_user.user_name,
                                     name_room=hell.name_room,
                                     room_id=hell.id)
        db.add(post)
        await db.commit()
        await db.refresh(post)

        # Offload email sending and system notification to BackgroundTasks
        registration_link = f"https://{settings.url_address_dns}/api/success_registration?token={new_user.token_verify}"
        background_tasks.add_task(send_mail.send_registration_mail,
                                  "Thank you for registration!",
                                  new_user.email,
                                  {
                                      "title": "Registration",
                                      "name": user_data.user_name,
                                      "registration_link": registration_link
                                  })
        background_tasks.add_task(say_hello_system, new_user.id)
        finish = datetime.now() - start
        print(f"Create User Time: {finish}")
        return new_user
    except Exception as e:
        user_logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    password: user.UserDelete,
    db: AsyncSession = Depends(get_async_session), 
    current_user: user_model.User = Depends(oauth2.get_current_user)
):
    """
    Asynchronously deletes a user from the database.

    This endpoint allows a user to delete their own profile by providing their user ID and password. It performs several checks to ensure that the user is allowed to delete the profile, such as verifying the user's identity, checking the existence of the user, and ensuring the user is verified and authorized to perform the deletion.

    Parameters:
    - id (int): The unique identifier of the user to be deleted.
    - password (str): The password of the user to authenticate the deletion request.
    - db (AsyncSession): The database session used to perform database operations.
    - current_user (int): The user ID obtained from the current user session, used to ensure a user can only delete their own profile.

    Raises:
    - HTTPException: If the current user is not the user being deleted, if the user does not exist, if the user is not verified, or if the provided password is incorrect.

    Returns:
    - Response: An empty response with a 204 No Content status, indicating successful deletion.
    """
    try:

        if not current_user.verified or current_user.blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified users can delete their profiles or user in blocked."
            )

        if not utils.verify(password.password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )

        query_room = select(room_model.Rooms).where(room_model.Rooms.owner == current_user.id)
        result_room = await db.execute(query_room)
        rooms_to_update = result_room.scalars().all()

        default_user = await get_default_user(db)

        for room in rooms_to_update:
            query_moderators = select(room_model.RoleInRoom).where(room_model.RoleInRoom.room_id == room.id, room_model.RoleInRoom.role == 'moderator')
            result_moderators = await db.execute(query_moderators)
            moderator = result_moderators.scalars().first()

            message = f"Room {room.name_room} is now owned by YOU"
            if moderator:
                room.owner = moderator.user_id
                moderator.role = 'owner'
                await system_notification_change_owner(moderator.user_id, message)
            else:
                room.owner = default_user.id
            room.delete_at = datetime.now(pytz.utc)

        await db.commit()

        # delete user
        await db.delete(current_user)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        user_logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    
    
@router.put('/v2/avatar')
async def update_user_v2(file: UploadFile = File(...), 
                        db: AsyncSession = Depends(get_async_session),
                        current_user: user_model.User = Depends(oauth2.get_current_user)):

    try:
        if not current_user.verified or current_user.blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not verification or blocked."
            )

        user_data = await get_user(current_user.id, db=db)

        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID: {current_user.id} not found"
            )

        avatar_url = await utils.upload_to_backblaze(file, settings.bucket_name_user_avatar)

        user_data.avatar = avatar_url
        await db.commit()
        return "updated avatar"

    except Exception as e:
        user_logger.error(f"Error updating user avatar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put('/v2/description')
async def description_user_v2(description: str = Form(...), 
                        db: AsyncSession = Depends(get_async_session),
                        current_user: user_model.User = Depends(oauth2.get_current_user)):

    try:
        if not current_user.verified or current_user.blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not verification or blocked."
            )

        user_data = await get_user(current_user.id, db=db)

        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID: {current_user.id} not found"
            )

        user_data.description = description
        await db.commit()
        return "updated description"

    except Exception as e:
        user_logger.error(f"Error updating user description: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put('/v2/username/{user_name}')
async def update_user_name_v2(user_name: str = Path(..., description="The username to update"),
                        db: AsyncSession = Depends(get_async_session),
                        current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Update a user's username.

    This function updates the username of the currently authenticated user in the database.
    It checks if the user is verified and not blocked before performing the update.
    If the user is not verified or blocked, it raises an HTTPException with a 403 status code.
    If the user is not found in the database, it raises an HTTPException with a 404 status code.

    Parameters:
    - user_name (str): The new username to be updated. This parameter is obtained from the request form.
    - db (Session): The database session to use for querying and updating the user's information.
    - current_user (user_model.User): The currently authenticated user. This parameter is obtained from the dependency injection.

    Returns:
    - str: A string indicating that the username has been updated.

    Raises:
    - HTTPException: If the user is not verified or blocked, or if the user is not found in the database.
    """
    try:
        if not current_user.verified or current_user.blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not verification or blocked."
            )

        user_data = await get_user(current_user.id, db=db)

        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID: {current_user.id} not found"
            )

        user_status_query = await db.execute(select(user_model.UserStatus).filter(user_model.UserStatus.user_id == current_user.id))
        user_status = user_status_query.scalar_one_or_none()

        if user_status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User status for ID: {current_user.id} not found"
            )


        user_data.user_name = user_name
        user_status.user_name = user_name
        await db.commit()

        return "updated username"
    except Exception as e:
        user_logger.error(f"Error updating user username: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put('/full_name/')
async def update_full_name(full_name: str = Form(...),
                        db: AsyncSession = Depends(get_async_session),
                        current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        if await has_verified_or_blocked_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not verification or blocked."
            )
        user_data = await get_user(current_user.id, db=db)
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID: {current_user.id} not found"
            )
        user_data.full_name = full_name
        await db.commit()
        return "updated full name"
    except Exception as e:
        user_logger.error(f"Error updating user full name: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/{email}', response_model=user.UserInfo)
async def get_user_mail(email: EmailStr,
                        db: AsyncSession = Depends(get_async_session)):
    """
    Get a user by their email.

    Parameters:
    email (str): The email of the user to retrieve.
    db (Session): The database session to use.

    Returns:
    schemas.UserInfo: The user information, if found.

    Raises:
    HTTPException: If the user is not found.
    """
    
    # Query the database for a user with the given email
    try:
        user_email = await get_user_for_email(email, db)

        # If the user is not found, raise an HTTP 404 error
        if not user_email:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                                detail=f"User with email {email} not found")

        return user_email
    except Exception as e:
        user_logger.error(f"Error retrieving user by email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/audit/{user_name}', response_model=user.UserInfo)
async def get_user_name(user_name: str,
                  db: AsyncSession = Depends(get_async_session)):
    """
    Get a user by their use_name.

    Parameters:
    user_name (str): The user_name of the user to retrieve.
    db (Session): The database session to use.

    Returns:
    schemas.UserInfo: The user information, if found.

    Raises:
    HTTPException: If the user is not found.
    """
    
    # Query the database for a user with the given email
    try:
        user_result = await get_user_for_username(user_name, db)

        # If the user is not found, raise an HTTP 404 error
        if not user_result:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                                detail=f"User with user name {user_name} not found")

        return user_result
    except Exception as e:
        user_logger.error(f"Error retrieving user by name: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/me/', response_model=user.UserInfo)
async def read_current_user(current_user: user.UserOut = Depends(oauth2.get_current_user)):
    """
    Get the currently authenticated user.

    Parameters:
    current_user (schemas.UserOut): The currently authenticated user.

    Returns:
    schemas.UserInfo: The user information.
    """
    return current_user

@router.get("/", response_model=List[user.UserInfo], include_in_schema=False)
async def read_users(db: AsyncSession = Depends(get_async_session)):
    """
    Retrieve a list of users.
    """
    query = select(user_model.User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users



@router.post("/test", status_code=status.HTTP_201_CREATED, response_model=user.UserOut, include_in_schema=False)
async def created_user_test(user: user.UserCreateDel,
                            db: AsyncSession = Depends(get_async_session)):
    """
    This function creates a new user in the database. It takes a UserCreateDel object as input, which contains the user's details.

    Parameters:
    - user (user.UserCreateDel): An object containing the user's details, including their email, password
    - db (AsyncSession): The database session used to perform database operations.

    The function performs the following steps:
    1. Hashes the user's password using the utils.hash() function.
    2. Creates a new User object using the user.model_dump() method.
    3. Adds the new user to the database using the db.add() method.
    4. Commits the changes to the database using the await db.commit() method.
    5. Refreshes the new user object in the database using the await db.refresh() method.
    6. Creates a new User_Status object for the new user.
    7. Adds the new User_Status object to the database using the db.add() method.
    8. Commits the changes to the database using the await db.commit() method.
    9. Refreshes the new User_Status object in the database using the await db.refresh() method.
    10. Returns the new user object.
    """
    # Hash the user's password
    company = await get_company(start_app.company_subdomain, db)
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    # Create a new user and add it to the database
    new_user = user_model.User(**user.model_dump(),
                               company_id=company.id)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    hell = await get_room_hell(db)
    # Create a User_Status entry for the new user
    post = user_model.UserStatus(user_id=new_user.id, user_name=new_user.user_name,
                                 name_room=hell.name_room, room_id=hell.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return new_user








#  OLD CODE


# @router.post("/", status_code=status.HTTP_201_CREATED, response_model=user.UserOut)
# async def created_user(user: user.UserCreate, db: AsyncSession = Depends(get_async_session)):
#     """
#     This function creates a new user in the database.
#
#     Args:
#         user (schemas.UserCreate): The user data to create.
#         db (AsyncSession): The database session to use.
#
#     Returns:
#         schemas.UserOut: The newly created user.
#
#     Raises:
#         HTTPException: If a user with the given email already exists.
#     """
#
#     # Check if a user with the given email already exists
#     query = select(user_model.User).where(user_model.User.email == user.email)
#     result = await db.execute(query)
#     existing_user = result.scalar_one_or_none()
#
#     if existing_user:
#         raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
#                             detail=f"User {existing_user.email} already exists")
#
#     # Hash the user's password
#     hashed_password = utils.hash_password(user.password)
#     user.password = hashed_password
#
#     verification_token = utils.generate_unique_token(user.email)
#
#     # Create a new user and add it to the database
#     new_user = user_model.User(**user.model_dump(),
#                                token_verify=verification_token)
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)
#
#     # Create a User_Status entry for the new user
#     post = user_model.User_Status(user_id=new_user.id, user_name=new_user.user_name, name_room="Hell", room_id=1)
#     db.add(post)
#     await db.commit()
#     await db.refresh(post)
#
#     registration_link = f"http://{settings.url_address_dns}/api/success_registration?token={new_user.token_verify}"
#     await send_mail.send_registration_mail("Thank you for registration!", new_user.email,
#                                            {
#                                                "title": "Registration",
#                                                "name": user.user_name,
#                                                "registration_link": registration_link
#                                            })
#     await say_hello_system(new_user.id)
#
#     return new_user