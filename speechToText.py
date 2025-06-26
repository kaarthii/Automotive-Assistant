import sounddevice as sd # To record audio from the microphone
import numpy as np  # For array operations on audio data
import whisper     # OpenAI's Whisper model for speech transcription
import wave   # To save audio in .wav format
import queue

#STEP: 1 RECORDING THE SPEECH

# Load the large Whisper model once globally for use across functions
whisper_model=whisper.load_model("large")

audio_q = queue.Queue()  # This queue holds real-time audio chunks from the mic
recording_finished = False  # Flag to control when to stop recording
recording_stream = None   # Placeholder for the input stream object
samplerate = 16000    # Sample rate in Hz (16k is great for speech)
channels = 1    # Mono audio input
filename = "temp_audio.wav"   # Name of the output audio file

# Callback function that collects the audio data in real time
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Stream status: {status}")  # Logs overflow or underflow warnings
    audio_q.put(indata.copy())   # Place audio chunk into queue for consumption

# Function to record audio from the microphone and save it as a WAV file
def record_audio():
    global recording_finished
    recording_finished = False
    # Create a new wave file for writing binary audio data
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(2)  # 16 bits per sample = 2 bytes
    wf.setframerate(samplerate)

    print("Listening...")

    try:
        # Create a stream that constantly collects microphone input
        with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', callback=audio_callback):
            while not recording_finished:
                # Pull audio chunks from the queue and write to file
                wf.writeframes(audio_q.get(timeout=1))
    except Exception as e:
        print(f"Recording failed: {e}")
    finally:
        wf.close()   # Ensure file is properly closed regardless of error
        print("Recording stopped.")

#STEP: 2 TRANSCRIBING THE SPEECH 

# Function to monitor and wait for recording to complete, then transcribe audio to text
def recognize_speech():
    print("Transcribing...")
    whisp=whisper_model.transcribe("temp_audio.wav")  # Transcribe the file just recorded
    text=whisp.get("text", "").strip()   # Extract the transcribed text
    if not text:
        print("Transcription failed or empty.")  # Handle blank or failed transcriptions
        return "" 
    print(f"Final Transcription: {text}")
    return text
# Function to transcribe any audio file using Whisper
def transcribe_audio(file_path):
    print(f"Transcribe file: {file_path}")
    result=whisper_model.transcribe(file_path)  # Transcribes user-supplied audio path
    transcribed=result.get("text","").strip()   # Retrieve clean transcribed text
    print(f"Transcribed audio: {transcribed}")
    return transcribed