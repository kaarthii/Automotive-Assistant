from flask import Flask, request, jsonify,render_template
import os
import ollama
from speechToText import recognize_speech,record_audio
from textToSpeech import speak



app=Flask(__name__,static_folder='static')


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

def detect_intent(user_question):
    user_question=user_question.lower()

    if "search" in user_question or "google" in user_question or "find" in user_question:
        return "search_web"
    elif "play" in user_question or "youtube" in user_question:
        return "play_youtube"
    elif "open" in user_question or "website" in user_question:
        return "open_website"
    elif "exit" in user_question or "quit" in user_question:
        return "exit"
    else:
        return "general_question"

def refine_query(intent,user_question):
    user_question=user_question.lower()
    keywords={
        "search_web":["search","google","find"],
        "play_youtube":["play","youtube"],
        "open_website":["open","website"]
    }

    for keyword in keywords.get(intent,[]):
        user_question=user_question.replace(keyword,"")
    return user_question.strip()
    
def perform_action(intent,user_question):
    if intent=="search_web":
        from intent import search_google
        refined_query=refine_query(intent,user_question)
        speak("Searching on google!")
        search_google(refined_query)

    elif intent=="play_youtube":
        from intent import play_youtube
        refined_query=refine_query(intent,user_question)
        speak("Playing on youtube!")
        play_youtube(refined_query)

    elif intent=="open_website":
        from intent import open_website
        refined_query=refine_query(intent,user_question)
        speak("Openning!")
        open_website(refined_query)
        return False

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

@app.route('/voice', methods=['GET'])
def voice():
    listening = True  

    while listening:  
        user_question = recognize_speech()
        if not user_question:
            print("No valid speech detected.")
            return jsonify({"error": "Could not recognize speech"}), 400

        user_question = user_question.strip().lower() 
        print(f"Recognized: {user_question}")

        intent=detect_intent(user_question)
        print(f"Detected Intent: {intent}")

        result=perform_action(intent,user_question)
        if result is False:
            listening=False
            break

    return jsonify({"message": "Session ended"}) 
    

@app.route('/')
def home():
    return render_template("index.html")
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=True)
