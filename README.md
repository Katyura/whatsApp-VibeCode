# WhatsApp VibeCode

A WhatsApp-like messaging application with text, media, status updates, and single-device user authentication.

## Features

- **Phone Number Authentication**: Sign up and login with phone number + SMS OTP verification
- **1-on-1 Messaging**: Real-time text messaging between users with WebSocket support
- **Group Messaging**: Create groups and send messages to multiple users
- **Read Receipts**: Track message delivery and read status
- **Typing Indicators**: See when users are typing
- **Message Management**: Edit and delete messages
- **Message Reactions**: React to messages with emojis
- **Status Updates**: 24-hour status stories with selective visibility
- **Last Seen**: Track user activity and last seen timestamps
- **Single Device Login**: Enforce single device login per user
- **End-to-End Encryption**: Device-level encryption for messages
- **Media Sharing**: P2P file transfer with client-side compression
- **Push Notifications**: Firebase Cloud Messaging for offline notifications

## Tech Stack

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Real-time**: Django Channels + WebSocket
- **Authentication**: JWT + Phone OTP
- **File Transfer**: WebRTC P2P
- **Encryption**: RSA/AES
- **Push Notifications**: Firebase Cloud Messaging
- **Task Queue**: Celery + Redis

### Frontend
- **Framework**: React Native (Expo)
- **State Management**: Redux
- **API Client**: Axios
- **WebSocket**: Native WebSocket
- **Local Storage**: AsyncStorage
- **Notifications**: Expo Notifications

## Setup Instructions

### Backend
1. Navigate to backend directory: `cd backend`
2. Create virtual environment and install dependencies: `pip install -r requirements.txt`
3. Configure .env file with database and API credentials
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

### Frontend
1. Navigate to frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Configure API endpoint in `src/services/api.js`
4. Start Expo: `npm start`

## Project Architecture

The application uses a modern stack with:
- **Backend**: Django + PostgreSQL + Django Channels
- **Frontend**: React Native with Redux state management
- **Real-time**: WebSocket for instant messaging
- **Authentication**: JWT tokens with phone OTP
- **Security**: End-to-end encryption at device level

## Key Components

### Backend
- User authentication with OTP
- Chat and Group models
- Message storage with encryption support
- WebSocket consumers for real-time messaging
- Status update system with 24-hour expiry
- Notification system

### Frontend  
- Redux store for state management
- Authentication screens (phone + OTP)
- Chat list and chat screens
- Status creation and viewing
- User profile management

## API Documentation

Full API documentation is available at `/api/docs` when running the backend.

Key endpoints:
- `POST /api/auth/send-otp/` - Request OTP
- `POST /api/auth/verify-otp/` - Verify OTP
- `GET/POST /api/messages/chats/` - Chat management
- `GET/POST /api/status/` - Status management
- `WS /ws/chat/{chat_id}/` - WebSocket for chat
- `WS /ws/group/{group_id}/` - WebSocket for group

## Security

- Phone number based authentication
- JWT token validation
- Single device login enforcement
- End-to-end encryption
- Secure token storage
- Input validation on all endpoints
- Rate limiting on authentication

## Installation & Deployment Guide

### Requirements
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### Production Deployment
- Use Gunicorn for Django
- Setup Nginx as reverse proxy
- Enable SSL/TLS certificates
- Configure environment variables
- Use production database
- Setup monitoring and logging

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

MIT License - See LICENSE file for details.
