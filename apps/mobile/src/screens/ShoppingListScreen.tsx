import React, { useState, useEffect } from 'react';
import { RootStackParamList } from '../../App';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  TextInput,
  SafeAreaView,
  StatusBar,
  Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation, useRoute, RouteProp, NavigationProp } from '@react-navigation/native';
import { getShoppingList, addToShoppingList } from '../services/api';

// Define shopping list item type
interface ShoppingListItem {
  id: string;
  name: string;
  completed: boolean;
  added_at: string;
}

// Using RootStackParamList imported from App.tsx

const ShoppingListScreen = () => {
  const [items, setItems] = useState<ShoppingListItem[]>([]);
  const [newItem, setNewItem] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const navigation = useNavigation<NavigationProp<RootStackParamList>>();
  const route = useRoute<RouteProp<RootStackParamList, 'ShoppingList'>>();

  // Load shopping list items
  useEffect(() => {
    fetchShoppingList();
  }, []);

  // Handle new item from route params (from chatbot)
  useEffect(() => {
    if (route.params?.newItem) {
      setSuccessMessage(`${route.params.newItem} added to your shopping list`);
      fetchShoppingList();
      
      // Clear success message after 3 seconds
      const timer = setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [route.params]);

  // Fetch shopping list from API
  const fetchShoppingList = async () => {
    try {
      setIsLoading(true);
      const response = await getShoppingList();
      if (response && response.items) {
        setItems(response.items);
      }
    } catch (error) {
      console.error('Error fetching shopping list:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Add item to shopping list
  const handleAddItem = async () => {
    if (!newItem.trim()) return;
    
    try {
      setIsLoading(true);
      await addToShoppingList(newItem);
      setNewItem('');
      setSuccessMessage(`${newItem} added to your shopping list`);
      
      // Refresh shopping list
      await fetchShoppingList();
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (error) {
      console.error('Error adding item to shopping list:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle item completion status
  const toggleItemCompletion = (id: string) => {
    setItems(
      items.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  };

  // Render shopping list item
  const renderItem = ({ item }: { item: ShoppingListItem }) => (
    <TouchableOpacity
      style={styles.itemContainer}
      onPress={() => toggleItemCompletion(item.id)}
    >
      <View style={styles.itemCheckbox}>
        {item.completed ? (
          <Icon name="check-circle" size={24} color="#4CAF50" />
        ) : (
          <Icon name="radio-button-unchecked" size={24} color="#999" />
        )}
      </View>
      <Text
        style={[
          styles.itemText,
          item.completed && styles.itemTextCompleted,
        ]}
      >
        {item.name}
      </Text>
    </TouchableOpacity>
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
            <Text style={styles.successTitle}>{successMessage}</Text>
            <TouchableOpacity style={styles.viewListButton} onPress={() => setSuccessMessage('')}>
              <Text style={styles.viewListButtonText}>View list</Text>
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
          {/* Shopping list */}
          <View style={styles.header}>
            <Text style={styles.title}>Shopping List</Text>
            <TouchableOpacity onPress={fetchShoppingList}>
              <Icon name="refresh" size={24} color="#0066cc" />
            </TouchableOpacity>
          </View>
          
          {/* Add item input */}
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              value={newItem}
              onChangeText={setNewItem}
              placeholder="Add an item..."
              placeholderTextColor="#999"
            />
            <TouchableOpacity
              style={[styles.addButton, !newItem.trim() && styles.addButtonDisabled]}
              onPress={handleAddItem}
              disabled={!newItem.trim() || isLoading}
            >
              <Icon name="add" size={24} color="#fff" />
            </TouchableOpacity>
          </View>
          
          {/* Items list */}
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <Text style={styles.loadingText}>Loading...</Text>
            </View>
          ) : items.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Icon name="shopping-basket" size={64} color="#ddd" />
              <Text style={styles.emptyText}>Your shopping list is empty</Text>
              <Text style={styles.emptySubtext}>
                Add items using the field above or ask the chatbot
              </Text>
            </View>
          ) : (
            <FlatList
              data={items}
              renderItem={renderItem}
              keyExtractor={(item: ShoppingListItem) => item.id}
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
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  input: {
    flex: 1,
    height: 48,
    backgroundColor: '#f0f0f0',
    borderRadius: 24,
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#333',
  },
  addButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#0066cc',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 12,
  },
  addButtonDisabled: {
    backgroundColor: '#ccc',
  },
  listContainer: {
    padding: 16,
  },
  itemContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  itemCheckbox: {
    marginRight: 12,
  },
  itemText: {
    fontSize: 16,
    color: '#333',
    flex: 1,
  },
  itemTextCompleted: {
    textDecorationLine: 'line-through',
    color: '#999',
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 30,
  },
  viewListButton: {
    paddingVertical: 8,
    marginBottom: 16,
  },
  viewListButtonText: {
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

export default ShoppingListScreen;
