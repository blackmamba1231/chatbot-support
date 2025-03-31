import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import ChatInput from './ChatInput';

type MessageType = {
  id: string;
  content: string;
  isBot: boolean;
  timestamp: string;
};

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: '1',
      content: 'Hello! I\'m Kodee from Vogo.Family. How can I assist you today? 😊',
      isBot: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTimestamp = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: MessageType = {
      id: Date.now().toString(),
      content,
      isBot: false,
      timestamp: formatTimestamp(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          language: 'en',
          voice_input: false,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from chatbot');
      }

      const data = await response.json();
      
      const botMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        isBot: true,
        timestamp: formatTimestamp(),
      };
      
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again later.',
        isBot: true,
        timestamp: formatTimestamp(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Suggested quick responses for common queries
  const quickResponses = [
    "What services do you offer?",
    "I need help with my car",
    "Schedule an appointment",
    "Contact a human agent"
  ];

  const handleQuickResponse = (response: string) => {
    handleSendMessage(response);
  };

  if (isChatMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <div className="bg-blue-600 text-white p-4 rounded-lg shadow-lg cursor-pointer" onClick={() => setIsChatMinimized(false)}>
          <div className="flex items-center">
            <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center mr-3">
              <span className="text-blue-600 font-bold">K</span>
            </div>
            <div>
              <p className="font-medium">Chat with Kodee</p>
              <p className="text-xs">Click to reopen chat</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80 md:w-96 bg-white rounded-lg shadow-xl overflow-hidden flex flex-col" style={{ height: '500px', maxHeight: '80vh' }}>
      {/* Chat Header */}
      <div className="bg-blue-600 text-white px-4 py-3 flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center mr-2">
            <span className="text-blue-600 font-bold">K</span>
          </div>
          <div>
            <h3 className="font-medium text-sm">Kodee</h3>
            <p className="text-xs text-blue-100">Active now</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setIsChatMinimized(true)}
            className="bg-gray hover:bg-blue-400 text-black w-8 h-8 rounded flex items-center justify-center transition-colors"
            aria-label="Minimize chat"
          >
            <span className="text-xl">—</span>
          </button>
          <button 
            onClick={() => setMessages([{
              id: '1',
              content: 'Hello! I\'m Kodee from Vogo.Family. How can I assist you today? 😊',
              isBot: true,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            }])}
            className="bg-gray hover:bg-red-400 text-black w-8 h-8 rounded flex items-center justify-center transition-colors"
            aria-label="Reset chat"
          >
            <span className="text-xl">×</span>
          </button>
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-grow overflow-y-auto p-4 bg-gray-50">
        {messages.map((message) => (
          <Message
            key={message.id}
            content={message.content}
            isBot={message.isBot}
            timestamp={message.timestamp}
          />
        ))}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-start">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white mr-2 flex-shrink-0">
                <span className="font-bold text-sm">K</span>
              </div>
              <div className="bg-gray-100 text-gray-500 rounded-lg px-4 py-2 max-w-[80%] border border-gray-200">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '600ms' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Quick Responses */}
      <div className="bg-gray-50 px-4 py-2 border-t border-gray-200">
        <div className="flex flex-wrap gap-2">
          {quickResponses.map((response, index) => (
            <button
              key={index}
              onClick={() => handleQuickResponse(response)}
              className="bg-white text-blue-600 border border-blue-300 rounded-full px-3 py-1 text-xs hover:bg-blue-50 transition-colors"
              disabled={isLoading}
            >
              {response}
            </button>
          ))}
        </div>
      </div>
      
      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatContainer;
