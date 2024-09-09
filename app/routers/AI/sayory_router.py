from typing import Optional
from fastapi import status, HTTPException, Depends, APIRouter
from .ai_functions import ask_to_gpt, transcriptions





router = APIRouter(
    prefix="/sayory",
    tags=['Sayory AI'],
)




@router.post("/say")
async def say_to_sayori(say_to_chat: str,
                        temperature: Optional[float],
                        num: int):
    """
    This function sends a text query to a GPT model and returns the response.

    Parameters:
    - say_to_chat (str): The text query to be sent to the GPT model.
    - temperature (Optional[float]): The temperature parameter for the GPT model. It controls the randomness of the generated text.
      A lower value (closer to 0) makes the output more deterministic, while a higher value (closer to 1) makes it more random.
      If not provided, the default value is None, which means the model's default temperature will be used.

    Returns:
    - dict: A dictionary containing the response from the GPT model. The dictionary has a single key-value pair:
      {"response": response}, where "response" is the text generated by the GPT model.

    Raises:
    - HTTPException: If an error occurs during the interaction with the GPT model, an HTTPException is raised with a 500 status code
      and the error message as the detail.
    """
    
    try:
        response = await ask_to_gpt(say_to_chat, temperature, num)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/transcription")
async def transcribe_audio_from_url(url: str):
    return transcriptions(url)

