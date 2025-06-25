from gtts import gTTS     # Google Text-to-Speech API for converting text to MP3
from pydub import AudioSegment   # For converting MP3 to WAV
import pygame      # To play MP3 audio
import os
import time
import io    # For in-memory byte stream operations

# Function to synthesize text into speech, play it, and return a WAV file path
def speak(text):
    temp_audio = "temp_audio.mp3"   # Temporary MP3 filename
    file_name = "ai_response.wav"   # Final audio output in WAV format

    # Generate TTS audio using gTTS and save as MP3
    tts = gTTS(text=text, lang='en')
    tts.save(temp_audio)
    
    # Initialize pygame audio mixer and play the generated MP3
    pygame.mixer.init()
    pygame.mixer.music.load(temp_audio)
    pygame.mixer.music.play()

    # Wait until the MP3 has finished playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()   # Unload after playback

    with open(temp_audio, 'rb') as f:
        audio_data = f.read()
    sound = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

    sound.export(file_name, format="wav")  # Save as WAV

    # Brief pause to ensure system releases file lock
    time.sleep(0.5)
    # Clean up the temporary MP3 file if possible
    if os.path.exists(temp_audio):
        try:
            os.remove(temp_audio)
        except PermissionError:
            print("Warning: temp_audio file is still locked, skipping delete")

    print(f"AI response is saved as {file_name}")
    return file_name  # Return the path to the final WAV file
