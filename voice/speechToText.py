import sounddevice as sd
import vosk 
import json
import numpy as np
import whisper
import wave


model=vosk.Model("C:/Users/karthi_d/Karthi/vosk-model-small-en-us-0.15")
whisper_model=whisper.load_model("medium")

def check_audio_file():
    with wave.open("temp_audio.wav", "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
        print(f"Audio file duration: {duration} seconds")
    
def recognize_speech():
    device_index=1
    audio_buffer=[]
    samplerate = 16000
    with sd.RawInputStream(samplerate=samplerate,channels=2,dtype='int16',device=device_index) as stream:
        print("Listening...")
        rec=vosk.KaldiRecognizer(model,samplerate)
        while True:
            data,_=stream.read(4000)
            audio_buffer.append(data)
            data=np.frombuffer(data,dtype=np.int16).tobytes()
            if rec.AcceptWaveform(data):
                result=json.loads(rec.Result())
                return result["text"],b"".join(audio_buffer)
def process():
    user_speech,raw_audio=recognize_speech()
    print("Recognized..")
    if not raw_audio:
        print("No audio detected.")
        return ""
    with wave.open("temp_audio.wav","wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(raw_audio)
    check_audio_file() 
    whisp=whisper_model.transcribe("temp_audio.wav")
    print(f"Whisper Output: {whisp}")
    if not whisp or "text" not in whisp:
        print("Whisper failed to transcribe.")
        return ""
    lang=whisp["language"]
    text=whisp["text"]

    print(f"language: {lang}")
    print(f"text: {text}")
    if not text.strip():
        print("Transcription resulted in an empty string.")
        return ""

    if lang!="en":
        whisp=whisper_model.transcribe("temp_audio.wav",task="translate")
        trans=whisp["text"]
        print(f"Translated Text: {trans}")
        return trans
    return text


