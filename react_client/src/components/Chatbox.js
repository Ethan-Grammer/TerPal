import React, { useState, useEffect} from 'react';
import axios from 'axios';
import './Chatbox.css'; // Import CSS

function Chatbox() {
  const [messages, setMessages] = useState([]);
  const [initialUploadDone, setInitialUploadDone] = useState(false); // New state to track the initial upload

  useEffect(() => {setMessages(welcomeMessages);}, []);

  // Retrieves transcript from file input
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('http://localhost:3001/upload', formData);
        const uploadConfirmation = response.data.confirmation;
        const aiMessage = response.data.response;

        setInitialUploadDone(true); // Update state to indicate that the file has been uploaded
        
        setMessages([...messages, { text: uploadConfirmation, sender: 'user', label: 'TerpPal' }, 
        { text: aiMessage, sender: 'ai', label: 'You' }]);
      } catch (error) {
        console.error('Error uploading file:', error);
        setMessages([...messages, { text: "Failed to upload file.", sender: 'ai', label: 'TerpPal' }]);
      }
    }
  };

  // Sends user message to Groq API
  const sendMessage = async (msg) => {
    const newMessages = [...messages, { text: msg, sender: 'user', label: 'You' }];
    setMessages(newMessages);
    try {
      const response = await axios.post('http://localhost:3001/chat', {
        messages: msg
      });

      const aiMessage = response.data.response;
      setMessages([...newMessages, { text: aiMessage, sender: 'ai', label: 'TerpPal' }]);
    } catch (error) {
      console.error('Error communicating with the chat API:', error);
      setMessages([...newMessages, { text: "Failed to get a response.", sender: 'ai', label: 'TerpPal' }]);
    }
  };




  // Return structured Chatbox HTML
  return (
    <div className="container">
      <div className="messageContainer">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <span className={`senderLabel ${message.sender}`}>{message.label}</span>
            {message.text}
          </div>
        ))}
      </div>
      <div className="inputContainer">
        {initialUploadDone ? ( // Can only start chatting after you upload your transcript file
          <input
            className="input"
            type="text"
            placeholder="Type your message here..."
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.target.value.trim()) {
                sendMessage(e.target.value);
                e.target.value = ''; // Clear the input after sending
              }
            }}
          />
        ) : (
          <div>
            <input type="file" onChange={handleFileUpload} id="fileInput" style={{ display: 'none' }} />
            <label htmlFor="fileInput">Choose file to upload transcript</label>
          </div>
        )}
      </div>
    </div>
  );

}

const welcomeMessages = [{
    text: "Hello, welcome to UMD's Virtual Advising. To get started, please upload your Unofficial Transcript.",
    sender: 'ai',
    label: 'TerpPal'
    },
    {
      text: "If you are having trouble finding your transcript, you can go to https://www.testudo.umd.edu to retrieve it.",
      sender: 'ai',
      label: 'TerpPal'
}];

export default Chatbox;