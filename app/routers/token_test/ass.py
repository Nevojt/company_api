
from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.async_db import get_async_session
from app.auth import oauth2



router = APIRouter(tags=['ASS'])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

@router.get('/ass')
async def ass_endpoint(token: str,
                        db: AsyncSession = Depends(get_async_session)):
    """_summary_

    Args:
        token (str): token verification
        db (Session, optional): session database. Defaults to Depends(get_db).

    Raises:
        HTTPException:: Token not validation

    Returns:
        Response: return server
    """

    try:
        user_data = await oauth2.verify_access_token(token=token,
                                               credentials_exception=credentials_exception,
                                               db=db)

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        check_user = await oauth2.get_current_user(token=token,
                                             db=db)
        if not check_user:
            raise HTTPException(status_code=404, detail="User not found")

        if check_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {check_user.id} is blocked")


        return Response(status_code=status.HTTP_200_OK)
    except HTTPException as ex_error:
        raise ex_error