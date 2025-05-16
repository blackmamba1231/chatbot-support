import React from 'react';
import './ChatWidget.css';

function ChatHeader({ onClose }) {
  return (
    <div className="vogo-chat-header">
      <div className="vogo-chat-header-info">
        <div className="vogo-chat-avatar">K</div>
        <div className="vogo-chat-title">
          <h3>Kodee</h3>
          <p>Vogo.Family Assistant</p>
        </div>
      </div>
      <button 
        className="vogo-chat-close-button"
        onClick={onClose}
        aria-label="Close chat"
      >
        <span>✕</span>
      </button>
    </div>
  );
}

export default ChatHeader;
