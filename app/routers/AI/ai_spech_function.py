
<<<<<<< HEAD
import os
from typing import Optional

from fastapi import HTTPException, status
import requests
from pathlib import Path
from openai import AsyncOpenAI, OpenAI
from app.config.config import settings
from app.config.utils import generate_random_code

=======
from pathlib import Path
from openai import AsyncOpenAI
from app.config.config import settings
from app.config.utils import generate_random_code
from _log_config.log_config import get_logger

ai_speak_logger = get_logger('ai_speak', 'ai_speak.log')
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

sayori_key=settings.openai_api_key

client = AsyncOpenAI(
    api_key=sayori_key
)
name = generate_random_code()
async def speech_engine(text: str):
<<<<<<< HEAD
    speech_file_path = Path(__file__).parent / f"{name}.mp3"
    response = await client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=text
    )
    response.stream_to_file(speech_file_path)
=======
    try:
        speech_file_path = Path("app/routers/AI/audio") / f"speck-{generate_random_code()}.mp3"

        response = await client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path
    except Exception as e:
        ai_speak_logger.error(f"Error occurred while generating speech: {e}")

>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824
