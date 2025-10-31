import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from './api';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export const notificationService = {
  // Initialize notifications
  initNotifications: async () => {
    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('Failed to get push token for push notification!');
        return;
      }

      // Get FCM token
      const token = await Notifications.getExpoPushTokenAsync();
      console.log('Push token:', token.data);

      // Send to backend to save
      try {
        const userId = await AsyncStorage.getItem('userId');
        // You would send this to backend to store with device
        await AsyncStorage.setItem('fcmToken', token.data);
      } catch (error) {
        console.error('Error saving FCM token:', error);
      }

      return token.data;
    } catch (error) {
      console.error('Error initializing notifications:', error);
    }
  },

  // Subscribe to notification events
  subscribeToNotifications: (callback) => {
    const subscription = Notifications.addNotificationResponseReceivedListener((response) => {
      const { notification } = response;
      console.log('Notification received:', notification);
      
      if (callback) {
        callback(notification);
      }
    });

    return subscription;
  },

  // Handle local notifications
  sendLocalNotification: async (title, body, data = {}) => {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: true,
        },
        trigger: {
          seconds: 1,
        },
      });
    } catch (error) {
      console.error('Error sending local notification:', error);
    }
  },

  // Cancel all notifications
  cancelAllNotifications: async () => {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
    } catch (error) {
      console.error('Error canceling notifications:', error);
    }
  },
};

export default notificationService;
