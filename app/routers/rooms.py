from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, oauth2

router = APIRouter(
    prefix="/rooms",
    tags=['Rooms'],
)


@router.get("/")
async def get_rooms(db: Session = Depends(get_db)):
    posts = db.query(models.Rooms).all()
    return posts



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RoomPost)
async def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db), get_current_user: str = Depends(oauth2.get_current_user)):
    
    existing_room = db.query(models.Rooms).filter(models.Rooms.name_room == room.name_room).first()
    if existing_room:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            detail=f"Room {existing_room.name_room} already exists")
    
    room = models.Rooms(**room.dict())
    db.add(room)
    db.commit()
    db.refresh(room)    
    return room



@router.get("/{name_room}", response_model=schemas.RoomPost)
async def get_room(name_room: str, db: Session = Depends(get_db)):
    post = db.query(models.Rooms).filter(models.Rooms.name_room == name_room).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    return post


@router.delete("/{name_room}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(name_room: str, db: Session = Depends(get_db)):
    post = db.query(models.Rooms).filter(models.Rooms.name_room == name_room)
    
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{name_room}", response_model=schemas.RoomPost)
def update_room(name_room: str, update_post: schemas.RoomCreate, db: Session = Depends(get_db)):
    
    post_query = db.query(models.Rooms).filter(models.Rooms.name_room == name_room)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with name_room: {name_room} not found")
    
    post_query.update(update_post.dict(), synchronize_session=False)
    
    db.commit()
    return post_query.first()