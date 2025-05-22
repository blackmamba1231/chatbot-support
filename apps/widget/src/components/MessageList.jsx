import React from 'react';
import './ChatWidget.css';

function MessageList({ messages }) {
  if (!messages || messages.length === 0) {
    return (
      <div className="vogo-chat-welcome">
        <h3>Welcome to Vogo.Family 👋</h3>
        <p>How can I help you today?</p>
      </div>
    );
  }

  return (
    <div className="vogo-chat-messages">
      {messages.map((message) => (
        <div 
          key={message.id}
          className={`vogo-chat-message ${message.sender === 'user' ? 'vogo-chat-message-user' : 'vogo-chat-message-bot'} ${message.isError ? 'vogo-chat-message-error' : ''}`}
        >
          {message.sender === 'bot' && (
            <div className="vogo-chat-avatar">V</div>
          )}
          
          <div className="vogo-chat-message-content">
            <div className="vogo-chat-bubble">
              {message.text}
            </div>
            
            {message.sender === 'user' && message.isVoice && (
              <div className="vogo-chat-message-meta">
                <small>Voice message</small>
              </div>
            )}
            
            {message.products && message.products.length > 0 && (
              <div className="vogo-chat-products">
                {message.products.map((product) => (
                  <div key={product.id} className="vogo-chat-product">
                    {product.image_url && (
                      <img 
                        src={product.image_url} 
                        alt={product.name}
                        className="vogo-chat-product-image"
                      />
                    )}
                    <div className="vogo-chat-product-info">
                      <h4>{product.name}</h4>
                      <p>{product.price} lei</p>
                      {product.location && (
                        <p className="vogo-chat-product-location">📍 {product.location}</p>
                      )}
                      <a 
                        href={product.permalink} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="vogo-chat-product-button"
                      >
                        View Details
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {message.sender === 'user' && (
            <div className="vogo-chat-avatar vogo-chat-avatar-user">Y</div>
          )}
        </div>
      ))}
    </div>
  );
}

export default MessageList;
