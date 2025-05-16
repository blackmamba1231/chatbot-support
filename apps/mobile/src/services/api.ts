import axios from 'axios';

// API base URL - update this with your actual backend URL
const API_URL = 'http://localhost:8000';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API functions
export const sendMessage = async (message: string, language: string = 'en') => {
  try {
    const response = await api.post('/chat', { 
      query: message,
      language: language
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// Voice API functions
export const sendVoiceMessage = async (audioData: any, language: string = 'en') => {
  try {
    // Create form data to send audio file
    const formData = new FormData();
    formData.append('audio', audioData);
    formData.append('language', language);
    
    const response = await api.post('/chat/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error sending voice message:', error);
    throw error;
  }
};

// Shopping list API functions
export const getShoppingList = async () => {
  try {
    const response = await api.get('/shopping-list');
    return response.data;
  } catch (error) {
    console.error('Error getting shopping list:', error);
    throw error;
  }
};

export const addToShoppingList = async (item: string) => {
  try {
    const response = await api.post('/shopping-list', { item });
    return response.data;
  } catch (error) {
    console.error('Error adding to shopping list:', error);
    throw error;
  }
};

// Calendar API functions
export const getCalendarEvents = async (date?: string) => {
  try {
    const url = date ? `/calendar?date=${date}` : '/calendar';
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Error getting calendar events:', error);
    throw error;
  }
};

export const addCalendarEvent = async (eventData: any) => {
  try {
    const response = await api.post('/calendar', eventData);
    return response.data;
  } catch (error) {
    console.error('Error adding calendar event:', error);
    throw error;
  }
};

export default {
  sendMessage,
  sendVoiceMessage,
  getShoppingList,
  addToShoppingList,
  getCalendarEvents,
  addCalendarEvent
};
