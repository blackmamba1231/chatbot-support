import React, { useState, useEffect, useRef } from 'react';
import './ChatWidget.css';
import ChatHeader from './ChatHeader';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import QuickResponses from './QuickResponses';
import VoiceInput from './VoiceInput';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
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
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchQuickResponses = async () => {
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
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          user_id: userInfo.userId,
          session_id: userInfo.sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add bot response to chat
        const botMessage = {
          id: Date.now() + 1,
          text: data.response,
          sender: 'bot',
          timestamp: new Date().toISOString(),
          products: data.products || []
        };
        
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('Failed to get response from the server');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an issue. Please try again later.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickResponse = (response) => {
    handleSendMessage(response.text);
  };

  const handleVoiceInput = async (audioBlob) => {
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.mp3');
      formData.append('user_id', userInfo.userId);
      formData.append('session_id', userInfo.sessionId);
      
      const response = await fetch(`${API_URL}/voice/transcribe`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Add transcribed message from user
        if (data.transcription) {
          const userMessage = {
            id: Date.now(),
            text: data.transcription,
            sender: 'user',
            timestamp: new Date().toISOString(),
            isVoice: true
          };
          
          setMessages(prev => [...prev, userMessage]);
        }
        
        // Add bot response
        const botMessage = {
          id: Date.now() + 1,
          text: data.response,
          sender: 'bot',
          timestamp: new Date().toISOString(),
          products: data.products || []
        };
        
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('Failed to process voice input');
      }
    } catch (error) {
      console.error('Error processing voice input:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I had trouble understanding your voice input. Please try again.',
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
    <div className="vogo-chat-widget-embedded">
      <div className="vogo-chat-widget-inner">
        <ChatHeader onClose={() => {}} />
        
        <div className="vogo-chat-body" ref={chatRef}>
          <MessageList messages={messages} />
          {loading && <div className="vogo-chat-loading">
            <div className="vogo-chat-loading-dots">
              <span></span><span></span><span></span>
            </div>
          </div>}
        </div>
        
        <div className="vogo-chat-bottom">
          {quickResponses.length > 0 && (
            <QuickResponses responses={quickResponses} onSelect={handleQuickResponse} />
          )}
          <div className="vogo-chat-input-container">
            <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
            <VoiceInput onVoiceRecorded={handleVoiceInput} disabled={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatWidget;
