import AsyncStorage from '@react-native-async-storage/async-storage';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

export class WebSocketService {
  constructor() {
    this.callbacks = {};
    this.reconnectTimer = null;
  }

  async connect(chatId, token, isGroup = false) {
    const endpoint = isGroup ? 'group' : 'chat';
    const url = `${WS_URL}/ws/${endpoint}/${chatId}/?token=${token}`;

    return new Promise((resolve, reject) => {
      try {
        socket = new WebSocket(url);

        socket.onopen = () => {
          console.log('WebSocket connected');
          reconnectAttempts = 0;
          resolve();
        };

        socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        };

        socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        socket.onclose = () => {
          console.log('WebSocket disconnected');
          this.attemptReconnect(chatId, token, isGroup);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  handleMessage(data) {
    const messageType = data.type;
    if (this.callbacks[messageType]) {
      this.callbacks[messageType](data);
    }
  }

  subscribe(messageType, callback) {
    this.callbacks[messageType] = callback;
  }

  unsubscribe(messageType) {
    delete this.callbacks[messageType];
  }

  send(data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  sendMessage(content, messageType = 'TEXT') {
    this.send({
      type: 'text_message',
      content,
      message_type: messageType,
    });
  }

  sendTyping(isTyping) {
    this.send({
      type: 'typing',
      is_typing: isTyping,
    });
  }

  sendReadReceipt(messageId) {
    this.send({
      type: 'read_receipt',
      message_id: messageId,
    });
  }

  editMessage(messageId, newContent) {
    this.send({
      type: 'message_edit',
      message_id: messageId,
      content: newContent,
    });
  }

  deleteMessage(messageId, mode = 'self_only') {
    this.send({
      type: 'message_delete',
      message_id: messageId,
      mode,
    });
  }

  addReaction(messageId, emoji) {
    this.send({
      type: 'reaction_add',
      message_id: messageId,
      emoji,
    });
  }

  removeReaction(messageId, emoji) {
    this.send({
      type: 'reaction_remove',
      message_id: messageId,
      emoji,
    });
  }

  attemptReconnect(chatId, token, isGroup) {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      this.reconnectTimer = setTimeout(() => {
        console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        this.connect(chatId, token, isGroup).catch((error) => {
          console.error('Reconnection failed:', error);
        });
      }, RECONNECT_DELAY);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    if (socket) {
      socket.close();
      socket = null;
    }
  }

  isConnected() {
    return socket && socket.readyState === WebSocket.OPEN;
  }
}

export default new WebSocketService();
