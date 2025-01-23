
import os
<<<<<<< HEAD
from typing import Optional
=======
from typing import Optional, Any
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

from fastapi import HTTPException, status
import requests
from openai import AsyncOpenAI, OpenAI
from app.config.config import settings
from app.config.utils import generate_random_code
<<<<<<< HEAD

=======
from _log_config.log_config import get_logger

ai_functions_logger = get_logger('ai_functions', 'ai_functions.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

sayori_key=settings.openai_api_key

client = AsyncOpenAI(
    api_key=sayori_key
)

async def ask_to_gpt(ask_to_chat: str,
                     temperature: Optional[float],
<<<<<<< HEAD
                     num: int) -> str:
=======
                     num: int) -> list[Any] | str:
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
    try:
        chat_completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                "role": "user",
                "content": ask_to_chat,
                }
            ],
            temperature=temperature,
            max_tokens=256,
            n=num,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        if num == 1:
            response_1 = chat_completion.choices[0].model_dump()
            response_1 = response_1["message"]["content"]
            response = [response_1]
            return response
<<<<<<< HEAD
        
=======

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        elif num == 2:
            response_1 = chat_completion.choices[0].model_dump()
            response_1 = response_1["message"]["content"]
            response_2 = chat_completion.choices[1].model_dump()
            response_2 = response_2["message"]["content"]
<<<<<<< HEAD
        
=======

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
            response = [response_1, response_2]
            return response

    except Exception as e:
<<<<<<< HEAD
        return "Sorry, I couldn't process your request."
    
=======
        ai_functions_logger.error(f"Error occurred while asking to GPT: {e}")
        return f"Sorry, I couldn't process your request. {e}"

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

client_trans = OpenAI(
    api_key=sayori_key
)

def transcriptions(url: str):
    try:
        # Download audio files
        response = requests.get(url)
<<<<<<< HEAD
        response.raise_for_status()  
        
        # Generate temporary audio file name
        temporary_audio = "app/routers/AI/audio/" + generate_random_code() + ".mp3"
        
=======
        response.raise_for_status()

        # Generate temporary audio file name
        temporary_audio = "app/routers/AI/audio/" + generate_random_code() + ".mp3"

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        # Create temporary audio file
        with open(temporary_audio, "wb") as audio_file:
            audio_file.write(response.content)

        # Write temporary audio
        with open(temporary_audio, "rb") as audio_file:
            transcript = client_trans.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Delete temporary audio
        os.remove(temporary_audio)
        return transcript
    except requests.RequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
<<<<<<< HEAD
    except Exception as e:
=======

    except Exception as e:
        ai_functions_logger.error(f"Error occurred while transcribing audio: {e}")
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
