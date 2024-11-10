
from pathlib import Path
from openai import AsyncOpenAI
from app.config.config import settings
from app.config.utils import generate_random_code
from _log_config.log_config import get_logger

ai_speak_logger = get_logger('ai_speak', 'ai_speak.log')

sayori_key=settings.openai_api_key

client = AsyncOpenAI(
    api_key=sayori_key
)
name = generate_random_code()
async def speech_engine(text: str):
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

