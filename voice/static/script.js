let isRecording=false;
let recordingStarted=false;

document.addEventListener("DOMContentLoaded", function () {
    const sendBtn = document.getElementById("sendBtn");
    const micBtn = document.getElementById("voiceBtn");
    const responseText = document.getElementById("responseText");

    sendBtn.addEventListener("click", function () {
        let userInput = document.getElementById("userInput").value;

        fetch("/text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userInput })
        })
            .then(response => response.json())
            .then(data => {
                responseText.innerText = `Translated: ${data.translated_question}\nResponse: ${data.answer}`;
            })
            .catch(error => {
                console.error("Error: ", error);
                responseText.innerText = "Something went wrong.";
            });
    });

    micBtn.addEventListener("click", async function () {
        if (!isRecording) {
            isRecording = true;
            responseText.innerText = "Listening...";
            try{
                const res=await fetch("/start-recording");
                const json=await res.json();
                if (json.status==="recording_started"){
                    recordingStarted=true;
                }
            } catch(e){
                responseText.innerText="Failed to start recording";
                isRecording=false;
                return;
            }
        } else {

            if(!recordingStarted){
                responseText.innerText="Recording hasn't started yet";
                isRecording=false;
                return;
            }

            isRecording = false;
            responseText.innerText = "Thinking...";
            try{
                const res=await fetch("/stop-recording");
                const json = await res.json();
                responseText.innerText = json.answer ? `Bot: ${json.answer}` : "No valid response.";
            } catch (err) {
                responseText.innerText = "Error: " + err;
            } finally {
                recordingStarted = false;
            }
                
        }
    });
});
