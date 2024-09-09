
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.async_db import get_async_session
from sqlalchemy.future import select
from app.auth import oauth2
from app.models.user_model import User


router = APIRouter(tags=['ASS'])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.get('/ass')
async def ass_endpoint(token: str, db: AsyncSession = Depends(get_async_session)):
    """_summary_

    Args:
        token (str): token verification
        session (Session, optional): session database. Defaults to Depends(get_db).

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
        
        if user.blocked == True:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {user.id} is blocked")

            
        return Response(status_code=status.HTTP_200_OK)
    except HTTPException as ex_error:
        raise ex_error