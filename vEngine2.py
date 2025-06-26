# Import necessary libraries and modules
from flask import Flask, request, jsonify,render_template  # Flask for web server and API routing
from speechToText import recognize_speech,record_audio,transcribe_audio  # Voice input processing
from textToSpeech import speak   # Converts text to spoken audio
import pandas as pd  # Handles CSV data
from sentence_transformers import SentenceTransformer   # For generating sentence embeddings
from sklearn.metrics.pairwise import cosine_similarity  # For intent matching via similarity
from intent import search_google,play_youtube,open_website,open_app  # Various task functions
from intent import play_in_spotify 
import time
import threading  # For running non-blocking voice recording

# Global variables to handle follow-up queries
pending_query = None
pending_action = None

# Initialize Flask app and load static files
app=Flask(__name__,static_folder='static')

# Load predefined command dataset
df=pd.read_csv("data.csv")
lines=df["commands"].astype(str).tolist()

# Load sentence transformer model and encode command lines
model = SentenceTransformer('all-MiniLM-L6-v2')
line_embeddings = model.encode(lines)

#STEP: 3 DETECTING THE INTENT FROM THE TRANSCRIBED TEXT
# -------- Intent Detection --------
def detect_intent(user_question):
    """
    Determine the user's intent from their query.
    Returns a string representing the intent label.
    """
    user_question=user_question.lower()

    # Handle follow-up for previous "play" intent
    if pending_action=="play" and ("spotify" in user_question or "youtube" in user_question):
        return "resolve_play"
    # Check for compound intent: open and play
    if "open" in user_question and "play" in user_question:
        return "open_and_play"
    # Identify search intent
    if "search" in user_question or "google" in user_question or "find" in user_question:
        return "search_web"
    # Identify media play intent
    elif "play" in user_question :
        return "play_media"
    # Identify website opening intent
    elif "open" in user_question and "website" in user_question:
        return "open_website"
    # Identify app opening intent
    elif "open" in user_question and not(".com" in user_question or "website" in user_question):
        return "open_app"
     # Exit command
    elif "exit" in user_question or "quit" in user_question:
        return "exit"
    # Default fallback
    else:
        return "search_web"

#STEP:4 CLEANING THE QUERY
# Function to clean up user query by removing intent keywords
def refine_query(intent,user_question):
    user_question=user_question.lower()
    keywords={
        "search_web":["search","google","find"],
        "play_media":["play"],
        "open_website":["open","website"]
    }

    for keyword in keywords.get(intent,[]):
        user_question=user_question.replace(keyword,"")
    return user_question.strip()

#STEP:5 HANDLING THE ACTION BASED ON THE INTENT
#STEP:6 AFTER FETCHING THE RESULT MAKING THE AI TO SPEAK THE RESULT AND SAVE IT IN A .WAV FILE
# -------- Action Handler --------
# Core function to perform action based on detected intent
def perform_action(intent,user_question):
    """
    Based on the intent, this function routes the request
    to the appropriate task: search, play media, open website, etc.
    """
    global pending_query, pending_action
    spoken_output=""
    audio_path=""

    # Handle web search
    if intent=="search_web":
        refined_query=refine_query(intent,user_question)
        spoken_output="Searching on google!"
        audio_path=speak(spoken_output)
        result_text=search_google(refined_query)
        audio_path=speak(result_text)
    # Handle media playback
    elif intent=="play_media":
        refined_query=refine_query(intent,user_question)
        if "on youtube" in user_question or "youtube" in user_question:
            spoken_output=f"Playing {refined_query}"
            audio_path=speak(spoken_output)
            play_youtube(refined_query.replace("on youtube","").strip())
        elif "on spotify" in user_question or "spotify" in user_question:
            spoken_output=f"Playing {refined_query}"
            audio_path=speak(spoken_output)
            play_in_spotify(refined_query.replace("on spotify","").strip())
        else:
            # Ask user to clarify platform
            pending_query=refined_query
            pending_action="play"
            spoken_output="would you like me to play on spotify or youtube?"
            audio_path=speak(spoken_output)

    # Handle website opening
    elif intent=="open_website":
        refined_query=refine_query(intent,user_question)
        spoken_output=f"Opening {refined_query}"
        audio_path=speak(spoken_output)
        open_website(refined_query)

    # Handle app opening with optional text input
    elif intent=="open_app":
        words=user_question.lower().split()
        app=None
        text=None

        try:
            open_index=words.index("open")
            app=words[open_index + 1]
        except(ValueError, IndexError):
            pass

        if "write" in user_question.lower():
            text=user_question.lower().split("write",1)[-1].strip()
        elif "type" in user_question.lower():
            text=user_question.lower().split("type",1)[-1].strip()

        if app:
            spoken_output=f"Opening {app}"
            audio_path=speak(spoken_output)
            open_app(app,text)
        else:
            spoken_output="I couldn't identify which app to open"
            audio_path=speak(spoken_output)

    # Handle combined open and play intent
    elif intent=="open_and_play":
        app=None
        track_name=None
        try:
            after_open=user_question.split("open",1)[1]
            if "and play" in after_open:
                app_part,track_part=after_open.split("and play",1)
                app=app_part.strip()
                track_name=track_part.strip()
        except Exception as e:
            print(f"Failed to parse open_and_play intent: {e}")
        if app=="spotify":
            spoken_output=f"opening {app} and playing {track_name}"
            audio_path=speak(spoken_output)
            open_app(app)
            time.sleep(5)
            play_in_spotify(track_name)
        else:
            spoken_output="Sorry, i can only handle spotify for now"
            audio_path=speak(spoken_output)

    # Handle follow-up clarification for play intent
    elif intent=="resolve_play":
        if "spotify" in user_question:
            spoken_output=f"playing {pending_query} on spotify"
            audio_path=speak(spoken_output)
            play_in_spotify(pending_query)
        elif "youtube" in user_question:
            spoken_output=f"playing {pending_query} on youtube"
            audio_path=speak(spoken_output)
            play_youtube(pending_query)
        pending_query=None
        pending_action=None

    # Handle general fallback questions
    elif intent=="general_question":
        spoken_output="Hmm..Thinking..."
        audio_path=speak(spoken_output)
        result_text = search_google(user_question)
        spoken_output=result_text
        audio_path=speak(spoken_output)

    # Handle exit
    elif intent=="exit":
        spoken_output="Goodbye!"
        audio_path=speak(spoken_output)
        return False
    
    #STEP:7 TRANSCRIBING THE RECORDED AI VOICE AND COMPARING IT WITH EXISTING CSV
    # Match spoken output with predefined commands using cosine similarity
    match_display=None
    if spoken_output:
        transcribed_text = transcribe_audio(audio_path) if audio_path else spoken_output
        final_embedding=model.encode([transcribed_text.lower()])
        similarities=cosine_similarity(final_embedding,line_embeddings)[0]
        best_score=max(similarities)
        best_index=similarities.argmax()

        if best_score>=0.55:
            matched_line=lines[best_index]
            print(f"Matched: '{matched_line}' (score: {best_score:.2f})")
            match_display={
                "text":f"Matched: '{matched_line}'",
                "score":f"{best_score*100:.0f}%",
                "matched":True
            }
        else:
            print(f"No match found (score: {best_score:.2f})")
            match_display={
                "text":"No match found",
                "matched":False
            }
            df_existing = pd.read_csv("data.csv")
            existing_commands = df_existing["commands"].astype(str).tolist()
            if "," in transcribed_text:
                transcribed_text = transcribed_text.replace(",", "")
            if transcribed_text not in existing_commands:
            # Append the unmatched transcribed text to data.csv
                try:
                    with open("data.csv", "a", encoding="utf-8") as f:
                        f.write(f"\n{transcribed_text}")
                    print("Unmatched command added to data.csv")
                except Exception as e:
                    print(f"Failed to append to data.csv: {e}")
    return {
        "response": transcribed_text or spoken_output,
        "match_info":match_display
    }

# -------- Flask API Endpoints --------
# API endpoint to handle text-based queries
@app.route('/text',methods=['POST'])
def text():
    print("request came1")
    data= request.get_json(force=True)
    user_question = data['question']

    if not user_question.strip():
        return jsonify({"error": "Empty input"}), 400

    intent = detect_intent(user_question)
    result_text=perform_action(intent,user_question)

    response_data = {"User_question": user_question, "answer": result_text["response"],"match_info":result_text["match_info"]}
    return jsonify(response_data)

# API endpoint to start voice recording in a separate thread
@app.route('/start-recording')
def start_recording():
    global recording_started
    recording_started=False
    if not recording_started:
        recording_started = True
        threading.Thread(target=record_audio).start()
        return jsonify({"status": "recording_started"})
    else:
        return jsonify({"error": "Recording already in progress"}), 400

# API endpoint to stop recording and process the voice input
@app.route('/stop-recording')
def stop_recording():
    global recording_started, recording_finished
    if recording_started:
        
        recording_started=False
        recording_finished = True
        # wait just briefly for the file to be finalized
        time.sleep(1)
        user_question = recognize_speech()
        if not user_question:
            print("No valid speech detected.")
            return jsonify({"error": "Could not recognize speech"}), 400

        user_question = user_question.strip().lower() 
        print(f"Recognized: {user_question}")

        intent=detect_intent(user_question)
        result=perform_action(intent,user_question)
        return jsonify({
            "question": user_question,
            "answer": result["response"],
            "match_info": result["match_info"]
        })
    else:
        return jsonify({"error": "Recording was not started"}), 400


@app.route('/')
def home():
    return render_template("index.html")
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)