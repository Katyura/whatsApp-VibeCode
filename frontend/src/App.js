import React, { useEffect, useReducer } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Provider } from 'react-redux';
import store from './store';
import AuthStack from './navigation/AuthStack';
import AppStack from './navigation/AppStack';

const AuthContext = React.createContext();

export { AuthContext };

export default function App() {
  const [state, dispatch] = useReducer(
    (prevState, action) => {
      switch (action.type) {
        case 'RESTORE_TOKEN':
          return {
            ...prevState,
            userToken: action.payload,
            isLoading: false,
          };
        case 'SIGN_IN':
          return {
            ...prevState,
            isSignout: false,
            userToken: action.payload,
          };
        case 'SIGN_OUT':
          return {
            ...prevState,
            isSignout: true,
            userToken: null,
          };
      }
    },
    {
      isLoading: true,
      isSignout: false,
      userToken: null,
    }
  );

  useEffect(() => {
    const bootstrapAsync = async () => {
      let userToken;
      try {
        userToken = await AsyncStorage.getItem('userToken');
      } catch (e) {
        // Restoring token failed
      }

      dispatch({ type: 'RESTORE_TOKEN', payload: userToken });
    };

    bootstrapAsync();
  }, []);

  const authContext = React.useMemo(
    () => ({
      signIn: async (token) => {
        try {
          await AsyncStorage.setItem('userToken', token);
        } catch (e) {
          console.error(e);
        }
        dispatch({ type: 'SIGN_IN', payload: token });
      },
      signOut: async () => {
        try {
          await AsyncStorage.removeItem('userToken');
        } catch (e) {
          console.error(e);
        }
        dispatch({ type: 'SIGN_OUT' });
      },
      signUp: async (token) => {
        try {
          await AsyncStorage.setItem('userToken', token);
        } catch (e) {
          console.error(e);
        }
        dispatch({ type: 'SIGN_IN', payload: token });
      },
    }),
    []
  );

  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <NavigationContainer>
          {state.isLoading ? null : state.userToken == null ? (
            <AuthStack authContext={authContext} />
          ) : (
            <AppStack authContext={authContext} />
          )}
        </NavigationContainer>
      </SafeAreaProvider>
    </Provider>
  );
}
