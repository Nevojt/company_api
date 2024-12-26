<<<<<<< HEAD

=======
from _log_config.log_config import get_logger
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import pytz
from sqlalchemy import select
from app.models import user_model, room_model, company_model
from app.config.utils import generate_random_code

<<<<<<< HEAD
# scheduler = AsyncIOScheduler()
def setup_scheduler(db_session_factory):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_old_rooms, 'cron', day='*', hour='0', args=[db_session_factory])
    scheduler.add_job(delete_test_users, 'cron', day='*', hour='0', args=[db_session_factory])
    scheduler.add_job(update_access_token, 'interval', hours=4, args=[db_session_factory])
    # scheduler.add_job(update_access_token, 'interval', minutes=1, args=[db_session_factory]) # test functionality

    scheduler.start()
    return scheduler


async def delete_old_rooms(db_session_factory):
    async with db_session_factory() as db:
        thirty_days_ago = datetime.now(pytz.utc) - timedelta(days=30)
        query = select(room_model.Rooms).where(room_model.Rooms.delete_at < thirty_days_ago)
        result = await db.execute(query)
        old_rooms = result.scalars().all()
        for room in old_rooms:
            await db.delete(room)
        await db.commit()
        
        
async def delete_test_users(db_session_factory):
    async with db_session_factory() as db:
        
        email_pattern = '%.testuser'
        
        query = select(user_model.User).where(user_model.User.email.like(email_pattern))
        result = await db.execute(query)
        test_users = result.scalars().all()
        for user in test_users:
            await db.delete(user)
        await db.commit()
        
async def update_access_token(db_session_factory):
    async with db_session_factory() as db:
        token_query = select(company_model.Company)
        result = await db.execute(token_query)
        companies = result.scalars().all()

        # Generate new access token
        for company in companies:
            company.code_verification = generate_random_code()
            db.add(company)
        await db.commit()

    
=======
scheduler_logger = get_logger('scheduler', 'scheduler.log')

# scheduler = AsyncIOScheduler()
def setup_scheduler(db_session_factory):
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(delete_old_rooms, 'cron', day='*', hour='0', args=[db_session_factory])
        scheduler.add_job(delete_test_users, 'cron', day='*', hour='0', args=[db_session_factory])
        scheduler.add_job(update_access_token, 'interval', hours=12, args=[db_session_factory])
        scheduler.add_job(unban_users, 'interval', seconds=10, args=[db_session_factory])
        # scheduler.add_job(update_access_token, 'interval', minutes=1, args=[db_session_factory]) # test functionality

        scheduler.start()
        return scheduler
    except Exception as e:
        scheduler_logger.error(f"Failed to setup scheduler: {str(e)}")
        return None


async def delete_old_rooms(db_session_factory):
    try:
        async with db_session_factory() as db:
            thirty_days_ago = datetime.now(pytz.utc) - timedelta(days=30)
            query = select(room_model.Rooms).where(room_model.Rooms.delete_at < thirty_days_ago)
            result = await db.execute(query)
            old_rooms = result.scalars().all()
            for room in old_rooms:
                await db.delete(room)
            await db.commit()
    except Exception as e:
        scheduler_logger.error(f"Failed to delete old rooms: {str(e)}")
        
        
async def delete_test_users(db_session_factory):
    try:
        async with db_session_factory() as db:

            email_pattern = '%.testuser'

            query = select(user_model.User).where(user_model.User.email.like(email_pattern))
            result = await db.execute(query)
            test_users = result.scalars().all()
            for user in test_users:
                await db.delete(user)
            await db.commit()
    except Exception as e:
        scheduler_logger.error(f"Failed to delete test users: {str(e)}")
        
async def update_access_token(db_session_factory):
    try:
        async with db_session_factory() as db:
            token_query = select(company_model.Company)
            result = await db.execute(token_query)
            companies = result.scalars().all()

            # Generate new access token
            for company in companies:
                company.code_verification = generate_random_code()
                db.add(company)
            await db.commit()
    except Exception as e:
        scheduler_logger.error(f"Failed to update access tokens: {str(e)}")


async def unban_users(db_session_factory):
    try:
        current_time_utc = datetime.now(pytz.timezone("UTC"))
        current_time_naive = current_time_utc.replace(tzinfo=None)
        async with db_session_factory() as db:
            unban_query = await db.execute(select(room_model.Ban))
            bans = unban_query.scalars().all()
            to_unban = [ban for ban in bans if ban.end_time <= current_time_naive]

            for ban in to_unban:
                await db.delete(ban)

            await db.commit()

    except Exception as e:
        scheduler_logger.error(f"Failed to unban users: {str(e)}")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
