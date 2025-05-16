# Vogo.Family Mobile Chatbot

A React Native mobile application for the Vogo.Family chatbot, providing mall delivery services and more.

## Features

- Chat interface with AI-powered responses
- Voice recognition for hands-free interaction
- Multi-language support (English, Romanian, French)
- Shopping list management
- Calendar integration
- Responsive UI optimized for mobile devices

## Screenshots

The app includes three main screens:

1. **Chat Screen**: The main interface for interacting with the chatbot
2. **Shopping List Screen**: View and manage your shopping list
3. **Calendar Screen**: View and manage your calendar events

## Prerequisites

- Node.js (v14 or newer)
- npm or yarn
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vogo-chatbot-mobile.git
   cd vogo-chatbot-mobile
   ```

2. Install dependencies:
   ```
   npm install
   # or
   yarn install
   ```

3. Update the API URL in `src/services/api.ts` to point to your backend server.

## Running the App

### Android

```
npm run android
# or
yarn android
```

### iOS (macOS only)

```
npm run ios
# or
yarn ios
```

## Project Structure

```
vogo-chatbot-mobile/
├── src/
│   ├── assets/         # Images, fonts, and other static assets
│   ├── components/     # Reusable UI components
│   ├── screens/        # Screen components
│   │   ├── ChatScreen.tsx
│   │   ├── ShoppingListScreen.tsx
│   │   └── CalendarScreen.tsx
│   └── services/       # API and other services
│       └── api.ts
├── App.tsx             # Main app component
└── package.json        # Dependencies and scripts
```

## Backend Integration

The mobile app communicates with the backend server via RESTful APIs:

- `/chat`: Send text messages to the chatbot
- `/chat/voice`: Send voice messages to the chatbot
- `/shopping-list`: Manage shopping list items
- `/calendar`: Manage calendar events

## Voice Recognition

The app uses `@react-native-community/voice` for voice recognition. To use this feature:

1. Press and hold the microphone button
2. Speak your message
3. Release the button to send the message

## Multi-Language Support

The app automatically detects the language of your messages and responds in the same language. Currently supported languages:

- English
- Romanian
- French

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the AI model
- React Native community for the excellent framework
- Vogo.Family team for the project requirements
