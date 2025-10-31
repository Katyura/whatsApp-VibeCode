# WhatsApp VibeCode - Mobile App

React Native mobile application for iOS and Android.

## Prerequisites

- Node.js 16+
- Expo CLI: `npm install -g expo-cli`
- iOS: Xcode (Mac only) or Expo Go app
- Android: Android Studio or Expo Go app

## Installation

```bash
cd frontend
npm install
```

## Development

### Run on Device

```bash
# Start Expo
npm start

# Scan QR code with:
# - Expo Go app (recommended for testing)
# - iPhone camera app (for iOS)
# - Android phone camera app
```

### Run on Emulator

```bash
# Android Emulator
npm run android

# iOS Simulator (Mac only)
npm run ios
```

## Building

### Android APK

```bash
eas build --platform android
```

### iOS App

```bash
eas build --platform ios
```

## Environment Setup

Create a `.env` file in the frontend directory:

```
REACT_APP_API_URL=http://your-backend:8000/api
REACT_APP_WS_URL=ws://your-backend:8000
```

## Features

- Phone authentication with OTP
- Real-time messaging
- Group chats
- Status updates
- Media sharing
- Push notifications
- End-to-end encryption

## Project Structure

```
src/
├── screens/          # App screens
├── services/         # API, WebSocket, etc.
├── store/           # Redux store
├── navigation/      # Screen navigation
├── utils/           # Utilities
└── assets/          # Images, fonts, etc.
```

## Testing

```bash
npm test
```

## Troubleshooting

### Port Already in Use

```bash
lsof -i :19000
kill -9 <PID>
```

### Clear Cache

```bash
expo start --clear
```

### Dependencies Issue

```bash
rm -rf node_modules package-lock.json
npm install
```

