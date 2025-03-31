import React, { useState, useRef, useEffect } from 'react';

type ChatInputProps = {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
};

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading = false }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 80)}px`;
    }
  }, [message]);

  return (
    <div className="border-t border-gray-200 p-3 bg-white">
      <form onSubmit={handleSubmit} className="flex items-end">
        <div className="flex-grow relative">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            className="w-full p-3 pr-10 border border-gray-300 rounded-full resize-none max-h-20 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 text-sm"
            rows={1}
            disabled={isLoading}
          />
          <div className="absolute right-3 bottom-3 flex space-x-1">
            <button 
              type="button" 
              className="text-gray-400 hover:text-gray-600"
              title="Attach file"
            >
              <span className="text-lg">📎</span>
            </button>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={!message.trim() || isLoading}
          className={`ml-2 p-3 rounded-full ${
            !message.trim() || isLoading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
          title="Send message"
        >
          <span className="text-sm">➤</span>
        </button>
      </form>
      
      <div className="flex justify-between items-center mt-2 text-xs text-gray-500 px-2">
        <span>Press Enter to send</span>
        <span>Powered by Vogo.Family</span>
      </div>
    </div>
  );
};

export default ChatInput;
