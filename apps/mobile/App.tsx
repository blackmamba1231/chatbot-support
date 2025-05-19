import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Import screens
import ChatScreen from './src/screens/ChatScreen';
import ShoppingListScreen from './src/screens/ShoppingListScreen';
import CalendarScreen from './src/screens/CalendarScreen';

// Define the root stack parameter list with proper params
export type RootStackParamList = {
  Chat: undefined;
  ShoppingList: { newItem?: any; message?: string } | undefined;
  Calendar: { newEvent?: any; message?: any } | undefined;
};

// Create stack navigator
const Stack = createStackNavigator<RootStackParamList>();

// Define the main app component
const App = () => {
  return (
    <SafeAreaProvider>
      {/* @ts-ignore - Bypassing TypeScript error with the children prop */}
      <NavigationContainer>
        {/* @ts-ignore - Bypassing TypeScript error with the children prop */}
        <Stack.Navigator
          initialRouteName="Chat"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#0066cc',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}
        >
          <Stack.Screen 
            name="Chat" 
            component={ChatScreen} 
            options={{ title: 'Vogo.Family Chat' }} 
          />
          <Stack.Screen 
            name="ShoppingList" 
            component={ShoppingListScreen} 
            options={{ title: 'Shopping List' }} 
          />
          <Stack.Screen 
            name="Calendar" 
            component={CalendarScreen} 
            options={{ title: 'Calendar' }} 
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

export default App;
