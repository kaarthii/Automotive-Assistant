from gtts import gTTS
from pydub import AudioSegment 
import os


def speak(text):
    temp_mp3="temp_audio.mp3"
    file_name="ai_response.wav"

    tts=gTTS(text=text,lang='en')
    tts.save(temp_mp3)

    sound=AudioSegment.from_mp3(temp_mp3)
    sound.export(file_name,format="wav")

    os.remove(temp_mp3)

    print(f"Ai response is saved as {file_name}")
    return file_name

