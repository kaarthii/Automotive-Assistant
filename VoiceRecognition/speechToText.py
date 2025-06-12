import sounddevice as sd
import vosk 
import json
import numpy as np
import whisper
import wave


whisper_model=whisper.load_model("large")

def record_audio():
    filename="temp_audio.wav"
    duration=10
    samplerate=16000

    print("Listening...")
    audio_data=sd.rec(int(duration*samplerate),samplerate=samplerate,channels=1,dtype='int16')
    sd.wait()

    with wave.open("temp_audio.wav","wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    print("Recognized..")

def recognize_speech():
    record_audio()
    print("Transcribing...")
    whisp=whisper_model.transcribe("temp_audio.wav")
    text=whisp.get("text", "").strip()
    if not text:
        print("Transcription failed or empty.")
        return "" 
    print(f"Final Transcription: {text}")
    return text
