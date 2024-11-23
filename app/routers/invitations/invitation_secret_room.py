from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
<<<<<<< HEAD
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.database import get_db
from app.database.async_db import get_async_session

from app.models import room_model, user_model
from app.schemas.invitaton import InvitationSchema
=======
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import oauth2
from app.database.async_db import get_async_session
from uuid import UUID
from app.models import room_model, user_model
from app.schemas.invitaton import InvitationSchema
from _log_config.log_config import get_logger

invitation_logger = get_logger('invitation_secret_room', 'invitation_secret_room.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

router = APIRouter(
    prefix='/invitations',
    tags=['Invitations'],
)


<<<<<<< HEAD
@router.get("/", response_model=List[InvitationSchema])
async def get_pending_invitations(db: Session = Depends(get_db), 
=======
@router.get("/get", response_model=List[InvitationSchema])
async def get_pending_invitations(db: AsyncSession = Depends(get_async_session),
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
                                  current_user: user_model.User = Depends(oauth2.get_current_user)):
    """
    Get a list of all pending invitations for the current user.

    Parameters:
        db (Session): The database session object
        current_user (user_model.User): The current user

    Returns:
        List[InvitationSchema]: A list of invitation objects

    Raises:
        HTTPException: If no invitations are found
    """
<<<<<<< HEAD
    invitations = db.query(room_model.RoomInvitation).filter(
        room_model.RoomInvitation.recipient_id == current_user.id,
        room_model.RoomInvitation.status == 'pending'
    ).all()
    
    if not invitations:
        raise HTTPException(status_code=404, detail="No pending invitations found")

    return invitations

@router.post('/invite_user')
async def invite_user_to_room(room_id: int, recipient_id: int, 
                              db: AsyncSession = Depends(get_async_session), 
                              current_user: user_model.User = Depends(oauth2.get_current_user)):
    
    room_get = select(room_model.Rooms).where(room_model.Rooms.id == room_id,
                                          room_model.Rooms.owner == current_user.id,
                                          room_model.Rooms.secret_room == True)
    result = await db.execute(room_get)
    existing_room = result.scalar_one_or_none()
    
    if existing_room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with ID {room_id} not found")
        
    #  Create invitation
    new_invitation = room_model.RoomInvitation(
        room_id=room_id,
        sender_id=current_user.id,
        recipient_id=recipient_id
    )
    db.add(new_invitation)
    await db.commit()
    return {"message": "Invitation sent to user"}
=======
    try:
        invitations_query = await db.execute(select(room_model.RoomInvitation).where(
            room_model.RoomInvitation.recipient_id == current_user.id,
            room_model.RoomInvitation.status == 'pending'
        ))
        invitations = invitations_query.scalars().all()

        if not invitations:
            return []

        return invitations

    except Exception as e:
        invitation_logger.error(f"Error occurred while getting pending invitations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/invite_user')
async def invite_user_to_room(room_id: UUID, recipient_id: UUID,
                              db: AsyncSession = Depends(get_async_session), 
                              current_user: user_model.User = Depends(oauth2.get_current_user)):
    try:
        room_get_query = await db.execute(select(room_model.Rooms).where(room_model.Rooms.id == room_id,
                                              room_model.Rooms.owner == current_user.id,
                                              room_model.Rooms.secret_room))
        existing_room = room_get_query.scalar_one_or_none()

        if existing_room is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Room with ID {room_id} not found")

        #  Create invitation
        new_invitation = room_model.RoomInvitation(
            room_id=room_id,
            sender_id=current_user.id,
            recipient_id=recipient_id
        )
        db.add(new_invitation)
        await db.commit()
        return {"message": "Invitation sent to user"}
    except Exception as e:
        invitation_logger.error(f"Error occurred while inviting user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

@router.post('/respond_invitation')
async def respond_to_invitation(invitation_id: int, accepted: bool,
                                db: AsyncSession = Depends(get_async_session), 
                                current_user: user_model.User = Depends(oauth2.get_current_user)):
<<<<<<< HEAD
    
    if current_user.blocked == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with ID {current_user.id} is blocked")
        
    # Checking the availability of the invitation
    invitation_query = select(room_model.RoomInvitation).where(
        room_model.RoomInvitation.id == invitation_id,
        room_model.RoomInvitation.recipient_id == current_user.id
    )
    result = await db.execute(invitation_query)
    invitation = result.scalar_one_or_none()
    
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invitation with ID {invitation_id} not found")
    # Processing the response to the invitation
    if accepted:
        invitation.status = 'accepted'
        new_manager_room = room_model.RoomsManager(user_id=current_user.id, room_id=invitation.room_id)
        db.add(new_manager_room)
    else:
        invitation.status ='declined'
        
    await db.commit()
    return {"message": "Invitation response recorded"}
=======
    try:
        if current_user.blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"User with ID {current_user.id} is blocked")

        # Checking the availability of the invitation
        invitation_query = await db.execute(select(room_model.RoomInvitation).where(
            room_model.RoomInvitation.id == invitation_id,
            room_model.RoomInvitation.recipient_id == current_user.id
        ))
        invitation = invitation_query.scalar_one_or_none()

        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Invitation with ID {invitation_id} not found")
        # Processing the response to the invitation
        if accepted:
            invitation.status = 'accepted'
            new_manager_room = room_model.RoomsManagerMyRooms(user_id=current_user.id,
                                                            room_id=invitation.room_id)
            db.add(new_manager_room)
        else:
            invitation.status ='declined'

        await db.commit()
        return {"message": "Invitation response recorded"}
    except Exception as e:
        invitation_logger.error(f"Error occurred while responding to invitation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
