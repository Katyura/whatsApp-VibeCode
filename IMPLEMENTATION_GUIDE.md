# WhatsApp VibeCode - Implementation Guide

This guide provides step-by-step instructions for setting up and running the WhatsApp VibeCode application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the Application](#running-the-application)
5. [Database Migrations](#database-migrations)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Git

### Dependencies Installation
```bash
# Python packages
pip install --upgrade pip setuptools wheel

# Node.js packages (already in package.json)
npm install -g expo-cli
```

## Backend Setup

### Step 1: Install Python Dependencies

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (PostgreSQL)
DB_NAME=whatsapp_vibecode
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Twilio SMS (optional, for development use print-to-console)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Firebase (optional for push notifications)
FIREBASE_CREDENTIALS_PATH=
```

### Step 3: Setup PostgreSQL Database

```bash
# Create database
createdb whatsapp_vibecode

# Or using PostgreSQL CLI
psql -U postgres
CREATE DATABASE whatsapp_vibecode;
```

### Step 4: Run Database Migrations

```bash
python manage.py migrate
```

### Step 5: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 6: Start Development Services

You'll need to run these in separate terminal windows:

**Terminal 1: Django Development Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2: Celery Worker** (for background tasks)
```bash
celery -A config worker -l info
```

**Terminal 3: Celery Beat** (for scheduled tasks)
```bash
celery -A config beat -l info
```

**Terminal 4: Redis** (if not running via Docker)
```bash
redis-server
```

Or use Docker Compose:
```bash
docker-compose up -d
```

## Frontend Setup

### Step 1: Install Node Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure API Endpoint

Edit `src/services/api.js` to point to your backend:

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
```

### Step 3: Install Expo CLI (if not already installed)

```bash
npm install -g expo-cli
```

## Running the Application

### Development Mode

1. **Start Backend** (from backend directory):
```bash
python manage.py runserver
```

2. **Start Frontend** (from frontend directory in a new terminal):
```bash
npm start
```

3. **Connect to App**:
   - Web: Visit `http://localhost:19006` (Web preview)
   - Android: Scan QR code with Android device
   - iOS: Scan QR code with iOS device
   - Emulator: Press 'a' for Android or 'i' for iOS in Expo CLI

### Using Docker Compose

For easier local development, use Docker Compose to run PostgreSQL and Redis:

```bash
# From project root
docker-compose up -d

# Run Django migrations
cd backend
python manage.py migrate

# Start Django
python manage.py runserver

# In another terminal, start frontend
cd frontend
npm start
```

## Database Migrations

### Creating Migrations

When you modify models, create migrations:

```bash
python manage.py makemigrations
```

### Applying Migrations

```bash
python manage.py migrate
```

### Checking Migration Status

```bash
python manage.py showmigrations
```

## Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

### Run Specific Tests

```bash
python manage.py test apps.users.tests
python manage.py test apps.messages.tests.ChatModelTests
```

## Admin Interface

Access Django admin at: `http://localhost:8000/admin`

Use the superuser credentials you created earlier to log in.

### Available Admin Pages
- Users: View and manage user accounts
- Devices: Track active devices per user
- Chats: View 1-on-1 chats
- Groups: Manage groups
- Messages: View message records
- Status Updates: Monitor statuses
- Notifications: Track notifications

## API Documentation

### Interactive API Documentation

Swagger UI: `http://localhost:8000/api/docs/`

ReDoc: `http://localhost:8000/api/redoc/`

### Sample API Calls

```bash
# Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'

# Verify OTP
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp": "123456",
    "device_id": "device-uuid",
    "device_name": "Mobile Device"
  }'

# Get Chats
curl -X GET http://localhost:8000/api/messages/chats/ \
  -H "Authorization: Bearer your-jwt-token"
```

## WebSocket Connection

### Connect to Chat WebSocket

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/chat/chat-id/?token=your-jwt-token');

socket.onopen = () => console.log('Connected');

// Send message
socket.send(JSON.stringify({
  type: 'text_message',
  content: 'Hello!',
  message_type: 'TEXT'
}));

// Receive message
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message received:', data);
};
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
python manage.py runserver 8001
```

### PostgreSQL Connection Error

Make sure PostgreSQL is running:

```bash
# On macOS with Homebrew
brew services start postgresql

# On Linux
sudo systemctl start postgresql
```

### Redis Connection Error

Make sure Redis is running:

```bash
# On macOS with Homebrew
brew services start redis

# On Linux
sudo systemctl start redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

### WebSocket Connection Issues

1. Check if backend is running with Daphne/Channels support
2. Verify Redis is running (required for Channels)
3. Check WebSocket URL matches your backend

### Django Migrations Conflict

```bash
# Create new empty migration
python manage.py makemigrations --empty apps.users --name fix_conflict

# Manually resolve conflict, then apply
python manage.py migrate
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Django debug mode | `True` or `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `whatsapp_vibecode` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `TWILIO_ACCOUNT_SID` | Twilio account | `your-sid` |
| `TWILIO_AUTH_TOKEN` | Twilio token | `your-token` |
| `TWILIO_PHONE_NUMBER` | Twilio phone | `+1234567890` |

## Next Steps

1. **Customize**: Modify UI components to match your branding
2. **Test**: Create comprehensive test suites
3. **Deploy**: Follow deployment guide for production
4. **Monitor**: Setup logging and monitoring
5. **Scale**: Consider caching strategies and database optimization

## Support

For issues, please:
1. Check this guide's troubleshooting section
2. Review Django and React Native documentation
3. Create an issue on GitHub with detailed information

## References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Channels](https://channels.readthedocs.io/)
- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [Redux Documentation](https://redux.js.org/)
