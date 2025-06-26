
// START RECORDING: Triggered when mic button is clicked
document.getElementById('record-btn').addEventListener('click', () => {
  // Send request to Flask endpoint to start recording audio
  fetch('/start-recording') 
    .then(res => res.json())  // Await server acknowledgment
    .then(() => {
      // Update assistant UI to indicate recording has started
      document.getElementById('assistant-output').innerHTML = `<strong>Listening...</strong>`;
    });
});

// STOP RECORDING: Triggered when stop button is clicked
document.getElementById('stop-btn').addEventListener('click', () => {
  // Tell server to stop recording and return recognized data
  fetch('/stop-recording')
    .then(res => {
      if (!res.ok) throw new Error("Recording failed");  // Handle error if backend fails
      return res.json();  // Parse JSON response from Flask
    })
    .then(data => {
      // Extract user query and assistant's response from server response
      const userSpeech = data.question || 'Not recognized';
      const assistantReply = data.answer || '...';
      // Matching line and similarity score for feedback (based on intent matching)
      const matchLine = data.match_info?.text || '';
      const matchScore = data.match_info?.score || '';
      const match = data.match_info;
      // Render match result based on whether it was confidently matched
      let matchHTML = '';
      if (match) {
        if (match.matched) {
          matchHTML = `<p style="color: green;"><strong>${matchLine}</strong> (score: ${matchScore})</p>`;
        } else {
          matchHTML = `<p style="color: red;"><strong>${matchLine}</strong></p>`;
        }
      }
      // Update the assistant UI with final transcribed text and response
      document.getElementById('assistant-output').innerHTML = `
        <strong>You said:</strong> ${userSpeech}<br>
        <strong>Response:</strong> ${assistantReply}<br>
        ${matchHTML}
      `;
    })
    .catch(err => {
      // Display error in red if server call fails
      document.getElementById('assistant-output').innerHTML =
        `<p style="color: red;"><strong>Oops:</strong> ${err.message}</p>`;
    });
});

// TEXT MODE: Submit manual query via the input field
document.getElementById('send-btn').addEventListener('click', () => {
  const text = document.getElementById('text-input').value;
  if (!text.trim()) return;
// Send query as JSON to Flask server
  fetch('/text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json' // Required for JSON payload
    },
    body: JSON.stringify({ question: text })
  })
  .then(res => res.json())
  .then(data => {
    // Extract question and assistant's response
    const userInput = data.User_question || '—';
    const botOutput = data.answer || 'No response received.';
    // Extract intent match explanation and score (if any)
    const matchLine=data.match_info.text;
    const matchScore=data.match_info.score;
    const match=data.match_info;

    let matchHTML='';
      if(match){
        if(match.matched){
          matchHTML = `<p style="color: green;"><strong>${matchLine}</strong> (score: ${matchScore})</p>`;
        } else{
          matchHTML = `<p style="color: red;"><strong>${matchLine}</strong></p>`;
        }
      }

    // Display final interaction result to the user
    document.getElementById('assistant-output').innerHTML = `
      <strong>You said:</strong> ${userInput}<br>
      <strong>Response:</strong> ${botOutput}<br>
      ${matchHTML}      
    `;
    // Clear the input field after sending
    document.getElementById('text-input').value = ''; 
  });
});
