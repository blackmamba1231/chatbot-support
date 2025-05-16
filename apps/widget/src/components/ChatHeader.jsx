import React from 'react';
import './ChatWidget.css';

function ChatHeader({ onClose, onMinimize, isMinimized }) {
  return (
    <div className="vogo-chat-header">
      <div className="vogo-chat-header-info">
        <div className="vogo-chat-avatar">K</div>
        <div className="vogo-chat-title">
          <h3>Kodee</h3>
          <p>Vogo.Family Assistant</p>
        </div>
      </div>
      <div className="vogo-chat-header-actions">
        <button 
          className="vogo-chat-minimize-button"
          onClick={onMinimize}
          aria-label={isMinimized ? 'Maximize chat' : 'Minimize chat'}
        >
          <span>{isMinimized ? '⬆️' : '⬇️'}</span>
        </button>
        <button 
          className="vogo-chat-close-button"
          onClick={onClose}
          aria-label="Close chat"
        >
          <span>✕</span>
        </button>
      </div>
    </div>
  );
}

export default ChatHeader;
