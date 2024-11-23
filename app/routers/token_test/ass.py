
from fastapi import APIRouter, Response, status, HTTPException, Depends
<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.async_db import get_async_session
from sqlalchemy.future import select
=======
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.async_db import get_async_session
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from app.auth import oauth2
from app.models.user_model import User


router = APIRouter(tags=['ASS'])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.get('/ass')
<<<<<<< HEAD
async def ass_endpoint(token: str, db: AsyncSession = Depends(get_async_session)):
=======
async def ass_endpoint(token: str,
                    db: AsyncSession = Depends(get_async_session)):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """_summary_

    Args:
        token (str): token verification
<<<<<<< HEAD
        session (Session, optional): session database. Defaults to Depends(get_db).
=======
        db (Session, optional): session database. Defaults to Depends(get_db).
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

    Raises:
        HTTPException:: Token not validation

    Returns:
        Response: return server
    """
    
    try:
        user_data = await oauth2.verify_access_token(token, credentials_exception, db)
        user_query = select(User).where(User.id == user_data.id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
<<<<<<< HEAD
        
        if user.blocked == True:
=======

        if user.blocked:
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {user.id} is blocked")

            
        return Response(status_code=status.HTTP_200_OK)
<<<<<<< HEAD
=======
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    except HTTPException as ex_error:
        raise ex_error