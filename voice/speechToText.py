import sounddevice as sd # To record audio from the microphone
import numpy as np  # For array operations on audio data
import whisper     # OpenAI's Whisper model for speech transcription
import wave    # To save audio in .wav format
import time   # Used for delays

# Load the large Whisper model once globally for use across functions
whisper_model=whisper.load_model("large")

# Function to record audio from the microphone and save it as a WAV file
def record_audio():
    global recording_finished
    recording_finished=False
    filename="temp_audio.wav"  # Temporary file name to store the recording
    duration=10                # Duration of recording in seconds
    samplerate=16000           # Standard sample rate for Whisper

    print("Listening...")
    audio_data=sd.rec(int(duration*samplerate),samplerate=samplerate,channels=1,dtype='int16') # 16-bit audio encoding
    sd.wait()  # Wait until recording is done
    # Save the recorded data to a WAV file
    with wave.open(filename,"wb") as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # Sample width of 2 bytes (16 bits)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    recording_finished=True
    print("Recognized..")
# Function to monitor and wait for recording to complete, then transcribe audio to text
def recognize_speech():
    global recording_finished
    wait_time=0
    # Wait loop until recording is flagged as finished
    while not recording_finished:
        time.sleep(0.1)
        wait_time+=1
        if wait_time>200:   # Timeout after ~20 seconds
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
# Function to transcribe any audio file using Whisper
def transcribe_audio(file_path):
    print(f"Transcribe file: {file_path}")
    result=whisper_model.transcribe(file_path)
    transcribed=result.get("text","").strip()
    print(f"Transcribed audio: {transcribed}")
    return transcribed
