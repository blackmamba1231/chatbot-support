import React from 'react';

type MessageProps = {
  content: string;
  isBot: boolean;
  timestamp?: string;
};

const Message: React.FC<MessageProps> = ({ content, isBot, timestamp }) => {
  // Function to convert URLs in text to clickable links
  const renderTextWithLinks = (text: string) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = text.split(urlRegex);
    
    return parts.map((part, index) => {
      if (part.match(urlRegex)) {
        return (
          <a 
            key={index} 
            href={part} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-800"
          >
            {part}
          </a>
        );
      }
      return part;
    });
  };

  // Function to render emojis properly
  const renderContent = (content: string) => {
    if (isBot) {
      return renderTextWithLinks(content);
    }
    return content;
  };

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-4 message-animation`}>
      {isBot && (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white mr-2 flex-shrink-0">
          <span className="font-bold text-sm">K</span>
        </div>
      )}
      
      <div
        className={`rounded-lg px-4 py-2 chat-bubble-hover ${
          isBot
            ? 'bg-gray-100 text-gray-800 border border-gray-200 max-w-[80%]'
            : 'bg-blue-600 text-white max-w-[80%]'
        }`}
      >
        <div className="whitespace-pre-wrap text-sm">
          {renderContent(content)}
        </div>
        {timestamp && (
          <div className={`text-xs mt-1 ${isBot ? 'text-gray-500' : 'text-blue-200'}`}>
            {timestamp}
          </div>
        )}
      </div>
      
      {!isBot && (
        <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white ml-2 flex-shrink-0">
          <span className="font-bold text-sm">Y</span>
        </div>
      )}
    </div>
  );
};

export default Message;
