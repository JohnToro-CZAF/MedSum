import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Chatbot.css";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const handleInputChange = (event) => {
    setInput(event.target.value);
  };
  const _handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      sendMessage();
    }
  }
  const sendMessage = async () => {
    if (input) {
      setMessages([...messages, { text: input, sender: "user" }]);
      setInput("");

      try {
        const response = await axios.post(
          "http://localhost:4949/handle_message",
          { text: input }
        );

        const botResponse = response.data.text;

        setMessages([...messages, { text: input, sender: "user" }, { text: botResponse, sender: "bot" }, ]);
        console.log(messages)
      } catch (error) {
        console.log(error);
      }
    }
  };

  useEffect(() => {
    setMessages([{ text: "Hi! How can I help you?", sender: "bot" }]);
  }, []);

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <span className="chatbot-title">Ask me anything</span>
        <button className="chatbot-close-button">X</button>
      </div>
      <div className="chatbot-message-container">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chatbot-message ${
              message.sender === "user" ? "user-message" : "bot-message"
            }`}
          >
            {message.text}
          </div>
        ))}
      </div>
      <div className="chatbot-input-container">
        <input
          className="chatbot-input"
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message here..."
          onKeyDown={_handleKeyDown}
        />
        <button className="chatbot-send-button" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
