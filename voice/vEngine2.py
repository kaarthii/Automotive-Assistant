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

pending_query = None
pending_action = None

app=Flask(__name__,static_folder='static')
df=pd.read_csv("data.csv")
lines=df["commands"].astype(str).tolist()

model = SentenceTransformer('all-MiniLM-L6-v2')
line_embeddings = model.encode(lines)

def aya_response(prompt):
    try:
        response = ollama.chat(model="aya:8b", messages=[{"role": "user", "content": prompt}])
        return response.get("message", {}).get("content", "Error: No response generated.")
    except Exception as e:
        print(f"Error fetching response from Aya: {e}")
        return "Error: AI response failed."

def get_answer(user_question):
    prompt = f"""
You are a multilingual assistant. Your job is to:
1. Translate the user's question to English if it's in another language.
2. Then answer it in English.

User's question: "{user_question}"

Respond only with the translated question and your final answer.
"""
    answer = aya_response(prompt)
    print(f"Generated Answer: {answer}")
    return answer

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
        return "general_question"

    

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
    if intent=="search_web":
        refined_query=refine_query(intent,user_question)
        speak("Searching on google!")
        search_google(refined_query)

    elif intent=="play_media":
        
        refined_query=refine_query(intent,user_question)
        if "on youtube" in user_question or "youtube" in user_question:
            speak("playing on youtube")
            play_youtube(refined_query.replace("on youtube","").strip())
        elif "on spotify" in user_question or "spotify" in user_question:
            speak("playing on spotify")
            play_in_spotify(refined_query.replace("on spotify","").strip())
        else:
            pending_query=refined_query
            pending_action="play"
            speak("would you like me to play on spotify or youtube?")


    elif intent=="open_website":
        refined_query=refine_query(intent,user_question)
        speak("Openning!")
        open_website(refined_query)
        return False

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
            speak(f"Opening {app}")
            open_app(app,text)
        else:
            speak("I couldn't identify which app to open")
    
    elif intent=="resolve_play":
      
        if "spotify" in user_question:
            speak("playing on spotify")
            play_in_spotify(pending_query)
        elif "youtube" in user_question:
            play_youtube(pending_query)
        pending_query=None
        pending_action=None

    elif intent=="general_question":
        speak("Hmm..Thinking...")
        answer=get_answer(user_question)
        speak(f"{answer}")
    elif intent=="exit":
        speak("Goodbye!")
        return False
    return True

 
@app.route('/text',methods=['POST'])
def text():
    print("request came1")
    data= request.get_json(force=True)
    user_question = data['question']

    if not user_question.strip():
        return jsonify({"error": "Empty input"}), 400

    answer= get_answer(user_question)
    if not answer:
        return jsonify({"error": "Failed to generate an answer"}), 500

    response_data = {"User_question": user_question, "answer": answer}
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

        is_match,best_score,matched_question=is_similar(user_question,0.55)
        if is_match:
            print(f"Similar score: {best_score:.2f}")
            print(f"Matched Line: {matched_question}")
        else:
            print(f"Similar score: {best_score:.2f}")
            print("Lines do not match")


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
