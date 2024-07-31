
import os
from typing import Optional

from fastapi import HTTPException, status
import requests
from openai import AsyncOpenAI, OpenAI
from app.config.config import settings
from app.config.utils import generate_random_code


sayori_key=settings.openai_api_key

client = AsyncOpenAI(
    api_key=sayori_key
)

async def ask_to_gpt(ask_to_chat: str,
                     temperature: Optional[float]) -> str:
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
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        response = chat_completion.choices[0].model_dump()
        return response["message"]["content"]
    except Exception as e:
        return "Sorry, I couldn't process your request."
    

client_trans = OpenAI(
    api_key=sayori_key
)

def transcriptions(url: str):
    try:
        # Download audio files
        response = requests.get(url)
        response.raise_for_status()  
        
        # Generate temporary audio file name
        temporary_audio = "app/routers/AI/audio/" + generate_random_code() + ".ogg"
        
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
