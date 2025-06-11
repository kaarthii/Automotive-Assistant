document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("sendBtn").addEventListener("click", function() {
        let userInput=document.getElementById("userInput").value;

        fetch("/text",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify({question:userInput})
            })
            .then(response=>response.json())
            .then(data=>{
                document.getElementById("responseText").innerText = 
                    `Translated: ${data.translated_question}\nResponse: ${data.answer}`;
            })
            .catch(error=>console.error("Error: ",error));

    });

    document.getElementById("voiceBtn").addEventListener("click", function() {
        fetch("/voice")
        .then(response => response.json())
        .then(data => {
            document.getElementById("responseText").innerText = "Bot: " + data.answer;
        });
    });
});


