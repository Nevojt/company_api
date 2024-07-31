from typing import Optional
from fastapi import status, HTTPException, Depends, APIRouter
from .ai_functions import ask_to_gpt, transcriptions





router = APIRouter(
    prefix="/sayory",
    tags=['Sayory AI'],
)




@router.post("/say")
async def say_to_sayori(say_to_chat: str,
                        temperature: Optional[float]):
    
    try:
        response = await ask_to_gpt(say_to_chat, temperature)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/transcription")
async def transcribe_audio_from_url(url: str):
    return transcriptions(url)

