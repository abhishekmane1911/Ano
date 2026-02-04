# Ano - Anonymous Chat & Matchmaking Platform

An anonymous chatting and matchmaking platform exclusively for IIT Indore students. Ano enables students to communicate anonymously in public chatrooms and engage in Tinder-style matchmaking while maintaining complete anonymity through UUID-based identifiers.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [WebSocket Events](#websocket-events)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Documentation](#documentation)

## ✨ Features

### Core Features
- **Anonymous Authentication**: IIT Indore email verification (@iiti.ac.in) with JWT tokens
- **Anonymous Profiles**: UUID-based profiles with interests, hobbies, and anonymized avatars
- **Public Chatrooms**: Real-time group chat with typing indicators and read receipts
- **Matchmaking**: Tinder-style swipe interface for anonymous connections
- **Match Chat**: Private one-on-one anonymous messaging with matches
- **Safety Features**: User reporting, blocking, and admin moderation tools
- **Search**: Full-text search across message history
- **Themes**: Light and dark mode support
- **Responsive Design**: Mobile-first design optimized for all devices

### Security Features
- Argon2 password hashing
- JWT authentication with refresh tokens
- CSRF protection
- Rate limiting on all endpoints
- Input validation and sanitization
- HTTPS enforcement
- File upload validation and scanning

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (React + TypeScript)               │
│  Zustand State Management | Framer Motion | Tailwind CSS    │
└─────────────────────────────────────────────────────────────┘
                            │
                    HTTPS / WebSocket
                            │
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Nginx)                       │
│         CORS | Rate Limiting | SSL Termination              │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│   REST API     │                    │   WebSocket     │
│  (Django DRF)  │                    │   (Channels)    │
└───────┬────────┘                    └────────┬────────┘
        │                                      │
┌───────▼──────────────────────────────────────▼─────────┐
│              Django Application Layer                   │
│  Auth | Profiles | Chat | Matchmaking | Reports        │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│   PostgreSQL   │                    │     Redis       │
│   (Database)   │                    │  (Cache/Queue)  │
└────────────────┘                    └─────────────────┘
```

## 📦 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Git**
- **PostgreSQL** 15+ (via Docker)
- **Redis** 7+ (via Docker)

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd Ano

# Start database services
docker-compose up -d

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend setup (in new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## 💻 Development Setup

### Backend Setup (Detailed)

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (see Environment Variables section)

# Run database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

**Backend Development Commands:**
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Format code
black .

# Lint code
flake8

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create Django app
python manage.py startapp app_name

# Run Celery worker (for async tasks)
celery -A ano_backend worker -l info

# Run Django shell
python manage.py shell
```

### Frontend Setup (Detailed)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start development server
npm run dev
```

**Frontend Development Commands:**
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## 🔧 Environment Variables

### Backend Environment Variables

Create `backend/.env` from `backend/.env.example`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ano_db
DB_USER=ano_user
DB_PASSWORD=ano_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT Settings (in minutes)
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend Environment Variables

Create `frontend/.env` from `frontend/.env.example`:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000/ws

# Environment
VITE_ENV=development
```

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest authentication/tests.py

# Run specific test
pytest authentication/tests.py::TestUserRegistration::test_valid_registration

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## 📚 API Documentation

See [docs/API.md](docs/API.md) for complete API documentation.

### Quick API Reference

**Authentication:**
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout

**Profiles:**
- `POST /api/profiles/` - Create profile
- `GET /api/profiles/me/` - Get own profile
- `PUT /api/profiles/me/` - Update profile
- `GET /api/profiles/{uuid}/` - Get profile by UUID

**Chat:**
- `GET /api/chatrooms/` - List chatrooms
- `GET /api/chatrooms/{uuid}/messages/` - Get messages
- `POST /api/chatrooms/{uuid}/messages/` - Send message

**Matchmaking:**
- `GET /api/matchmaking/profiles/` - Get profiles to swipe
- `POST /api/matchmaking/swipe/` - Record swipe
- `GET /api/matchmaking/matches/` - Get matches

**Reports:**
- `POST /api/reports/` - Create report
- `POST /api/reports/block/` - Block user

## 🔌 WebSocket Events

See [docs/WEBSOCKETS.md](docs/WEBSOCKETS.md) for complete WebSocket documentation.

### Chat WebSocket (`/ws/chat/{chatroom_uuid}/`)

**Client → Server:**
- `message.send` - Send message
- `message.edit` - Edit message
- `message.delete` - Delete message
- `message.react` - React to message
- `typing.start` - Start typing
- `typing.stop` - Stop typing

**Server → Client:**
- `message.receive` - New message
- `message.updated` - Message edited
- `message.deleted` - Message deleted
- `message.reaction` - New reaction
- `typing.indicator` - User typing
- `user.joined` - User joined
- `user.left` - User left

## 🚢 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

### Quick Production Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## 📁 Project Structure

```
Ano/
├── backend/                    # Django backend
│   ├── ano_backend/           # Main Django project
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py            # URL routing
│   │   ├── middleware.py      # Custom middleware
│   │   └── logging_config.py  # Logging configuration
│   ├── authentication/        # Auth app
│   ├── profiles/              # Profile management
│   ├── chat/                  # Chat and messaging
│   ├── matchmaking/           # Swipe and match
│   ├── reports/               # Reports and blocking
│   ├── admin_dashboard/       # Admin tools
│   ├── manage.py              # Django management
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend Docker image
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── auth/          # Authentication UI
│   │   │   ├── profile/       # Profile UI
│   │   │   ├── chat/          # Chat UI
│   │   │   ├── matchmaking/   # Matchmaking UI
│   │   │   ├── safety/        # Safety features UI
│   │   │   ├── admin/         # Admin dashboard UI
│   │   │   └── common/        # Shared components
│   │   ├── api/               # API client functions
│   │   ├── stores/            # Zustand state stores
│   │   ├── services/          # WebSocket services
│   │   ├── hooks/             # Custom React hooks
│   │   ├── contexts/          # React contexts
│   │   ├── styles/            # Global styles
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.js     # Tailwind configuration
│   └── Dockerfile             # Frontend Docker image
├── docs/                      # Documentation
│   ├── API.md                 # API documentation
│   ├── WEBSOCKETS.md          # WebSocket documentation
│   └── DEVELOPER_GUIDE.md     # Developer onboarding
├── docker-compose.yml         # Development services
├── docker-compose.prod.yml    # Production services
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Backend**: Follow PEP 8, use Black for formatting, Flake8 for linting
- **Frontend**: Follow ESLint rules, use Prettier for formatting
- **Commits**: Use conventional commit messages

## 📖 Documentation

- [API Documentation](docs/API.md) - Complete REST API reference
- [WebSocket Documentation](docs/WEBSOCKETS.md) - WebSocket events and payloads
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Developer onboarding guide
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Environment Variables](docs/ENVIRONMENT.md) - Complete environment variable reference

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Socket.IO** - WebSocket client
- **Axios** - HTTP client
- **Framer Motion** - Animations
- **React Router v6** - Routing

### Backend
- **Django 5.2** - Web framework
- **Django REST Framework** - API framework
- **Django Channels** - WebSocket support
- **PostgreSQL 15+** - Database
- **Redis 7+** - Cache and message broker
- **Celery** - Async task queue
- **djangorestframework-simplejwt** - JWT authentication
- **Argon2** - Password hashing

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Gunicorn** - WSGI server
- **Daphne** - ASGI server

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review the [Developer Guide](docs/DEVELOPER_GUIDE.md)

## 🔒 Security

- All user identifiers are UUID-based for anonymity
- No personal information exposed in any API response
- JWT tokens with secure HTTP-only cookies
- Rate limiting on all endpoints
- Input validation and sanitization
- HTTPS enforcement in production
- Regular security audits recommended

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Voice/video chat
- [ ] AI-powered content moderation
- [ ] Advanced matching algorithms
- [ ] Analytics dashboard
- [ ] Multi-language support
