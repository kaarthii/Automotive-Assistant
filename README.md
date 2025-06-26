## Automotive Voice Assistant

An intelligent voice-driven assistant designed for interactive infotainment or desktop productivity. It responds to voice or text, understands user intent, and executes dynamic tasks like web searches, media playback via Spotify/YouTube, or launching local apps—all backed by modern AI models and automation.

---

## Features

- Voice & Text Input
- Intent Recognition using NLP
- Spotify & YouTube Control
- Google Search + Website Opening
- Application Launching + Text Injection
- Real-Time Speech Feedback
- Command Match Confidence via Embeddings

---

## Architecture Overview

```
UI (HTML+JS)
   ↓
Flask API (vEngine.py)
   ├─ Speech Input (Whisper)
   ├─ Intent Classifier
   ├─ Task Engine (YouTube, Spotify, Google, Apps)
   └─ Voice Output (gTTS)
```

---

Getting Started

1. Clone the Repository

```bash
git clone https://github.com/your-username/automotive-assistant.git
cd automotive-assistant
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure you have:
- Python 3.9+
- Chrome installed for Selenium

3. Download Whisper Model

```python
import whisper
whisper.load_model("large")
```

4. Launch the Assistant

```bash
python vEngine.py
```

Open `http://localhost:5001` in your browser.

---

Project Structure

```
├── vEngine.py            # Flask backend: intent detection + API logic
├── intent.py             # Task execution via Selenium + pyautogui
├── speechToText.py       # Voice capture + Whisper transcription
├── textToSpeech.py       # Text-to-Speech generation using gTTS
├── path.py               # Windows .exe path resolver
├── data.csv              # Command reference for embedding similarity
├── templates/
│   └── index.html        # Assistant UI
├── static/
│   ├── styles.css        # Layout & theming
│   └── script.js         # Voice/Text frontend interactivity
```

---

Supported Intents

| Intent         | Example Command                            |
|----------------|---------------------------------------------|
| Search         | "Search weather in Bangalore"              |
| Play Media     | "Play Hukum on Spotify"                 |
| Open Website   | "Open wikipedia.com"                       |
| Open App       | "Open notepad and type hello world"        |
| Combined       | "Open Spotify and play Anirudh"       |

---

Dependencies (Key Packages)

- Flask, pandas, sentence-transformers, sklearn
- selenium, pyautogui, pygetwindow, beautifulsoup4
- sounddevice, numpy, whisper, wave
- gTTS, pydub, pygame
- webdriver_manager, io, os, subprocess

---

Command Similarity

The system compares responses to predefined `commands` in `data.csv` using:
- SentenceTransformer (`all-MiniLM-L6-v2`)
- Cosine similarity threshold (0.55)

Matched vs. unmatched results are shown via color-coded UI feedback.

---
