const initialState = {
  chats: [],
  currentChat: null,
  messages: [],
  loading: false,
  error: null,
};

export default function chatReducer(state = initialState, action) {
  switch (action.type) {
    case 'SET_CHATS':
      return { ...state, chats: action.payload };
    case 'SET_CURRENT_CHAT':
      return { ...state, currentChat: action.payload };
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    default:
      return state;
  }
}
