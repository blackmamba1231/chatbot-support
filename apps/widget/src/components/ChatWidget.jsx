import React, { useState, useEffect, useRef } from 'react';
import './ChatWidget.css';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import QuickResponses from './QuickResponses';
import VoiceInput from './VoiceInput';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
console.log('API_URL:', API_URL);

function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [quickResponses, setQuickResponses] = useState([]);
  const chatRef = useRef(null);
  const [userInfo, setUserInfo] = useState({
    userId: `user-${Math.random().toString(36).substring(2, 9)}`,
    sessionId: `session-${Math.random().toString(36).substring(2, 9)}`
  });

  // Load quick responses on mount
  useEffect(() => {
    fetchQuickResponses();
    setUserInfo({
      userId: `user-${Math.random().toString(36).substring(2, 9)}`,
      sessionId: `session-${Math.random().toString(36).substring(2, 9)}`
    });
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatRef.current) {
      // Use setTimeout to ensure DOM has updated before scrolling
      setTimeout(() => {
        chatRef.current.scrollTop = chatRef.current.scrollHeight;
      }, 100);
    }
  }, [messages, loading]);

  const fetchQuickResponses = async () => {
    console.log('Fetching quick responses...');
    try {
      const response = await fetch(`${API_URL}/chat/quick-responses`);
      if (response.ok) {
        const data = await response.json();
        setQuickResponses(data);
      }
    } catch (error) {
      console.error('Error fetching quick responses:', error);
    }
  };

  const toggleChat = () => {
    if (isMinimized) {
      setIsMinimized(false);
    } else {
      setIsOpen(!isOpen);
    }
  };

  const toggleMinimize = (e) => {
    e.stopPropagation();
    setIsMinimized(!isMinimized);
  };

  const handleSendMessage = async (message) => {
    // Handle voice input
    if (message instanceof Blob) {
      handleVoiceInput(message);
      return;
    }

    // Handle quick response objects
    if (typeof message === 'object' && message.text) {
      message = message.text;
    }
    
    // Safety check for null or undefined
    if (message === null || message === undefined) return;
    
    // Convert to string if it's not already
    const messageText = String(message).trim();
    
    if (!messageText) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: messageText,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      console.log('Sending message to:', `${API_URL}/chat/message`);
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          message: messageText,
          user_id: userInfo.userId,
          session_id: userInfo.sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Received response:', data);
        
        // Add bot response to chat
        const botMessage = {
          id: Date.now() + 1,
          text: data.response || 'I received your message but something went wrong with my response. Please try again.',
          sender: 'bot',
          timestamp: new Date().toISOString(),
          products: data.products || []
        };
        
        setMessages(prev => [...prev, botMessage]);
        
        // Ensure scroll happens after message is added
        setTimeout(() => {
          if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
          }
        }, 100);
      } else {
        console.error('API request failed with status:', response.status);
        throw new Error(`Failed to send message: ${response.status}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I couldn\'t process your message. Please try again later.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      // Ensure scroll happens after error message is added
      setTimeout(() => {
        if (chatRef.current) {
          chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
      }, 100);
    } finally {
      setLoading(false);
    }
  };

  

  const handleVoiceInput = async (audioBlob) => {
    try {
      setLoading(true);
      
      // Create form data
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.webm');
      formData.append('user_id', userInfo.userId);
      formData.append('session_id', userInfo.sessionId);

      const response = await fetch(`${API_URL}/voice/transcribe`, {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Add transcribed message from user
        const userMessage = {
          id: Date.now(),
          text: data.transcription || 'Voice message sent',
          sender: 'user',
          timestamp: new Date().toISOString(),
          isVoice: true
        };
        
        // Add bot response
        const botMessage = {
          id: Date.now() + 1,
          text: data.response || 'Message received',
          sender: 'bot',
          timestamp: new Date().toISOString(),
          products: data.products || []
        };
        
        setMessages(prev => [...prev, userMessage, botMessage]);
        
        // Scroll to bottom
        setTimeout(() => {
          if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
          }
        }, 100);
      } else {
        throw new Error('Could not process voice message');
      }
    } catch (error) {
      console.error('Error processing voice input:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I had trouble processing your voice input. Please try again.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vogo-chat-widget-container">
      {isOpen ? (
        <div className={`vogo-chat-widget ${isMinimized ? 'minimized' : ''}`}>
          <ChatHeader 
            onClose={toggleChat} 
            onMinimize={toggleMinimize} 
            isMinimized={isMinimized}
          />
          {!isMinimized && (
            <div className="vogo-chat-content">
              <div className="vogo-chat-messages" ref={chatRef}>
                <MessageList messages={messages} />
              </div>
              <div className="vogo-chat-bottom">
                <QuickResponses responses={quickResponses} onSelect={handleSendMessage} />
                <div className="vogo-chat-input-container">
                  <ChatInput onSendMessage={handleSendMessage} loading={loading} />
                  <VoiceInput onSendMessage={handleSendMessage} />
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <button className="vogo-chat-widget-button" onClick={toggleChat}>
          💬
        </button>
      )}
    </div>
  );
}

export default ChatWidget;
