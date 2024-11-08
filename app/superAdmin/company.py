import logging
from uuid import UUID
from typing import List
from fastapi import status, HTTPException, Depends, APIRouter, Path
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session
from app.models.user_model import User
from app.config.utils import generate_random_code

from app.models.company_model import Company, StatusSubscription
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanySchema

logging.basicConfig(filename='_log/companies_admin.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/company",
    tags=['Function for super admin'],

)



@router.post("/companies/", response_model=CompanySchema)
async def create_company(company: CompanyCreate,
                        db: AsyncSession = Depends(get_async_session),
                        current_user: User = Depends(oauth2.get_current_user)):
    try:
        if current_user.role != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail="The user is not a super admin, access is denied.")

        db_company_query = await db.execute(select(Company).where(Company.subdomain == company.subdomain))
        db_company = db_company_query.scalar_one_or_none()

        if db_company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Company with the same subdomain already exists")

        code_verification = generate_random_code()

        db_company = Company(**company.model_dump(), code_verification=code_verification)
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        return db_company
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred while creating the company")

@router.get("/companies/status/{status_company}", response_model=List[CompanySchema])
async def read_companies(
    status_company: StatusSubscription = Path(..., description="The status of the subscription"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(oauth2.get_current_user),
):
    """

    @param status_company:  **active. suspended, wait, inactive
    @param db:
    @param current_user:
    @return:
    """
    try:
        if current_user.role != "super_admin":
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"The user id: {current_user.id} is not a super admin, access is denied.",
            )
        logger.info("User is a not super admin")

        all_companies_query = await db.execute(
            select(Company).where(Company.subscription_status == status_company.value)
        )
        all_companies = (
            all_companies_query.scalars().all()
        )

        list_companies = [
            CompanySchema(
                id=company.id,
                name=company.name,
                subdomain=company.subdomain,
                subscription_status=company.subscription_status,
                subscription_end_date=company.subscription_end_date,
            ).model_dump()
            for company in all_companies
        ]

        return list_companies
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred while reading the companies")


@router.get("/companies/{company_id}", response_model=CompanySchema)
async def get_one_company(company_id: UUID, db: AsyncSession = Depends(get_async_session),
                          current_user: User = Depends(oauth2.get_current_user)):
    try:
        if current_user.role != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail="The user is not a super admin, access is denied.")

        db_company_query = await db.execute(select(Company).where(Company.id == company_id))
        db_company = db_company_query.scalar_one_or_none()

        if db_company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return db_company
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred while reading the company")


@router.get("/subdomain/{subdomain}")
async def read_company_by_subdomain(
                            subdomain: str,
                            db: AsyncSession = Depends(get_async_session),
                            current_user: User = Depends(oauth2.get_current_user),
                        ):
    try:
        if current_user.role != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail="The user is not a super admin, access is denied.")

        db_company_query = await db.execute(select(Company).where(Company.subdomain == subdomain))
        db_company = db_company_query.scalar_one_or_none()

        if db_company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Company not found")
        return db_company
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred while reading the company")

@router.put("/companies/{company_id}", response_model=CompanySchema,)
async def update_company_info(
                company_id: UUID,
                company: CompanyUpdate,
                db: AsyncSession = Depends(get_async_session),
                current_user: User = Depends(oauth2.get_current_user),
            ):
    try:
        if current_user.role != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                detail="The user is not a super admin, access is denied.")

        db_company_query = await db.execute(select(Company).where(Company.id == company_id))
        db_company = db_company_query.scalar_one_or_none()

        if db_company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Company not found")

        for key, value in company.model_dump(exclude_unset=True).items():
            setattr(db_company, key, value)

        await db.commit()
        await db.refresh(db_company)
        return db_company
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="An error occurred while updating the company")

@router.delete("/companies/{company_id}", response_model=CompanySchema) # , include_in_schema=True
def delete_company(company_id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    
    
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403,
                            detail="You are not authorized to delete this company")
    
    db.delete(db_company)
    db.commit()
    return db_company