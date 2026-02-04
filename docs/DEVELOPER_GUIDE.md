# Developer Onboarding Guide

Welcome to the Ano platform development team! This guide will help you get up to speed with the codebase, development workflow, and best practices.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [Development Workflow](#development-workflow)
4. [Code Organization](#code-organization)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Common Tasks](#common-tasks)
8. [Debugging Tips](#debugging-tips)
9. [Deployment Process](#deployment-process)
10. [Resources](#resources)

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Git** installed and configured
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Code Editor** (VS Code recommended)
- **PostgreSQL** client (optional, for database inspection)

### Initial Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Ano
```

2. **Set up backend**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
```

3. **Set up frontend**:
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your settings
```

4. **Start services**:
```bash
# Terminal 1: Database services
docker-compose up -d

# Terminal 2: Backend
cd backend
source venv/bin/activate
python manage.py runserver

# Terminal 3: Frontend
cd frontend
npm run dev

# Terminal 4: Celery (for async tasks)
cd backend
source venv/bin/activate
celery -A ano_backend worker -l info
```

5. **Verify setup**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Admin panel: http://localhost:8000/admin

### IDE Setup (VS Code)

Recommended extensions:

**Python**:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- Django

**JavaScript/TypeScript**:
- ESLint
- Prettier
- TypeScript Vue Plugin (Volar)
- Tailwind CSS IntelliSense

**General**:
- GitLens
- Docker
- REST Client
- Thunder Client (API testing)

**VS Code Settings** (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Architecture Overview

### High-Level Architecture

```
Frontend (React) ←→ API Gateway (Nginx) ←→ Backend (Django)
                                              ↓
                                         PostgreSQL
                                              ↓
                                           Redis
```

### Backend Architecture

**Django Apps**:
- `authentication`: User registration, login, JWT tokens
- `profiles`: Anonymous user profiles
- `chat`: Public chatrooms and messaging
- `matchmaking`: Swipe interface and matches
- `reports`: User reports and blocking
- `admin_dashboard`: Admin moderation tools

**Key Concepts**:
- **Anonymity**: All user-facing IDs are UUIDs
- **Security**: JWT auth, rate limiting, input validation
- **Real-time**: WebSocket via Django Channels
- **Async Tasks**: Celery for emails and media processing

### Frontend Architecture

**Structure**:
```
src/
├── components/     # React components
├── api/           # API client functions
├── stores/        # Zustand state management
├── services/      # WebSocket and other services
├── hooks/         # Custom React hooks
├── contexts/      # React contexts
└── styles/        # Global styles
```

**State Management**:
- **Zustand**: Lightweight state management
- **React Query**: Server state (if needed)
- **Context**: Theme, auth state

**Routing**:
- React Router v6 for client-side routing
- Protected routes for authenticated pages

## Development Workflow

### Git Workflow

We follow a feature branch workflow:

1. **Create feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and commit**:
```bash
git add .
git commit -m "feat: add user profile editing"
```

3. **Push and create PR**:
```bash
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

4. **Code review and merge**:
- Request review from team members
- Address feedback
- Merge after approval

### Commit Message Convention

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(auth): add password reset functionality
fix(chat): resolve message duplication issue
docs(api): update authentication endpoints
```

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

## Code Organization

### Backend Structure

```
backend/
├── ano_backend/           # Main project
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   ├── middleware.py     # Custom middleware
│   └── logging_config.py # Logging setup
├── authentication/        # Auth app
│   ├── models.py         # User model
│   ├── views.py          # API views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # URL patterns
│   └── tests.py          # Tests
├── profiles/             # Profile app
├── chat/                 # Chat app
│   ├── models.py         # Chatroom, Message models
│   ├── consumers.py      # WebSocket consumers
│   ├── routing.py        # WebSocket routing
│   └── ...
└── ...
```

### Frontend Structure

```
frontend/src/
├── components/
│   ├── auth/             # Auth components
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   ├── chat/             # Chat components
│   │   ├── ChatWindow.tsx
│   │   └── MessageBubble.tsx
│   └── common/           # Shared components
│       ├── Navigation.tsx
│       └── ThemeToggle.tsx
├── api/
│   ├── auth.ts           # Auth API calls
│   ├── chat.ts           # Chat API calls
│   └── axios.ts          # Axios config
├── stores/
│   ├── authStore.ts      # Auth state
│   └── chatStore.ts      # Chat state
└── services/
    └── websocket.ts      # WebSocket service
```

## Coding Standards

### Python (Backend)

**Style Guide**: PEP 8

**Formatting**: Black (line length: 88)

**Linting**: Flake8

**Example**:
```python
from typing import Optional
from django.db import models
from uuid import uuid4


class Profile(models.Model):
    """Anonymous user profile."""
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    anonymous_id = models.UUIDField(unique=True, default=uuid4, db_index=True)
    age = models.IntegerField()
    interests = models.JSONField(default=list)
    
    class Meta:
        db_table = "profiles"
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        return f"Profile {self.anonymous_id}"
    
    def get_public_data(self) -> dict:
        """Return public profile data (no PII)."""
        return {
            "anonymous_id": str(self.anonymous_id),
            "age": self.age,
            "interests": self.interests,
        }
```

**Key Principles**:
- Type hints for function parameters and returns
- Docstrings for classes and complex functions
- Never expose email or real names in responses
- Use UUIDs for all public identifiers
- Validate all input data

### TypeScript (Frontend)

**Style Guide**: ESLint + Prettier

**Example**:
```typescript
import { useState, useEffect } from 'react';
import { Profile } from '../types';
import { getProfile } from '../api/profile';

interface ProfileCardProps {
  anonymousId: string;
  onSwipe: (direction: 'left' | 'right') => void;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({
  anonymousId,
  onSwipe,
}) => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getProfile(anonymousId);
        setProfile(data);
      } catch (error) {
        console.error('Failed to fetch profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [anonymousId]);

  if (loading) return <LoadingSkeleton />;
  if (!profile) return <ErrorMessage />;

  return (
    <div className="profile-card">
      <img src={profile.avatar} alt="Profile" />
      <h2>{profile.age} years old</h2>
      <div className="interests">
        {profile.interests.map((interest) => (
          <span key={interest} className="tag">
            {interest}
          </span>
        ))}
      </div>
      <div className="actions">
        <button onClick={() => onSwipe('left')}>Pass</button>
        <button onClick={() => onSwipe('right')}>Like</button>
      </div>
    </div>
  );
};
```

**Key Principles**:
- Use TypeScript for type safety
- Functional components with hooks
- Props interface for all components
- Error handling for async operations
- Accessibility (ARIA labels, keyboard navigation)

### CSS/Styling

**Framework**: Tailwind CSS

**Example**:
```tsx
<div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
  <div className="w-full max-w-md p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
      Welcome to Ano
    </h1>
    <button className="w-full px-4 py-2 text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
      Get Started
    </button>
  </div>
</div>
```

**Principles**:
- Mobile-first responsive design
- Dark mode support
- Consistent spacing and colors
- Smooth transitions and animations

## Testing Guidelines

### Backend Testing

**Framework**: pytest + Django TestCase

**Test Structure**:
```python
# tests.py
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Profile


class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@iiti.ac.in",
            password="TestPass123!"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_profile(self):
        """Test profile creation with valid data."""
        data = {
            "age": 21,
            "interests": ["coding", "music"],
            "relationship_intent": "friendship"
        }
        response = self.client.post("/api/profiles/", data)
        
        assert response.status_code == 201
        assert "anonymous_id" in response.data
        assert response.data["age"] == 21
    
    def test_profile_no_email_exposure(self):
        """Test that profile response never includes email."""
        profile = Profile.objects.create(user=self.user, age=21)
        response = self.client.get(f"/api/profiles/{profile.anonymous_id}/")
        
        assert "email" not in response.data
        assert "user" not in response.data
```

**Run Tests**:
```bash
# All tests
pytest

# Specific file
pytest authentication/tests.py

# With coverage
pytest --cov=. --cov-report=html

# Verbose
pytest -v
```

### Frontend Testing

**Framework**: Jest + React Testing Library (when implemented)

**Example**:
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('renders login form', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('validates email format', async () => {
    render(<LoginForm />);
    const emailInput = screen.getByLabelText(/email/i);
    
    fireEvent.change(emailInput, { target: { value: 'invalid' } });
    fireEvent.blur(emailInput);
    
    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

### Testing Best Practices

1. **Write tests for**:
   - API endpoints
   - Business logic
   - Edge cases
   - Error handling
   - Security features

2. **Don't test**:
   - Third-party libraries
   - Django/React internals
   - Trivial getters/setters

3. **Test naming**:
   - Descriptive names
   - Follow pattern: `test_<what>_<condition>_<expected>`
   - Example: `test_login_invalid_credentials_returns_401`

4. **Test organization**:
   - One test file per module
   - Group related tests in classes
   - Use setUp/tearDown for common setup

## Common Tasks

### Adding a New API Endpoint

1. **Create model** (if needed):
```python
# models.py
class NewModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    # ... fields
```

2. **Create serializer**:
```python
# serializers.py
class NewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewModel
        fields = ['id', 'field1', 'field2']
```

3. **Create view**:
```python
# views.py
from rest_framework import viewsets

class NewModelViewSet(viewsets.ModelViewSet):
    queryset = NewModel.objects.all()
    serializer_class = NewModelSerializer
    permission_classes = [IsAuthenticated]
```

4. **Add URL**:
```python
# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'newmodels', NewModelViewSet)

urlpatterns = router.urls
```

5. **Write tests**:
```python
# tests.py
def test_create_newmodel(self):
    # ... test code
```

### Adding a New React Component

1. **Create component file**:
```typescript
// components/NewComponent.tsx
import React from 'react';

interface NewComponentProps {
  title: string;
}

export const NewComponent: React.FC<NewComponentProps> = ({ title }) => {
  return (
    <div className="new-component">
      <h2>{title}</h2>
    </div>
  );
};
```

2. **Export from index**:
```typescript
// components/index.ts
export { NewComponent } from './NewComponent';
```

3. **Use in parent**:
```typescript
import { NewComponent } from '../components';

<NewComponent title="Hello" />
```

### Adding Database Migration

1. **Modify model**:
```python
class Profile(models.Model):
    # Add new field
    new_field = models.CharField(max_length=100, default="")
```

2. **Create migration**:
```bash
python manage.py makemigrations
```

3. **Review migration file**:
```python
# migrations/0002_profile_new_field.py
# Check the generated migration
```

4. **Apply migration**:
```bash
python manage.py migrate
```

5. **Update serializers/views** as needed

### Adding WebSocket Event

1. **Update consumer**:
```python
# consumers.py
async def receive(self, text_data):
    data = json.loads(text_data)
    
    if data['type'] == 'new.event':
        await self.handle_new_event(data)

async def handle_new_event(self, data):
    # Process event
    await self.channel_layer.group_send(
        self.room_group_name,
        {
            'type': 'new_event_broadcast',
            'data': data
        }
    )

async def new_event_broadcast(self, event):
    await self.send(text_data=json.dumps({
        'type': 'new.event',
        'data': event['data']
    }))
```

2. **Update frontend**:
```typescript
// services/websocket.ts
socket.on('new.event', (data) => {
  // Handle event
});

// Send event
socket.emit('new.event', { ... });
```

## Debugging Tips

### Backend Debugging

**Django Debug Toolbar**:
```python
# settings.py (development only)
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

**Print Debugging**:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"User: {user.email}")
logger.info(f"Profile created: {profile.id}")
logger.error(f"Failed to save: {e}")
```

**Django Shell**:
```bash
python manage.py shell

>>> from authentication.models import User
>>> User.objects.all()
>>> user = User.objects.first()
>>> user.email
```

**Database Queries**:
```python
from django.db import connection

# After request
print(len(connection.queries))
for query in connection.queries:
    print(query['sql'])
```

### Frontend Debugging

**React DevTools**: Install browser extension

**Console Logging**:
```typescript
console.log('State:', state);
console.error('Error:', error);
console.table(users);
```

**Network Tab**: Monitor API calls and WebSocket messages

**Redux DevTools**: For state debugging (if using Redux)

### Common Issues

**Issue**: Database connection error
**Solution**: Check Docker containers are running, verify .env settings

**Issue**: CORS errors
**Solution**: Check CORS_ALLOWED_ORIGINS in backend settings

**Issue**: WebSocket won't connect
**Solution**: Verify JWT token, check Redis is running, review WebSocket URL

**Issue**: Module not found
**Solution**: Check imports, run `pip install` or `npm install`

## Deployment Process

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for detailed instructions.

**Quick Overview**:

1. **Build Docker images**:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Run migrations**:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

3. **Collect static files**:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic
```

4. **Start services**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Internal Docs

- [API Documentation](API.md)
- [WebSocket Documentation](WEBSOCKETS.md)
- [Deployment Guide](../DEPLOYMENT_GUIDE.md)
- [Environment Variables](ENVIRONMENT.md)

### Tools

- [Postman](https://www.postman.com/) - API testing
- [wscat](https://github.com/websockets/wscat) - WebSocket testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL GUI
- [Redis Commander](https://github.com/joeferner/redis-commander) - Redis GUI

### Learning Resources

- [Django for Beginners](https://djangoforbeginners.com/)
- [React Tutorial](https://react.dev/learn)
- [WebSocket Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [JWT Introduction](https://jwt.io/introduction)

## Getting Help

1. **Check documentation** - Start here
2. **Search codebase** - Look for similar implementations
3. **Ask team** - Use Slack/Discord
4. **Create issue** - For bugs or feature requests
5. **Pair programming** - Schedule with senior dev

## Next Steps

Now that you're set up:

1. ✅ Complete the setup process
2. ✅ Explore the codebase
3. ✅ Run the test suite
4. ✅ Pick a starter task from the backlog
5. ✅ Make your first contribution!

Welcome to the team! 🎉
