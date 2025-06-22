from flask import Flask, request, jsonify,render_template
import os
import ollama
from speechToText import recognize_speech,record_audio
from textToSpeech import speak
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from intent import search_google,play_youtube,open_website,open_app
from intent import play_in_spotify 
import time

pending_query = None
pending_action = None

app=Flask(__name__,static_folder='static')
df=pd.read_csv("data.csv")
lines=df["commands"].astype(str).tolist()

model = SentenceTransformer('all-MiniLM-L6-v2')
line_embeddings = model.encode(lines)


def is_similar(user_input,threshold=0.55):
    user_embedding = model.encode([user_input])
    similarities= cosine_similarity(user_embedding,line_embeddings)[0]
    best_score=max(similarities)
    best_index=similarities.argmax()
    
    is_match= best_score>=threshold
    matched_question = lines[best_index] if is_match else None
    return is_match,best_score,matched_question


def detect_intent(user_question):
    user_question=user_question.lower()

    if pending_action=="play" and ("spotify" in user_question or "youtube" in user_question):
        return "resolve_play"
    if "open" in user_question and "play" in user_question:
        return "open_and_play"
    if "search" in user_question or "google" in user_question or "find" in user_question:
        return "search_web"
    elif "play" in user_question :
        return "play_media"
    elif "open" in user_question and "website" in user_question:
        return "open_website"
    elif "open" in user_question and not(".com" in user_question or "website" in user_question):
        return "open_app"
    elif "exit" in user_question or "quit" in user_question:
        return "exit"
    else:
        return "search_web"

    

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
    
def perform_action(intent,user_question):
    global pending_query, pending_action
    spoken_output=""

    if intent=="search_web":
        refined_query=refine_query(intent,user_question)
        spoken_output="Searching on google!"
        speak(spoken_output)
        result_text=search_google(refined_query)
        speak(result_text)

    elif intent=="play_media":
        refined_query=refine_query(intent,user_question)
        if "on youtube" in user_question or "youtube" in user_question:
            spoken_output=f"Playing {refined_query} on YouTube"
            speak(spoken_output)
            play_youtube(refined_query.replace("on youtube","").strip())
        elif "on spotify" in user_question or "spotify" in user_question:
            spoken_output=f"Playing {refined_query} on Spotify"
            speak(spoken_output)
            play_in_spotify(refined_query.replace("on spotify","").strip())
        else:
            pending_query=refined_query
            pending_action="play"
            spoken_output="would you like me to play on spotify or youtube?"
            speak(spoken_output)


    elif intent=="open_website":
        refined_query=refine_query(intent,user_question)
        spoken_output=f"Opening {refined_query}"
        speak(spoken_output)
        open_website(refined_query)

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
            speak(spoken_output)
            open_app(app,text)
        else:
            spoken_output="I couldn't identify which app to open"
            speak(spoken_output)

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
            speak(spoken_output)
            open_app(app)
            time.sleep(5)
            play_in_spotify(track_name)
        else:
            spoken_output="Sorry, i can only handle spotify for now"
            speak(spoken_output)
    
    elif intent=="resolve_play":
        if "spotify" in user_question:
            spoken_output=f"playing {pending_query} on spotify"
            speak(spoken_output)
            play_in_spotify(pending_query)
        elif "youtube" in user_question:
            spoken_output=f"playing {pending_query} on youtube"
            speak(spoken_output)
            play_youtube(pending_query)
        pending_query=None
        pending_action=None

    elif intent=="general_question":
        spoken_output="Hmm..Thinking..."
        speak(spoken_output)
        result_text = search_google(user_question)
        spoken_output=result_text
        speak(spoken_output)

    elif intent=="exit":
        spoken_output="Goodbye!"
        speak(spoken_output)
        return False
    
    if spoken_output:
        final_embedding=model.encode([spoken_output.lower()])
        similarities=cosine_similarity(final_embedding,line_embeddings)[0]
        best_score=max(similarities)
        best_index=similarities.argmax()

        if best_score>=0.55:
            matched_line=lines[best_index]
            print(f"Matched : '{matched_line}' (score: {best_score:.2f})")
        else:
            print(f"No match found (score: {best_score:.2f})")
    return True

 
@app.route('/text',methods=['POST'])
def text():
    print("request came1")
    data= request.get_json(force=True)
    user_question = data['question']

    if not user_question.strip():
        return jsonify({"error": "Empty input"}), 400

    result_text = search_google(user_question)
    speak(result_text)

    response_data = {"User_question": user_question, "answer": result_text}
    return jsonify(response_data)

@app.route('/start-recording')
def start_recording():
    global recording_started
    recording_started=True
    import threading
    threading.Thread(target=record_audio).start()
    return jsonify({"status":"recording_started"})

@app.route('/stop-recording')
def stop_recording():
    global recording_started
    if recording_started:
        user_question = recognize_speech()
        recording_started=False
        if not user_question:
            print("No valid speech detected.")
            return jsonify({"error": "Could not recognize speech"}), 400

        user_question = user_question.strip().lower() 
        print(f"Recognized: {user_question}")

        intent=detect_intent(user_question)
        result=perform_action(intent,user_question)
        return jsonify({"answer": f"You said: {user_question}"})
    else:
        return jsonify({"error": "Recording was not started"}), 400



    

@app.route('/')
def home():
    return render_template("index.html")
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)
