import * as React from 'react';
const { useState, useEffect } = React;
import { RootStackParamList } from '../../App';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation, useRoute, RouteProp, NavigationProp } from '@react-navigation/native';
import { getCalendarEvents } from '../services/api';

// Define calendar event type
interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  location?: string;
  description?: string;
  created_at: string;
}

// Using RootStackParamList imported from App.tsx

const CalendarScreen = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [addedEvent, setAddedEvent] = useState<CalendarEvent | null>(null);
  const navigation = useNavigation<NavigationProp<RootStackParamList>>();
  const route = useRoute<RouteProp<RootStackParamList, 'Calendar'>>();

  // Load calendar events
  useEffect(() => {
    fetchCalendarEvents();
  }, []);

  // Handle new event from route params (from chatbot)
  useEffect(() => {
    if (route.params?.newEvent) {
      setAddedEvent(route.params.newEvent);
      setSuccessMessage(route.params.message || 'Event added to your calendar');
      fetchCalendarEvents();
    }
  }, [route.params]);

  // Fetch calendar events from API
  const fetchCalendarEvents = async () => {
    try {
      setIsLoading(true);
      const response = await getCalendarEvents();
      if (response && response.events) {
        setEvents(response.events);
      }
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    return date.toLocaleDateString('en-US', options);
  };

  // Render calendar event
  const renderEvent = ({ item }: { item: CalendarEvent }) => (
    <View style={styles.eventContainer}>
      <View style={styles.eventHeader}>
        <Text style={styles.eventTitle}>{item.title}</Text>
        <Icon name="event" size={24} color="#0066cc" />
      </View>
      <Text style={styles.eventDate}>{formatDate(item.date)}</Text>
      {item.time && <Text style={styles.eventTime}>Time: {item.time}</Text>}
      {item.location && <Text style={styles.eventLocation}>Location: {item.location}</Text>}
      {item.description && <Text style={styles.eventDescription}>{item.description}</Text>}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar backgroundColor="#f5f5f5" barStyle="dark-content" />
      
      {/* Success message */}
      {successMessage ? (
        <View style={styles.successContainer}>
          <View style={styles.successContent}>
            <View style={styles.successIconContainer}>
              <Icon name="check" size={40} color="#fff" />
            </View>
            <Text style={styles.successTitle}>
              {addedEvent ? (
                <>
                  Meeting with {addedEvent.title},
                  {'\n'}
                  {formatDate(addedEvent.date)}
                  {addedEvent.location ? `\nin ${addedEvent.location}` : ''}
                  {'\n'}added to your calendar
                </>
              ) : (
                successMessage
              )}
            </Text>
            <TouchableOpacity style={styles.viewCalendarButton} onPress={() => setSuccessMessage('')}>
              <Text style={styles.viewCalendarButtonText}>View my calendar / reminders</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.addAnotherButton} onPress={() => {
              setSuccessMessage('');
              navigation.navigate('Chat');
            }}>
              <Text style={styles.addAnotherButtonText}>Add another</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.backButton} onPress={() => navigation.navigate('Chat')}>
              <Text style={styles.backButtonText}>Back to home</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <>
          {/* Calendar header */}
          <View style={styles.header}>
            <Text style={styles.title}>Calendar</Text>
            <TouchableOpacity onPress={fetchCalendarEvents}>
              <Icon name="refresh" size={24} color="#0066cc" />
            </TouchableOpacity>
          </View>
          
          {/* Events list */}
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <Text style={styles.loadingText}>Loading...</Text>
            </View>
          ) : events.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Icon name="event-busy" size={64} color="#ddd" />
              <Text style={styles.emptyText}>No upcoming events</Text>
              <Text style={styles.emptySubtext}>
                Ask the chatbot to schedule an event for you
              </Text>
            </View>
          ) : (
            <FlatList
              data={events}
              renderItem={renderEvent}
              keyExtractor={(item: CalendarEvent) => item.id}
              contentContainerStyle={styles.listContainer}
            />
          )}
        </>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  listContainer: {
    padding: 16,
  },
  eventContainer: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  eventTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  eventDate: {
    fontSize: 16,
    color: '#666',
    marginBottom: 4,
  },
  eventTime: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  eventLocation: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  eventDescription: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 8,
  },
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  successContent: {
    width: '100%',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  successIconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  successTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 28,
  },
  viewCalendarButton: {
    paddingVertical: 8,
    marginBottom: 16,
  },
  viewCalendarButtonText: {
    fontSize: 16,
    color: '#0066cc',
    textDecorationLine: 'underline',
  },
  addAnotherButton: {
    width: '100%',
    height: 50,
    backgroundColor: '#006633',
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  addAnotherButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  backButton: {
    width: '100%',
    height: 50,
    backgroundColor: '#f5f5f5',
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: 16,
    color: '#333',
  },
});

export default CalendarScreen;
