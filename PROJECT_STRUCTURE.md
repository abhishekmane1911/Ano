# Ano Platform - Project Structure

## Directory Layout

```
Ano/
├── .git/                       # Git repository
├── .gitignore                  # Root gitignore
├── docker-compose.yml          # PostgreSQL & Redis services
├── README.md                   # Project documentation
├── PROJECT_STRUCTURE.md        # This file
├── start-dev.sh               # Development startup script
│
├── frontend/                   # React + TypeScript frontend
│   ├── node_modules/          # NPM dependencies
│   ├── public/                # Static assets
│   ├── src/                   # Source code
│   │   ├── assets/           # Images, fonts, etc.
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── store/            # Zustand state management
│   │   ├── services/         # API services
│   │   ├── utils/            # Utility functions
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx           # Main app component
│   │   └── main.tsx          # Entry point
│   ├── .env                   # Environment variables (gitignored)
│   ├── .env.example           # Environment template
│   ├── .gitignore             # Frontend gitignore
│   ├── .prettierrc            # Prettier configuration
│   ├── .prettierignore        # Prettier ignore rules
│   ├── eslint.config.js       # ESLint configuration
│   ├── index.html             # HTML template
│   ├── package.json           # NPM dependencies & scripts
│   ├── tsconfig.json          # TypeScript configuration
│   └── vite.config.ts         # Vite configuration
│
└── backend/                    # Django REST API backend
    ├── venv/                  # Python virtual environment (gitignored)
    ├── media/                 # User uploaded files (gitignored)
    ├── staticfiles/           # Collected static files (gitignored)
    │
    ├── ano_backend/           # Django project settings
    │   ├── __init__.py       # Celery app import
    │   ├── settings.py       # Django settings
    │   ├── urls.py           # Root URL configuration
    │   ├── wsgi.py           # WSGI application
    │   ├── asgi.py           # ASGI application (Channels)
    │   └── celery.py         # Celery configuration
    │
    ├── authentication/        # Auth app (registration, login, JWT)
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py         # Custom User model
    │   ├── serializers.py    # DRF serializers
    │   ├── views.py          # API views
    │   ├── urls.py           # App URLs
    │   └── tests.py          # Tests
    │
    ├── profiles/              # Profile app (anonymous profiles)
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py         # Profile model
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests.py
    │
    ├── chat/                  # Chat app (chatrooms, messages, WebSocket)
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py         # Chatroom, Message, Reaction, ReadReceipt
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── consumers.py      # WebSocket consumers
    │   ├── routing.py        # WebSocket routing
    │   └── tests.py
    │
    ├── matchmaking/           # Matchmaking app (swipes, matches)
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py         # Swipe, Match models
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── consumers.py      # Match chat WebSocket
    │   └── tests.py
    │
    ├── reports/               # Reports app (reports, blocks)
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py         # Report, Block models
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests.py
    │
    ├── admin_dashboard/       # Admin app (moderation, metrics)
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests.py
    │
    ├── .env                   # Environment variables (gitignored)
    ├── .env.example           # Environment template
    ├── .gitignore             # Backend gitignore
    ├── .flake8                # Flake8 configuration
    ├── pyproject.toml         # Black & pytest configuration
    ├── manage.py              # Django management script
    ├── requirements.txt       # Python dependencies
    └── requirements-dev.txt   # Development dependencies
```

## Key Configuration Files

### Frontend
- **vite.config.ts**: Vite build configuration
- **tsconfig.json**: TypeScript compiler options
- **eslint.config.js**: ESLint rules for code quality
- **.prettierrc**: Code formatting rules
- **package.json**: Dependencies and npm scripts

### Backend
- **settings.py**: Django configuration (database, apps, middleware)
- **asgi.py**: ASGI configuration for WebSockets
- **celery.py**: Celery task queue configuration
- **.flake8**: Python linting rules
- **pyproject.toml**: Black formatter and pytest configuration
- **requirements.txt**: Python package dependencies

### Infrastructure
- **docker-compose.yml**: PostgreSQL and Redis containers
- **.env**: Environment-specific configuration (not in git)
- **.env.example**: Template for environment variables

## Development Workflow

1. **Start services**: `docker-compose up -d`
2. **Backend**: `cd backend && source venv/bin/activate && python manage.py runserver`
3. **Frontend**: `cd frontend && npm run dev`
4. **Or use**: `./start-dev.sh` to start everything

## Code Quality Tools

### Frontend
- **ESLint**: `npm run lint`
- **Prettier**: `npm run format`
- **TypeScript**: `tsc --noEmit`

### Backend
- **Flake8**: `flake8`
- **Black**: `black .`
- **Tests**: `pytest`

## Next Steps

Follow the implementation tasks in `.kiro/specs/ano-platform/tasks.md` to build out the application features.
