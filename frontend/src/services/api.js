import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Add token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('userToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  sendOTP: (phoneNumber) =>
    api.post('/auth/send-otp/', { phone_number: phoneNumber }),
  
  verifyOTP: (phoneNumber, otp, deviceId, deviceName) =>
    api.post('/auth/verify-otp/', {
      phone_number: phoneNumber,
      otp,
      device_id: deviceId,
      device_name: deviceName,
    }),
  
  logout: () => api.post('/auth/logout/'),
};

export const userService = {
  getProfile: (userId) => api.get(`/users/${userId}/`),
  
  updateProfile: (data) => api.put('/users/profile/', data),
  
  searchUsers: (phone) => api.get('/users/search/', { params: { phone } }),
  
  uploadProfilePicture: (file) => {
    const formData = new FormData();
    formData.append('profile_picture', file);
    return api.post('/users/profile-picture/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const chatService = {
  getChats: () => api.get('/messages/chats/'),
  
  createChat: (userId) => api.post('/messages/chats/', { user_id: userId }),
  
  getMessages: (chatId, page = 0, limit = 50) =>
    api.get(`/messages/chats/${chatId}/messages/`, {
      params: { page, limit },
    }),
  
  sendMessage: (data) => api.post('/messages/send/', data),
  
  editMessage: (data) => api.patch('/messages/edit/', data),
  
  addReaction: (data) => api.post('/messages/react/', data),
};

export const groupService = {
  createGroup: (data) => api.post('/messages/groups/', data),
  
  getGroup: (groupId) => api.get(`/messages/groups/${groupId}/`),
  
  updateGroup: (groupId, data) => api.put(`/messages/groups/${groupId}/`, data),
  
  addMember: (groupId, userId) =>
    api.post(`/messages/groups/${groupId}/add_member/`, { user_id: userId }),
  
  removeMember: (groupId, userId) =>
    api.delete(`/messages/groups/${groupId}/members/${userId}/`),
  
  leaveGroup: (groupId) => api.post(`/messages/groups/${groupId}/leave/`),
};

export const statusService = {
  getFeed: () => api.get('/status/feed/'),
  
  createStatus: (data) => api.post('/status/create/', data),
  
  getStatus: (statusId) => api.get(`/status/${statusId}/`),
  
  recordView: (statusId) => api.post('/status/view/', { status_id: statusId }),
  
  deleteStatus: (statusId) => api.delete(`/status/${statusId}/`),
};

export default api;
