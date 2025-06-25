import sounddevice as sd
import numpy as np
import whisper
import wave


whisper_model=whisper.load_model("large")


def record_audio():
    global recording_finished
    recording_finished=False
    filename="temp_audio.wav"
    duration=10
    samplerate=16000

    print("Listening...")
    audio_data=sd.rec(int(duration*samplerate),samplerate=samplerate,channels=1,dtype='int16')
    sd.wait()

    with wave.open(filename,"wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    recording_finished=True
    print("Recognized..")

def recognize_speech():
    global recording_finished
    wait_time=0
    while not recording_finished:
        import time
        time.sleep(0.1)
        wait_time+=1
        if wait_time>200:
            print("recording did not finish")
            return ""
    print("Transcribing...")
    whisp=whisper_model.transcribe("temp_audio.wav")
    text=whisp.get("text", "").strip()
    if not text:
        print("Transcription failed or empty.")
        return "" 
    print(f"Final Transcription: {text}")
    return text

def transcribe_audio(file_path):
    print(f"Transcribe file: {file_path}")
    result=whisper_model.transcribe(file_path)
    transcribed=result.get("text","").strip()
    print(f"Transcribed audio: {transcribed}")
    return transcribed