from flask import Flask, request, jsonify,render_template
import os
import ollama
from speechToText import recognize_speech,process
from textToSpeech import speak
import whisper
from langdetect import detect
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


app=Flask(__name__,static_folder='static')
whisper_model=whisper.load_model("medium")

tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

def mistral_response(prompt):
    try:
        response = ollama.chat(model="mistral:7b", messages=[{"role": "user", "content": prompt}])
        return response.get("message", {}).get("content", "Error: No response generated.")
    except Exception as e:
        print(f"Error fetching response from Mistral: {e}")
        return "Error: AI response failed."

def get_answer(user_question,threshold=0.55):
    prompt=f"question:{user_question}\nanswer:"
    answer= mistral_response(prompt)
    print(f"Generated Answer: {answer}")
    return answer

def translate_text(text):
    lang = detect(text)

    if lang!="en":
        inputs=processor(text=text,src_lang=lang,return_tensors="pt")
        trans_text=model.generate(**inputs,tgt_lang="eng")[0].cpu().numpy().squeeze()
        return trans_text
    else:
        return text


    
 
@app.route('/text',methods=['POST'])
def text():
    print("request came1")
    data= request.get_json(force=True)
    user_question = data['question']

    if not user_question.strip():
        return jsonify({"error": "Empty input"}), 400

    translated_question=translate_text(user_question)
    if not translated_question:
        return jsonify({"error": "Translation failed"}), 500
    answer= get_answer(translated_question)
    if not answer:
        return jsonify({"error": "Failed to generate an answer"}), 500

    response_data = {"translated_question": translated_question, "answer": answer}
    return jsonify(response_data)

@app.route('/voice', methods=['GET'])
def voice():
    listening = True  

    while listening:  
        user_question = process()
        if not user_question:
            print("No valid speech detected.")
            return jsonify({"error": "Could not recognize speech"}), 400

        user_question = user_question.strip().lower() 
        print(f"Recognized: {user_question}")

        if "exit" in user_question:  
            print("Stopping voice recognition...")
            listening = False  
            break

        print("Thinking...")
        answer = get_answer(user_question)
        print(f"Answer: {answer}")
        speak(answer)

    return jsonify({"message": "Session ended"}) 
    

@app.route('/')
def home():
    return render_template("index.html")
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)