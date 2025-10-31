# Mobile App Setup Guide

## Development Setup

### 1. Install Expo CLI
```bash
npm install -g expo-cli
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Start Development Server
```bash
npm start
```

### 4. Run on Device
- **iPhone**: Use Expo Go app to scan QR code
- **Android**: Use Expo Go app to scan QR code

### 5. Run on Emulator
```bash
npm run android    # Android Emulator
npm run ios        # iOS Simulator (Mac only)
```

## Testing on Real Devices

### iOS
1. Install Expo Go app from App Store
2. Run `npm start`
3. Scan QR code with iPhone camera
4. Tap notification to open in Expo Go

### Android
1. Install Expo Go app from Google Play Store
2. Run `npm start`
3. Scan QR code with Expo Go app
4. App opens automatically

## Building for Production

### Prerequisites
- EAS account: https://expo.dev
- Run: `eas build:configure`

### Build Android APK
```bash
eas build --platform android --local
```

### Build iOS IPA
```bash
eas build --platform ios
```

### Submit to Stores
```bash
# Google Play Store
eas submit --platform android

# Apple App Store
eas submit --platform ios
```

## Environment Variables

Create `frontend/.env`:
```
REACT_APP_API_URL=http://your-server:8000/api
REACT_APP_WS_URL=ws://your-server:8000
```

## Common Issues

### Build Fails on iOS
```bash
# Clear build cache
eas build:cache --platform ios --clear

# Rebuild
eas build --platform ios
```

### Build Fails on Android
```bash
# Increase Java heap
export _JAVA_OPTIONS="-Xmx4g"
eas build --platform android
```

### App Crashes on Start
1. Check console: `npm start`
2. View logs: Select device in Expo CLI
3. Check API connection in services/api.js

### WebSocket Not Connecting
1. Verify backend URL in services/websocket.js
2. Ensure backend is running
3. Check network connectivity
4. Verify device can reach backend server

## Device Permissions

App requires:
- Camera (for media)
- Photo Library (for images/videos)
- Microphone (for voice messages)
- Location (for location sharing - optional)

Permissions are requested on first use.

## Performance Tips

1. **Reduce APK Size**: Remove unused assets
2. **Optimize Images**: Compress before use
3. **Lazy Load Screens**: Import screens dynamically
4. **Monitor Performance**: Use React DevTools

## Debug Mode

```bash
# Enable debug menu
npm start

# Press:
# - 'd' for Debugger
# - 'm' for Dev Menu
# - 'r' to reload
```

## Offline Support

App stores:
- User tokens in secure storage
- Chat history locally
- Syncs when online

## Updates

### Hot Reload
Changes auto-reload in development.

### Over-the-Air Updates
```bash
expo update
```

### App Store Updates
Submit new version to app stores.

