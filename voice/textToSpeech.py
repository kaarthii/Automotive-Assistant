from gtts import gTTS
from pydub import AudioSegment
import pygame
import os
import time
import io

def speak(text):
    temp_audio = "temp_audio.mp3"
    file_name = "ai_response.wav"

    tts = gTTS(text=text, lang='en')
    tts.save(temp_audio)

    pygame.mixer.init()
    pygame.mixer.music.load(temp_audio)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()

    with open(temp_audio, 'rb') as f:
        audio_data = f.read()
    sound = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

    sound.export(file_name, format="wav")

    time.sleep(0.5)
    if os.path.exists(temp_audio):
        try:
            os.remove(temp_audio)
        except PermissionError:
            print("Warning: temp_audio file is still locked, skipping delete")

    print(f"AI response is saved as {file_name}")
    return file_name
