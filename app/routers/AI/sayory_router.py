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
    """
    This function sends a text query to a GPT model and returns the response.

    Parameters:
    say_to_chat (str): The text query to be sent to the GPT model.
    temperature (Optional[float]): The temperature parameter for the GPT model.
        A higher value results in more random and diverse responses.
        A lower value results in more deterministic and less diverse responses.
        If not provided, the default value is None.

    Returns:
    dict: A dictionary containing the response from the GPT model.
        The dictionary has a single key-value pair: 'response' -> str.
    """
    
    try:
        response = await ask_to_gpt(say_to_chat, temperature)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/transcription")
async def transcribe_audio_from_url(url: str):
    """
    This function transcribes an audio file from a given URL into text.

    Parameters:
    url (str): The URL of the audio file to be transcribed.
        The URL must be accessible and point to a valid audio file.

    Returns:
    dict: A dictionary containing the transcribed text.
        The dictionary has a single key-value pair: 'transcription' -> str.
    """
    return transcriptions(url)

