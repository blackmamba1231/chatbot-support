import React, { useState } from 'react';
import './ChatWidget.css';

function ChatInput({ onSendMessage, disabled }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  return (
    <form className="vogo-chat-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="vogo-chat-input"
        placeholder="Type your message here..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={disabled}
      />
      <button
        type="submit"
        className="vogo-chat-send-button"
        disabled={!message.trim() || disabled}
        aria-label="Send message"
      >
        <span>➤</span>
      </button>
    </form>
  );
}

export default ChatInput;
