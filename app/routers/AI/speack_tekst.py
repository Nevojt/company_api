from gtts import gTTS
import os

text = "Pryvet, jak tvoi spravy?"
tts = gTTS(text=text, lang='en')
tts.save("app/routers/AI/output.mp3")
