
document.getElementById('record-btn').addEventListener('click', () => {
  fetch('/start-recording')
    .then(res => res.json())
    .then(() => {
      document.getElementById('assistant-output').innerHTML = `<strong>Listening...</strong>`;
    });
});


document.getElementById('stop-btn').addEventListener('click', () => {
  fetch('/stop-recording')
    .then(res => res.json())
    .then(data => {
      const userSpeech = data.answer?.match(/You said: (.*)/i)?.[1] || 'Not recognized';
      const assistantReply = data.answer?.replace(/You said: .*/i, '').trim() || '...';
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

      document.getElementById('assistant-output').innerHTML = `
        <strong>You said:</strong> ${userSpeech}<br>
        <strong>Response:</strong> ${assistantReply}<br>
        ${matchHTML}
      `;
    });
});


document.getElementById('send-btn').addEventListener('click', () => {
  const text = document.getElementById('text-input').value;
  if (!text.trim()) return;

  fetch('/text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question: text })
  })
  .then(res => res.json())
  .then(data => {
    const userInput = data.User_question || '—';
    const botOutput = data.answer || 'No response received.';
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


    document.getElementById('assistant-output').innerHTML = `
      <strong>You said:</strong> ${userInput}<br>
      <strong>Response:</strong> ${botOutput}<br>
      ${matchHTML}      
    `;
    document.getElementById('text-input').value = ''; 
  });
});
