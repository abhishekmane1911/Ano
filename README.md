# Ano — Anonymous Chat Platform for IIT Indore

An anonymous chatting platform exclusively for IIT Indore students (`@iiti.ac.in` email required). Ano lets students communicate in real-time public chatrooms while staying completely anonymous through UUID-based identifiers, with an advanced reputation/gamification system, AI-powered content moderation, and multi-layered spam protection.

> **Note:** Matchmaking is currently disabled in the UI while the matching algorithm is being improved. The backend code for matchmaking exists but the frontend routes are commented out.

##  Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Tech Stack](#️-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Development Setup](#-development-setup)
- [Environment Variables](#-environment-variables)
- [Running Tests](#-running-tests)
- [API Reference](#-api-reference)
- [WebSocket Events](#-websocket-events)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

##  Features

### Core Features
- **Anonymous Authentication** — IIT Indore email (`@iiti.ac.in`) verification with email OTP; UUID-based user IDs throughout
- **Anonymous Profiles** — UUID `anonymous_id` as the only public identifier; stores age, interests, hobbies, personality tags, relationship intent, bio, and avatar
- **Public Chatrooms** — Real-time group chat via Django Channels WebSockets with typing indicators, read receipts, message reactions (emoji), edit/delete, and pinned messages
- **Message Search** — Full-text PostgreSQL search across chatroom message history
- **Match Chat** — Private one-on-one messaging between matched users (backend complete; frontend temporarily disabled)
- **Matchmaking** — Tinder-style swipe interface for anonymous connections (backend complete; frontend disabled pending algorithm improvements)
- **Password Reset** — Secure token-based password reset via email (1-hour expiry)
- **Dark/Light Mode** — Full theme toggle with system-aware default
- **Polls** — Campus Legend–tier users can create polls in chatrooms
- **Confessions** — Campus Legend–tier users can submit moderated anonymous confessions

### Reputation & Gamification System
- **Rank Tiers**: Fresher → Sophomore (100 XP) → Senior (500 XP) → Campus Legend (1000 XP)
- **Logarithmic level progression**: Level N requires `100 × 1.5ⁿ` XP
- **Wilson Score** ranking for messages (statistically sound upvote/downvote ranking)
- **Reputation points** awarded for upvotes (+5), deducted for downvotes (-2) and validated reports (-50)
- **Real-time reputation updates** via WebSocket notifications

### AI Content Moderation
- **OpenAI Moderation API** — Primary moderation with circuit-breaker protection (opens after 3 failures, recovers in 5 minutes)
- **Local fallback moderation** — `better-profanity` + `vaderSentiment` for offline/fallback scenarios
- **Heat System** — Escalating penalty multipliers for repeat offenders (Clean → Warm → Hot → Burning → Scorching → Inferno)
- **Shadowbanning** — Automatic temporary restrictions (24h base, escalated by heat level, capped at 168h)
- **Rehabilitation** — Heat level reduces after 14 days of clean behavior
- **Real-time moderation notifications** via WebSocket

### Anti-Spam Protection (Multi-layered)
- **Rate limiting**: 15 messages / 10s window; 30 typing events / 10s
- **Burst detection**: 7 messages in 3s (higher threshold for short messages)
- **Duplicate detection**: Blocks 3+ identical messages in 60s (smart exemptions for "ok", "yes", etc.)
- **Similarity detection**: Levenshtein distance > 92% similarity across last 5 messages (skips short messages and conversational patterns)
- **Pattern detection**: Catches excessive caps (>80%), character repetition (7+ same chars), spam keywords, URL spam (3+ URLs)
- **Escalating penalties**: Warning → Temp mute (3 min) → Shadowban

### Security Features
- Argon2 password hashing (primary), PBKDF2 fallback
- JWT authentication with rotating refresh tokens + token blacklisting
- Refresh tokens stored in HTTP-only cookies
- CSRF protection with trusted origin validation
- Custom security middleware: HTTPS redirect, security headers, anonymous logging
- Identity hashing for logs (no personal data in log output)
- Rate limiting per endpoint (5 logins/5 min, 1000 API req/hour, etc.)
- File upload validation with `python-magic` (MIME type checking, 10 MB limit)
- XSS, clickjacking, content-type sniffing protection headers
- HSTS with subdomains + preload in production

### Admin & Monitoring
- **Django Admin** panel with custom admin apps
- **Admin Dashboard** (frontend) — platform metrics, report management, user moderation panel, broadcast messages
- **Health check endpoints** — `/api/health/` (DB ping) and `/api/monitoring/` (Celery, Redis, DB, task queues)
- **Performance monitoring** — execution time and success rate tracking for all Celery tasks
- **Circuit breakers** for OpenAI API and email service

---

##  Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Client (React 19 + TypeScript)                   │
│  Zustand State  |  Framer Motion  |  Tailwind CSS v4         │
│  React Router v7  |  Axios  |  Lucide React                  │
└──────────────────────────────────────────────────────────────┘
                            │
                   HTTPS / WebSocket (WSS)
                            │
┌──────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                       │
│         CORS  |  Rate Limiting  |  SSL Termination           │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│   REST API     │                    │   WebSocket     │
│  (Django DRF)  │                    │  (Channels 4)   │
└───────┬────────┘                    └────────┬────────┘
        │                                      │
┌───────▼──────────────────────────────────────▼──────────┐
│                Django 5.2 Application Layer             │
│  Auth | Profiles | Chat | Reports | Reputation          │
│ Moderation | Security | Admin Dashboard                  │
└──────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│   PostgreSQL   │                    │     Redis       │
│  (Primary DB   │                    │  Cache | Celery │
│  + Full-text   │                    │  Broker | WS    │
│    search)     │                    │  Channel Layer  │
└────────────────┘                    └─────────────────┘
                            │
              ┌─────────────┴──────────────┐
              │      Celery Workers        │
              │  (Async emails, moderation,│
              │   reputation, security)    │
              └────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| **React** | 19.2 | UI framework |
| **TypeScript** | 5.9 | Type safety |
| **Vite** | 7.2 | Build tool & dev server |
| **Tailwind CSS** | 4.1 | Utility-first styling |
| **Zustand** | 5.0 | State management |
| **React Router** | 7.9 | Client-side routing |
| **Framer Motion** | 12.x | Animations & page transitions |
| **Axios** | 1.13 | HTTP client |
| **Lucide React** | 0.555 | Icons |
| **emoji-picker-react** | 4.16 | Emoji picker for chat |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **Django** | 5.2.8 | Web framework |
| **Django REST Framework** | 3.16 | REST API |
| **Django Channels** | 4.3 | WebSocket (ASGI) |
| **channels-redis** | 4.3 | Redis channel layer |
| **Daphne** | 4.2 | ASGI server |
| **PostgreSQL** | 15+ | Primary database + full-text search |
| **Redis** | 7+ | Cache, Celery broker, channel layer |
| **Celery** | 5.6 | Async task queue |
| **djangorestframework-simplejwt** | 5.5 | JWT auth + token blacklist |
| **argon2-cffi** | 25.1 | Password hashing |
| **Pillow** | 12.0 | Image processing (avatars) |
| **python-magic** | 0.4.27 | File type validation |
| **openai** | 1.58 | AI content moderation |
| **better-profanity** | 0.7 | Local profanity filter |
| **vaderSentiment** | 3.3 | Sentiment analysis |
| **Gunicorn** | — | WSGI server (production) |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker** | Containerization |
| **Docker Compose** | Multi-service orchestration |
| **Nginx** | Reverse proxy + SSL |
| **GitHub** | Source control |

---

##  Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose (for PostgreSQL and Redis)
- **Git**

---

##  Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd Ano

# Start PostgreSQL and Redis via Docker for dev 
docker-compose up -d

# --- Backend ---
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env            # Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
daphne -b 127.0.0.1 -p 8000 ano_backend.asgi:application

# --- Frontend (new terminal) ---
cd frontend
npm install
cp .env.example .env            # Edit .env with your API URL
npm run dev

# --- Celery worker (new terminal, for async emails & tasks) ---
cd backend
source venv/bin/activate
celery -A ano_backend worker -l info
```

Access the app:
| Service | URL |
|---|---|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **Django Admin** | http://localhost:8000/admin |
| **Health Check** | http://localhost:8000/api/health/ |
| **System Monitoring** | http://localhost:8000/api/monitoring/ |

---

##  Development Setup

### Backend (Detailed)

```bash
cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements-dev.txt

cp .env.example .env

python manage.py migrate
python manage.py createsuperuser

python manage.py shell < load_legal_docs.py

daphne -b 127.0.0.1 -p 8000 ano_backend.asgi:application
```

**Useful backend commands:**
```bash
pytest                               
pytest --cov=. --cov-report=html    # Coverage report
pytest -v authentication/tests.py   # Test specific app
black .                            
flake8                              # Lint code
python manage.py makemigrations     # Create migrations
python manage.py migrate            # Apply migrations
celery -A ano_backend worker -l info            # Start Celery worker
celery -A ano_backend beat -l info              # Start Celery beat (scheduled tasks)
python manage.py cleanup_test_data 
```

### Frontend (Detailed)

```bash
cd frontend
npm install

cp .env.example .env

npm run dev             
npm run build           
npm run build:prod     
npm run preview        
```

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

```bash
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

# JWT 
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080   # 7 days

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Frontend URL (used in email links)
FRONTEND_URL=http://localhost:5173

# AI Moderation (optional — falls back to local if not set)
OPENAI_API_KEY=sk-...

# Moderation settings
MODERATION_ENABLED=True
MODERATION_TOXICITY_THRESHOLD=0.85
MODERATION_BLOCK_VIOLENCE=True
MODERATION_BLOCK_SELF_HARM=True
MODERATION_BLOCK_HARASSMENT=False
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_ENV=development
```

---

##  Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

pytest                                              # All tests
pytest -v                                           # Verbose
pytest -x                                           # Stop on first failure
pytest --cov=. --cov-report=html                   # With coverage
pytest authentication/tests.py                      # Specific app
pytest test_spam_detection.py                       # Spam detection tests
pytest test_moderation.py                           # Moderation tests
pytest test_password_reset.py                       # Password reset tests
pytest chat/test_websocket.py                       # WebSocket tests
```

Test files present:
- `authentication/tests.py` — registration, login, email verification, password reset
- `chat/tests.py` and `chat/test_websocket.py` — chatrooms, messages, WebSocket
- `matchmaking/tests.py` and `matchmaking/test_websocket.py` — swipes, matches, notifications
- `reports/tests.py` — reporting, blocking
- `reputation/tests.py` — Wilson Score, reputation points, tiers
- `security/tests.py` — rate limiting, authentication security
- `test_spam_detection.py` — anti-spam detection
- `test_moderation.py` — AI moderation pipeline
- `test_password_reset.py` — password reset flow (with `test_settings.py` for email overrides)

---

##  API Reference

### Authentication (`/api/auth/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/register/` | Register with `@iiti.ac.in` email |
| POST | `/verify-email/` | Verify email with token |
| POST | `/login/` | Login → JWT tokens + HTTP-only cookie |
| POST | `/logout/` | Blacklist refresh token + clear cookie |
| POST | `/refresh/` | Rotate access & refresh tokens |
| GET | `/me/` | Get current user info |
| POST | `/password-reset/` | Request password reset email |
| POST | `/password-reset-confirm/` | Confirm reset with token + new password |

### Profiles (`/api/profiles/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Create anonymous profile |
| GET | `/me/` | Get own profile |
| PUT | `/me/` | Update own profile |
| GET | `/{uuid}/` | Get profile by anonymous UUID |

### Chat (`/api/chat/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/chatrooms/` | List all active chatrooms |
| GET | `/chatrooms/{uuid}/messages/` | Paginated message history |
| POST | `/chatrooms/{uuid}/messages/` | Post a message |
| PATCH | `/messages/{uuid}/` | Edit own message |
| DELETE | `/messages/{uuid}/` | Delete own message |
| POST | `/messages/{uuid}/pin/` | Pin message (admin) |
| GET | `/chatrooms/{uuid}/search/` | Full-text search messages |
| POST | `/chatrooms/{uuid}/polls/` | Create poll (Campus Legend) |
| POST | `/polls/{uuid}/vote/` | Vote on poll |

### Reports & Safety (`/api/reports/`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Report a user |
| POST | `/block/` | Block a user |
| GET | `/blocked/` | List blocked users |
| DELETE | `/block/{uuid}/` | Unblock a user |

### Reputation (`/api/reputation/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/me/` | Own reputation score, tier, level |
| GET | `/leaderboard/` | Top users by reputation |
| POST | `/messages/{uuid}/vote/` | Upvote/downvote a message |
| GET | `/heat/` | Own heat level info |

### Moderation (`/api/moderation/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/status/` | Own moderation status & shadowban info |
| POST | `/rehabilitate/` | Attempt heat level reduction |
| GET | `/admin/queue/` | Moderation queue (admin) |
| POST | `/admin/{id}/action/` | Take moderation action (admin) |

### Admin (`/api/admin/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/metrics/` | Platform-wide metrics |
| GET | `/reports/` | All user reports |
| POST | `/reports/{id}/resolve/` | Resolve a report |
| POST | `/users/{uuid}/moderate/` | Mute/ban/warn a user |
| POST | `/broadcast/` | Broadcast message to chatroom |

### Health & Monitoring (`/api/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/` | Quick DB health check |
| GET | `/monitoring/health/` | Full system health (Celery, Redis, DB) |
| GET | `/monitoring/metrics/` | Task performance metrics |

---

##  WebSocket Events

### Chatroom WebSocket — `ws://localhost:8000/ws/chat/{chatroom_uuid}/`

**Client → Server:**
| Event | Description |
|---|---|
| `message.send` | Send a text/image message |
| `message.edit` | Edit own message |
| `message.delete` | Delete own message |
| `message.react` | Add/remove emoji reaction |
| `message.upvote` | Upvote a message |
| `message.downvote` | Downvote a message |
| `typing.start` | Start typing indicator |
| `typing.stop` | Stop typing indicator |

**Server → Client:**
| Event | Description |
|---|---|
| `message.receive` | New message (or shadowbanned ghost delivery) |
| `message.updated` | Message edited |
| `message.deleted` | Message deleted |
| `message.reaction` | Reaction added/removed |
| `message.vote_update` | Updated Wilson Score |
| `typing.indicator` | Someone is typing |
| `user.joined` | User joined chatroom |
| `user.left` | User left chatroom |
| `moderation.notification` | Shadowban/rejection notice |


---

## 📁 Project Structure

```
Ano/
├── backend/                         # Django backend (Python 3.11+)
│   ├── ano_backend/                 # Main Django project config
│   │   ├── settings.py              # All settings (env-driven)
│   │   ├── urls.py                  # Root URL routing
│   │   ├── asgi.py                  # ASGI entry point (Channels)
│   │   ├── wsgi.py                  # WSGI entry point (Gunicorn)
│   │   ├── celery.py                # Celery app configuration
│   │   ├── celery_config.py         # Celery task beat schedule
│   │   ├── middleware.py            # HTTPS redirect, security headers, anonymous logging
│   │   ├── monitoring.py            # PerformanceMonitor, CircuitBreaker, HealthChecker
│   │   ├── monitoring_tasks.py      # Scheduled monitoring Celery tasks
│   │   ├── logging_config.py        # Privacy-safe logging (no PII)
│   │   ├── validators.py            # Shared input validators
│   │   ├── file_validators.py       # MIME type + size file validators
│   │   ├── file_utils.py            # Media file utilities
│   │   └── health_urls.py           # /api/monitoring/ endpoints
│   ├── authentication/              # User auth app
│   │   ├── models.py                # Custom User (UUID PK, @iiti.ac.in validation)
│   │   ├── views.py                 # Register, login, logout, refresh, me, password reset
│   │   ├── serializers.py           # Request/response serializers
│   │   ├── tasks.py                 # Celery: send_verification_email, send_password_reset_email
│   │   ├── models_legal.py          # Terms/privacy acceptance models
│   │   └── views_legal.py           # Legal document endpoints
│   ├── profiles/                    # Anonymous profile app
│   │   └── models.py                # Profile (anonymous_id UUID, age, interests, hobbies, etc.)
│   ├── chat/                        # Chat & messaging app
│   │   ├── models.py                # Chatroom, Message, MessageReaction, ReadReceipt, Poll, Confession
│   │   ├── consumers.py             # ChatConsumer WebSocket handler (27KB)
│   │   ├── anti_spam.py             # AntiSpamSystem + SpamDetectionMiddleware
│   │   ├── routing.py               # WebSocket URL routing
│   │   └── views.py                 # REST endpoints for chatrooms/messages
│   ├── reports/                     # Reports & blocking app
│   │   └── models.py                # Report, Block models
│   ├── reputation/                  # Gamification app
│   │   ├── models.py                # UserReputation, MessageRanking (Wilson Score), Vote
│   │   ├── services.py              # ReputationService (points, tiers, leaderboard)
│   │   ├── tasks.py                 # Celery: tier updates, Wilson Score recalc, batch operations
│   │   ├── websocket_utils.py       # RealtimeNotifier for reputation WebSocket events
│   │   └── signals.py               # Auto-create UserReputation on user create
│   ├── moderation/                  # AI moderation app
│   │   ├── models.py                # ModerationResult, ViolationHistory, Shadowban
│   │   ├── services.py              # HeatSystem, OpenAIModerator, LocalModerator, ModerationService
│   │   ├── tasks.py                 # Celery: async moderation, heat score updates
│   │   └── middleware.py            # Request-level moderation middleware
│   ├── security/                    # Security app
│   │   ├── models.py                # SecurityEvent, RateLimit, IdentityHash
│   │   ├── authentication.py        # EnhancedAuthenticationService
│   │   ├── middleware.py            # Rate limiting middleware (12KB)
│   │   ├── tasks.py                 # Celery: security event analysis, email anonymization
│   │   └── services.py              # Identity hashing, threat analysis
│   ├── admin_dashboard/             # Admin tools app
│   │   └── views.py                 # Platform metrics, user moderation, broadcast
│   ├── manage.py
│   ├── requirements.txt             # Production dependencies
│   ├── requirements-dev.txt         # + pytest, black, flake8, hypothesis
│   └── Dockerfile
├── frontend/                        # React frontend (Node 18+)
│   ├── src/
│   │   ├── App.tsx                  # Router, route guards (ProtectedRoute, AdminRoute, PublicRoute)
│   │   ├── components/
│   │   │   ├── auth/                # LandingPage, LoginForm, SignupForm, EmailVerification,
│   │   │   │                        #   PasswordResetRequest, PasswordResetConfirm
│   │   │   ├── profile/             # ProfileCreation, ProfileEditor
│   │   │   ├── chat/                # ChatPage, ChatWindow, ChatroomList, MessageBubble,
│   │   │   │                        #   MessageInput, MessageReactions, SearchModal, SearchResults
│   │   │   ├── matchmaking/         # (code exists, routes disabled)
│   │   │   ├── safety/              # SafetySettings (report/block UI)
│   │   │   ├── admin/               # AdminDashboard, PlatformMetrics, ReportsList,
│   │   │   │                        #   ReportDetail, UserModerationPanel, BroadcastMessageForm
│   │   │   ├── reputation/          # ReputationComponents, ReputationDemo
│   │   │   ├── common/              # Navigation, ToastContainer, PageTransition
│   │   │   └── ui/                  # Shared UI primitives
│   │   ├── api/                     # Axios API clients (auth, chat, matchmaking, profile, reports, admin)
│   │   ├── stores/                  # Zustand stores (authStore, chatStore, matchmakingStore, profileStore)
│   │   ├── services/                # websocket.ts — WebSocket client service
│   │   ├── hooks/                   # useToast and other custom hooks
│   │   ├── contexts/                # React contexts
│   │   ├── styles/                  # Global CSS
│   │   ├── App.css                  # App-level styles
│   │   ├── index.css                # Tailwind base + global tokens
│   │   └── main.tsx                 # Entry point
│   ├── index.html
│   ├── package.json                 # Node dependencies
│   ├── vite.config.ts               # Vite config
│   ├── tailwind.config.js           # Tailwind v4 config
│   ├── tsconfig.app.json
│   ├── eslint.config.js
│   ├── nginx.conf                   # Nginx config (HTTP)
│   ├── nginx-ssl.conf               # Nginx config (HTTPS)
│   └── Dockerfile / Dockerfile.prod
├── docker-compose.yml               # Dev services (PostgreSQL 15 + Redis 7)
├── docker-compose.prod.yml          # Full production stack all services containerized
├── deploy.sh                        # Production deployment script
├── start-dev.sh                     # Local development start script
├── monitor.sh                       # Production monitoring script
├── test_e2e.sh                      # End-to-end test script
├── init-db.sql                      # Initial database setup SQL
├── COMMUNITY_GUIDELINES.md
├── PRIVACY_POLICY.md
├── TERMS_OF_SERVICE.md
├── LICENSE                          # MIT License
└── README.md                        # This file
```

---

##  Deployment

### Quick Production Deployment

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Monitor services
./monitor.sh
```

---


##  Security Notes

- All user identifiers exposed in any API response are UUIDs (never email addresses or real names)
- Logs use anonymous IDs only — no PII is ever written to log files
- JWT refresh tokens are stored in HTTP-only cookies (not accessible to JavaScript)
- Rate limiting is enforced at the middleware layer on all endpoints
- File uploads are validated for MIME type (not just extension) using `python-magic`
- Report security vulnerabilities by opening a private GitHub issue

---

##  Roadmap

- [ ] Re-enable matchmaking with improved algorithm
- [ ] Voice messages in chat
- [ ] Mobile app (React Native)
- [ ] Advanced matching algorithms (interest-based, behavior-based)
- [ ] Multi-language support

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
