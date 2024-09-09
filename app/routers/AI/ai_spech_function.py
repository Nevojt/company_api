
import os
from typing import Optional

from fastapi import HTTPException, status
import requests
from pathlib import Path
from openai import AsyncOpenAI, OpenAI
from app.config.config import settings
from app.config.utils import generate_random_code


sayori_key=settings.openai_api_key

client = AsyncOpenAI(
    api_key=sayori_key
)
name = generate_random_code()
async def speech_engine(text: str):
    speech_file_path = Path(__file__).parent / f"{name}.mp3"
    response = await client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=text
    )
    response.stream_to_file(speech_file_path)
