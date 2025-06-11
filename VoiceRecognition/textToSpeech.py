import pyttsx3
import whisper
import torch


def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()