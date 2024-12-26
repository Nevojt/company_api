
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
<<<<<<< HEAD

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import oauth2
=======
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.oauth2 import get_current_user
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
from ...database.async_db import get_async_session

from app.models import user_model
from app.schemas import user
<<<<<<< HEAD

=======
from _log_config.log_config import get_logger

company_user_log = get_logger('company_user', 'company_user.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824


router = APIRouter(
    prefix="/company-users",
    tags=["Company Users"],
)


@router.get("/{company_id}", response_model=List[user.UserInfoLights])
<<<<<<< HEAD
async def read_company_users(company_id: int,
                             db: AsyncSession = Depends(get_async_session),
                             current_user: user.UserOut = Depends(oauth2.get_current_user)):
    
    query_users = select(user_model.User).where(user_model.User.company_id == company_id)
    result = await db.execute(query_users)
    users = result.scalars().all()
    
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Company with ID: {company_id} not found")
    
    return users
=======
async def read_company_users(company_id: UUID,
                             db: AsyncSession = Depends(get_async_session),
                             current_user: user_model.User = Depends(get_current_user)):
    try:
        if current_user.role!= 'admin' and current_user.company_id!= company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to read users in this company")

        company_user_log.info(f"Reading users for company: {company_id}")
        query_users = select(user_model.User).where(user_model.User.company_id == company_id)
        result = await db.execute(query_users)
        users = result.scalars().all()

        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Company with ID: {company_id} not found")

        return users
    except Exception as e:
        company_user_log.error(f"Error reading company users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
