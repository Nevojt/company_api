from fastapi import status, HTTPException, Depends, APIRouter
<<<<<<< HEAD
from sqlalchemy.orm import Session
from app.models import messages_model
from app.schemas import message
from app.auth import oauth2
from app.database import database

=======
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import messages_model, user_model
from app.schemas import message
from app.auth.oauth2 import get_current_user
from app.database.async_db import get_async_session
from uuid import UUID
from _log_config.log_config import get_logger

vote_logger = get_logger('vote', 'vote.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
<<<<<<< HEAD
def vote(vote: message.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
=======
async def vote(
    votes: message.ChatSchemasVote,
    db: AsyncSession = Depends(get_async_session),
    current_user: user_model.User = Depends(get_current_user)
):
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    """
    Handles the voting process for a message. Users can cast or retract their vote on a specific message.

    Args:
<<<<<<< HEAD
        vote (schemas.Vote): The vote details, including message ID and vote direction.
        db (Session, optional): Database session dependency. Defaults to Depends(database.get_db).
        current_user (int): The ID of the current user, obtained through authentication.

    Raises:
        HTTPException: Raises a 404 error if the message to be voted on does not exist.
        HTTPException: Raises a 409 conflict error if the user has already voted on the specific message and is attempting to vote again.
        HTTPException: Raises a 404 error if the user tries to retract a vote that does not exist.
=======
        votes (message.ChatSchemasVote): The vote details, including message ID and vote direction.
        db (AsyncSession): The asynchronous database session.
        current_user (user_model.User): The current authenticated user.

    Raises:
        HTTPException: Various HTTP exceptions based on the voting logic.
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

    Returns:
        dict: A confirmation message indicating the successful addition or deletion of a vote.
    """
<<<<<<< HEAD
    
    message = db.query(messages_model.Socket).filter(messages_model.Socket.id == vote.message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Message with id: {vote.message_id} does not exist")
    
    vote_query = db.query(messages_model.Vote).filter(
        messages_model.Vote.message_id == vote.message_id, messages_model.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already voted on post {vote.message_id}")
        
        new_vote = messages_model.Vote(message_id = vote.message_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added voted "}
        
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote does not exist")
            
        vote_query.delete(synchronize_session=False)
        db.commit()
        
        return {"message": "Successfully deleted vote"}
    
@router.get('/')
async def get_votes(id_vote: int, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    vote_query = db.query(messages_model.Vote).filter(
        messages_model.Vote.message_id == id_vote, messages_model.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
=======
    try:
        # Check if the message exists
        message_query = await db.execute(
            select(messages_model.ChatMessages).where(
                messages_model.ChatMessages.id == votes.message_id
            )
        )
        message_one = message_query.scalar_one_or_none()

        if not message_one:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with id: {votes.message_id} does not exist"
            )

        # Check if the user has already voted on this message
        vote_query = await db.execute(
            select(messages_model.ChatMessageVote).where(
                messages_model.ChatMessageVote.message_id == votes.message_id,
                messages_model.ChatMessageVote.user_id == current_user.id
            )
        )
        found_vote = vote_query.scalar_one_or_none()

        if votes.dir == 1:
            if found_vote:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User {current_user.id} has already voted on message {votes.message_id}"
                )

            # Add a new vote
            new_vote = messages_model.ChatMessageVote(
                message_id=votes.message_id,
                user_id=current_user.id
            )
            db.add(new_vote)
            await db.commit()
            return {"message": "Successfully added vote"}

        else:
            if not found_vote:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vote does not exist"
                )

            # Delete the existing vote
            await db.delete(found_vote)
            await db.commit()
            return {"message": "Successfully deleted vote"}

    except Exception as e:
        vote_logger.error(f"Error in vote operation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
@router.get('/')
async def get_votes(id_vote: int,
                    db: AsyncSession = Depends(get_async_session),
                    current_user: UUID = Depends(get_current_user)):
    
    vote_query = await db.execute(select(messages_model.ChatMessageVote).where(
        messages_model.ChatMessageVote.message_id == id_vote,
        messages_model.ChatMessageVote.user_id == current_user.id
    ))
    found_vote = vote_query.scalar_one_or_none()
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    if found_vote:
        return True
    else:
        return False