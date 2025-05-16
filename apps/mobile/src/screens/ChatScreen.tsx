import React, { useState, useRef, useEffect } from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import { RootStackParamList } from '../../App';

import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Voice from '@react-native-community/voice';
import { useNavigation, NavigationProp } from '@react-navigation/native';
import { sendMessage, sendVoiceMessage } from '../services/api';

// Define message type
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: number;
}

const ChatScreen = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hi there! I\'m Kodee from Vogo.Family. How can I help you today?',
      sender: 'bot',
      timestamp: Date.now(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef(null);
  const navigation = useNavigation<NavigationProp<RootStackParamList>>();

  // Initialize voice recognition
  useEffect(() => {
    // Set up voice recognition
    Voice.onSpeechStart = () => {
      console.log('Speech started');
    };
    Voice.onSpeechEnd = () => {
      console.log('Speech ended');
    };
    Voice.onSpeechResults = (event: { value?: string[] }) => {
      if (event.value && event.value.length > 0) {
        setInputText(event.value[0]);
        // Auto-send the voice message
        handleSendMessage(event.value[0]);
      }
    };
    Voice.onSpeechError = (error: any) => {
      console.error('Speech error:', error);
      setIsRecording(false);
    };

    // Clean up
    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  // Start voice recording
  const startRecording = async () => {
    try {
      await Voice.start('en-US');
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting voice recording:', error);
    }
  };

  // Stop voice recording
  const stopRecording = async () => {
    try {
      await Voice.stop();
      setIsRecording(false);
    } catch (error) {
      console.error('Error stopping voice recording:', error);
    }
  };

  // Handle sending a message
  const handleSendMessage = async (text = inputText) => {
    if (!text.trim()) return;

    // Add user message to the chat
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: Date.now(),
    };
    setMessages((prevMessages: Message[]) => [...prevMessages, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Send message to backend (match web: { message, language })
      const response = await sendMessage(text, 'en');
      // Add bot response to the chat
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'bot',
        timestamp: Date.now(),
      };
      setMessages((prevMessages: Message[]) => [...prevMessages, botMessage]);
      // Handle special actions if needed (navigation, etc.)
      if (response.action === 'shopping_list_item_added') {
        navigation.navigate('ShoppingList', { 
          newItem: response.item,
          message: `${response.item} added to your shopping list`
        });
      } else if (response.action === 'calendar_event_added') {
        navigation.navigate('Calendar', { 
          newEvent: response.event_details,
          message: response.response
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: Date.now(),
      };
      setMessages((prevMessages: Message[]) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  // Render message item
  const renderMessageItem = ({ item }: { item: Message }) => {
    const isUser = item.sender === 'user';
    return (
      <View
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.botMessageContainer,
        ]}
      >
        {!isUser && (
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarText}>K</Text>
          </View>
        )}
        <View
          style={[
            styles.messageBubble,
            isUser ? styles.userMessageBubble : styles.botMessageBubble,
          ]}
        >
          <Text style={styles.messageText}>{item.text}</Text>
        </View>
        {isUser && (
          <View style={styles.avatarContainer}>
            <Text style={styles.avatarText}>Y</Text>
          </View>
        )}
      </View>
    );
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    if (flatListRef.current && messages.length > 0) {
      // Using setTimeout to ensure the FlatList has rendered before scrolling
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f5f5f5' }}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessageItem}
          keyExtractor={(item: Message) => item.id}
          contentContainerStyle={styles.messagesContainer}
        />

        {isLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#0066cc" />
            <Text style={styles.loadingText}>Kodee is typing...</Text>
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type a message..."
            placeholderTextColor="#999"
            multiline
          />
          <TouchableOpacity
            style={styles.recordButton}
            onPressIn={startRecording}
            onPressOut={stopRecording}
          >
            <Icon
              name={isRecording ? 'mic' : 'mic-none'}
              size={24}
              color={isRecording ? '#ff4c4c' : '#0066cc'}
            />
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]}
            onPress={() => handleSendMessage()}
            disabled={!inputText.trim()}
          >
            <Icon name="send" size={24} color={inputText.trim() ? '#fff' : '#aaa'} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  messagesContainer: {
    paddingHorizontal: 10,
    paddingBottom: 10,
  },
  messageContainer: {
    flexDirection: 'row',
    marginVertical: 5,
    alignItems: 'flex-end',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  botMessageContainer: {
    justifyContent: 'flex-start',
  },
  avatarContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#0066cc',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 5,
  },
  avatarText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  messageBubble: {
    maxWidth: '70%',
    padding: 12,
    borderRadius: 20,
  },
  userMessageBubble: {
    backgroundColor: '#0066cc',
    borderBottomRightRadius: 5,
  },
  botMessageBubble: {
    backgroundColor: '#fff',
    borderBottomLeftRadius: 5,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  messageText: {
    fontSize: 16,
    color: '#333',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
  },
  loadingText: {
    marginLeft: 10,
    color: '#666',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#ddd',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    maxHeight: 100,
    color: '#333',
  },
  recordButton: {
    marginLeft: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButton: {
    marginLeft: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0066cc',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
});

export default ChatScreen;
