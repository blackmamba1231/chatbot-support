import React from 'react';
import './ChatWidget.css';

function QuickResponses({ responses, onSelect }) {
  return (
    <div className="vogo-chat-quick-responses">
      <div className="vogo-chat-quick-responses-scroll">
        {responses.map((response) => (
          <button
            key={response.id}
            className="vogo-chat-quick-response-button"
            onClick={() => onSelect(response)}
          >
            {response.text}
          </button>
        ))}
      </div>
    </div>
  );
}

export default QuickResponses;
