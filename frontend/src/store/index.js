import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import authReducer from './reducers/authReducer';
import chatReducer from './reducers/chatReducer';
import userReducer from './reducers/userReducer';

const rootReducer = combineReducers({
  auth: authReducer,
  chat: chatReducer,
  user: userReducer,
});

const store = createStore(rootReducer, applyMiddleware(thunk));

export default store;
