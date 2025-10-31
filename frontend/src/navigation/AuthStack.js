import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import PhoneAuthScreen from '../screens/PhoneAuthScreen';
import OTPVerificationScreen from '../screens/OTPVerificationScreen';

const Stack = createNativeStackNavigator();

export default function AuthStack({ authContext }) {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen
        name="PhoneAuth"
        component={PhoneAuthScreen}
        options={{ animationEnabled: false }}
      />
      <Stack.Screen
        name="OTPVerification"
        component={OTPVerificationScreen}
        options={{ animationEnabled: false }}
      />
    </Stack.Navigator>
  );
}
