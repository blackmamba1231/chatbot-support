import React, { useState, useRef, useEffect } from 'react';
import { VoiceRecorder } from './VoiceRecorder';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatContainerProps {
  className?: string;
  minimized?: boolean;
  onMinimize?: () => void;
  onAction?: (action: string) => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  className,
  minimized = false,
  onMinimize,
  onAction,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your Vogo.Family assistant. How can I help you today?',
      role: 'assistant',
      timestamp: new Date(),
    },
    {
      id: '2',
      content: 'We offer a variety of products including:\n- Kids Activities & Toys\n- Bio & Organic Food\n- Antipasti & Gourmet Items\n- Pet Care Products\n- Allergy-Friendly Products',
      role: 'assistant',
      timestamp: new Date(),
    },
    {
      id: '3',
      content: 'Feel free to ask about any of our product categories or browse our mall delivery services!',
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const [locationOptions, setLocationOptions] = useState<string[]>([]);
  const [waitingForLocation, setWaitingForLocation] = useState(false);

  const handleSendMessage = async (message: string = inputValue) => {
    // Ensure message is a string before calling trim()
    if (!message || typeof message !== 'string' || !message.trim()) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      content: message,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/api/ai-shopping/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          language: 'en',
          location: selectedLocation ? { city: selectedLocation } : null,
        }),
      });

      const data = await response.json();

      // Check if the response contains an action
      if (data.action) {
        if (onAction) {
          onAction(data.action);
        }
        
        // Handle location selection
        if (data.action === 'select_location' || data.action === 'show_malls') {
          setWaitingForLocation(true);
          setLocationOptions(data.data?.locations || []);
        } else {
          setWaitingForLocation(false);
          setLocationOptions([]);
        }
      }
      
      // Check for product category related actions
      const messageLC = message.toLowerCase();
      if (messageLC.includes('kids') || messageLC.includes('activities') || messageLC.includes('toys')) {
        if (onAction) onAction('show_kids_activities');
      }
      if (messageLC.includes('bio') || messageLC.includes('organic') || messageLC.includes('health food')) {
        if (onAction) onAction('show_bio_food');
      }
      if (messageLC.includes('antipasti') || messageLC.includes('appetizers') || messageLC.includes('starters')) {
        if (onAction) onAction('show_antipasti');
      }
      if (messageLC.includes('pet') || messageLC.includes('dog') || messageLC.includes('cat')) {
        if (onAction) onAction('show_pet_care');
      }
      if (messageLC.includes('allergy') || messageLC.includes('allergic') || messageLC.includes('hypoallergenic')) {
        if (onAction) onAction('show_allergy_products');
      }

      setTimeout(() => {
        setIsTyping(false);
        const newAssistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          role: 'assistant',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, newAssistantMessage]);
      }, 500);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // Helper function to combine class names
  const cn = (...classes: (string | undefined | boolean)[]) => {
    return classes.filter(Boolean).join(' ');
  };

  if (minimized) {
    return (
      <button
        onClick={onMinimize}
        className="fixed bottom-4 right-4 bg-blue-500 text-white p-4 rounded-full shadow-lg hover:bg-blue-600 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
          />
        </svg>
      </button>
    );
  }

  return (
    <div className={cn(
      'fixed bottom-6 right-6 w-full max-w-md z-50 font-sans',
      'bg-white/70 backdrop-blur-lg rounded-3xl shadow-2xl border border-gray-100 flex flex-col',
      'transition-all duration-300',
      className
    )} style={{minHeight: 520, maxHeight: '80vh'}}>

      {/* Header */}
      <div className="flex items-center justify-between p-5 border-b border-gray-100 bg-blue-600 rounded-t-2xl shadow-sm relative z-20">
        <h2 className="text-xl font-bold text-white tracking-tight">Vogo.Family Support</h2>
        <button
          onClick={onMinimize}
          className="text-white hover:text-gray-200 transition-colors p-1 rounded-full focus:outline-none focus:ring-2 focus:ring-white"
          aria-label="Minimize chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 5.25l-7.5 7.5-7.5-7.5m15 6l-7.5 7.5-7.5-7.5"
            />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 max-h-[400px]">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              'flex items-end',
              message.role === 'user' ? 'justify-end flex-row-reverse' : 'justify-start'
            )}
          >
            {/* Avatar */}
            <div className={cn(
              'flex-shrink-0 w-10 h-10 rounded-full shadow-md flex items-center justify-center font-bold text-lg',
              message.role === 'user' ? 'bg-gray-400 text-white ml-2' : 'bg-blue-500 text-white mr-2'
            )}>
              {message.role === 'user' ? 'Y' : 'K'}
            </div>
            {/* Message bubble */}
            <div className={cn(
              'relative px-4 py-3 rounded-2xl shadow-md text-base break-words',
              message.role === 'user'
                ? 'bg-blue-500 text-white rounded-br-md rounded-tr-3xl rounded-tl-3xl'
                : 'bg-white/90 text-gray-900 rounded-bl-md rounded-tl-3xl rounded-tr-3xl border border-gray-100'
            )}>
              {message.content}
              <span className="block text-xs text-gray-400 mt-1 text-right select-none">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        {/* Location selection buttons */}
        {waitingForLocation && locationOptions.length > 0 && (
          <div className="flex items-start space-x-2">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
              K
            </div>
            <div className="bg-gray-100 p-3 rounded-lg rounded-bl-none">
              <div className="flex flex-col space-y-2">
                <p className="text-sm font-medium">Please select a location:</p>
                <div className="flex flex-wrap gap-2">
                  {locationOptions.map((location) => (
                    <button
                      key={location}
                      onClick={() => {
                        setWaitingForLocation(false);
                        handleSendMessage(location);
                      }}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
                    >
                      {location}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
        {isTyping && (
          <div className="flex items-start space-x-2">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
              K
            </div>
            <div className="bg-gray-100 p-3 rounded-lg rounded-bl-none">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Response Options */}
      <div className="px-4 py-2 border-t border-gray-200">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              setInputValue("Show available malls");
              handleSendMessage();
              if (onAction) onAction('show_malls');
            }}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
          >
            Browse Available Malls
          </button>
          <button
            onClick={() => {
              setInputValue("Browse products");
              handleSendMessage();
              if (onAction) onAction('browse_products');
            }}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
          >
            Browse Products
          </button>
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-2"
            onClick={() => handleSendMessage('Show me kids activities')}
          >
            Kids Activities
          </button>
          <button
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mr-2"
            onClick={() => handleSendMessage('Show bio food options')}
          >
            Bio Food
          </button>
          <button
            className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 mr-2"
            onClick={() => handleSendMessage('Show antipasti')}
          >
            Antipasti
          </button>
          <button
            className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 mr-2"
            onClick={() => handleSendMessage('Show pet care products')}
          >
            Pet Care
          </button>
          <button
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 mr-2"
            onClick={() => handleSendMessage('Show allergy products')}
          >
            Allergy Products
          </button>
        </div>
      </div>
      
      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <VoiceRecorder onTranscription={(text) => {
            setInputValue(text);
            handleSendMessage(text);
          }} />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSendMessage();
              }
            }}
            placeholder="Type your message..."
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => handleSendMessage(inputValue)}
            disabled={!inputValue.trim() || isTyping}
            className={cn(
              'px-4 py-2 rounded-lg',
              'bg-blue-500 text-white',
              'hover:bg-blue-600 transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};