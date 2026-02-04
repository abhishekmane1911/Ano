# Design Document

## Overview

Ano is a full-stack web application built with React/TypeScript frontend and Django/DRF backend, enabling anonymous communication and matchmaking for IIT Indore students. The architecture follows clean separation of concerns with a RESTful API for standard operations and WebSocket connections for real-time features. The system prioritizes anonymity through UUID-based identifiers, security through JWT authentication and rate limiting, and user experience through modern UI patterns and real-time updates.

### Key Design Principles

1. **Anonymity First**: All user-facing identifiers use UUIDs; no personal information exposed in any API response
2. **Security by Default**: JWT tokens, HTTPS, CSRF protection, input validation, and rate limiting on all endpoints
3. **Real-time Communication**: WebSocket channels for instant messaging, typing indicators, and presence updates
4. **Scalable Architecture**: Modular Django apps, PostgreSQL with proper indexing, and stateless API design
5. **Modern UX**: Responsive design, smooth animations, optimistic UI updates, and progressive loading

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   React    │  │   Zustand    │  │  Framer Motion   │   │
│  │ TypeScript │  │ State Mgmt   │  │   Animations     │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                    HTTPS / WSS
                            │
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Django Middleware (CORS, CSRF, Rate Limiting)     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│   REST API     │                    │   WebSocket     │
│   (Django DRF) │                    │   (Channels)    │
└───────┬────────┘                    └────────┬────────┘
        │                                      │
┌───────▼──────────────────────────────────────▼─────────┐
│              Application Layer (Django)                 │
│  ┌──────┐ ┌─────────┐ ┌──────┐ ┌────────────────┐    │
│  │ Auth │ │Profiles │ │ Chat │ │  Matchmaking   │    │
│  └──────┘ └─────────┘ └──────┘ └────────────────┘    │
│  ┌──────────┐ ┌────────────┐                          │
│  │ Reports  │ │   Admin    │                          │
│  └──────────┘ └────────────┘                          │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                  Data Layer (PostgreSQL)                 │
│  Users │ Profiles │ Messages │ Matches │ Reports        │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18 with TypeScript for type safety
- Tailwind CSS for utility-first styling
- Framer Motion for smooth animations
- Zustand for lightweight state management
- React Router v6 for client-side routing
- Socket.IO client for WebSocket connections
- Axios for HTTP requests with interceptors

**Backend:**
- Django 4.2 with Python 3.11+
- Django REST Framework for API endpoints
- Django Channels for WebSocket support
- djangorestframework-simplejwt for JWT authentication
- Argon2 for password hashing
- Celery for async tasks (email sending, media processing)
- Redis for WebSocket channel layer and caching

**Database:**
- PostgreSQL 15+ for relational data
- Redis for session storage and real-time data

**Infrastructure:**
- Nginx as reverse proxy
- Gunicorn/Daphne for WSGI/ASGI servers
- Docker for containerization
- Environment-based configuration

## Components and Interfaces

### Frontend Components

#### 1. Authentication Module
- **LandingPage**: Hero section explaining Ano with call-to-action
- **SignupForm**: Email validation, password strength indicator, terms acceptance
- **LoginForm**: Email/password input with "remember me" option
- **EmailVerification**: Displays verification status and resend option
- **PasswordReset**: Email-based password recovery flow

#### 2. Profile Module
- **ProfileCreation**: Multi-step form for interests, hobbies, age, relationship intent
- **ProfileEditor**: Update profile information and preferences
- **AnonymousAvatar**: Profile picture with anonymity filters applied
- **InterestSelector**: Tag-based selection for interests and hobbies

#### 3. Chat Module
- **ChatroomList**: List of available public chatrooms with unread counts
- **ChatWindow**: Message display with infinite scroll, reactions, and media
- **MessageInput**: Text input with emoji picker, media upload, voice recording
- **MessageBubble**: Individual message with sender, timestamp, read receipts
- **TypingIndicator**: Animated indicator showing who is typing
- **MediaViewer**: Full-screen image/video viewer with zoom
- **MessageReactions**: Emoji reactions display and selector
- **PinnedMessages**: Collapsible section showing pinned messages

#### 4. Matchmaking Module
- **SwipeCard**: Profile card with interests, age, and anonymous photo
- **SwipeInterface**: Tinder-style card stack with swipe gestures
- **MatchNotification**: Modal celebrating new matches
- **MatchList**: List of all current matches
- **MatchChat**: One-on-one anonymous chat with match

#### 5. Safety Module
- **ReportModal**: Form to report users with reason selection
- **BlockConfirmation**: Confirmation dialog for blocking users
- **SafetySettings**: Privacy and safety preferences

#### 6. Layout Components
- **Navigation**: Top bar with logo, navigation links, theme toggle
- **Sidebar**: Collapsible sidebar for chat/match navigation
- **ThemeToggle**: Switch between light and dark modes
- **LoadingSpinner**: Consistent loading indicator
- **ErrorBoundary**: Graceful error handling with fallback UI

### Backend API Endpoints

#### Authentication API (`/api/auth/`)
```
POST   /register/          - Register with institute email
POST   /verify-email/      - Verify email with token
POST   /login/             - Login and receive JWT tokens
POST   /refresh/           - Refresh access token
POST   /logout/            - Invalidate refresh token
POST   /password-reset/    - Request password reset
POST   /password-confirm/  - Confirm password reset
GET    /me/                - Get current user info
```

#### Profile API (`/api/profiles/`)
```
POST   /                   - Create anonymous profile
GET    /me/                - Get own profile
PUT    /me/                - Update own profile
POST   /avatar/            - Upload profile picture
GET    /{uuid}/            - Get anonymous profile by UUID
```

#### Chatroom API (`/api/chatrooms/`)
```
GET    /                   - List all chatrooms
GET    /{uuid}/            - Get chatroom details
GET    /{uuid}/messages/   - Get chatroom messages (paginated)
POST   /{uuid}/messages/   - Send message to chatroom
PUT    /messages/{uuid}/   - Edit message
DELETE /messages/{uuid}/   - Delete message
POST   /messages/{uuid}/react/ - Add reaction to message
POST   /messages/{uuid}/pin/   - Pin/unpin message
```

#### Matchmaking API (`/api/matchmaking/`)
```
GET    /profiles/          - Get profiles for swiping
POST   /swipe/             - Record swipe (left/right)
GET    /matches/           - Get all matches
GET    /matches/{uuid}/    - Get match details
GET    /matches/{uuid}/messages/ - Get match chat messages
POST   /matches/{uuid}/messages/ - Send message to match
```

#### Reports API (`/api/reports/`)
```
POST   /                   - Create report
POST   /block/             - Block user
GET    /blocked/           - Get blocked users list
DELETE /block/{uuid}/      - Unblock user
```

#### Admin API (`/api/admin/`)
```
GET    /reports/           - List all reports
PUT    /reports/{uuid}/    - Update report status
GET    /users/{uuid}/      - Get user details for moderation
POST   /users/{uuid}/ban/  - Ban user
POST   /broadcast/         - Send broadcast message
GET    /metrics/           - Platform health metrics
```

### WebSocket Channels

#### Chat Channel (`/ws/chat/{chatroom_uuid}/`)
**Events:**
- `message.send` - User sends message
- `message.receive` - Broadcast message to room
- `message.edit` - User edits message
- `message.delete` - User deletes message
- `message.react` - User reacts to message
- `typing.start` - User starts typing
- `typing.stop` - User stops typing
- `user.join` - User joins chatroom
- `user.leave` - User leaves chatroom
- `read.receipt` - User reads message

#### Match Chat Channel (`/ws/match/{match_uuid}/`)
**Events:**
- `message.send` - Send message to match
- `message.receive` - Receive message from match
- `typing.start` - Match starts typing
- `typing.stop` - Match stops typing
- `read.receipt` - Message read confirmation

## Data Models

### User Model (extends Django AbstractUser)
```python
{
  "id": "uuid",
  "email": "string (@iiti.ac.in)",
  "password": "string (hashed)",
  "is_verified": "boolean",
  "is_active": "boolean",
  "date_joined": "datetime",
  "last_login": "datetime"
}
```

### Profile Model
```python
{
  "id": "uuid",
  "user": "ForeignKey(User)",
  "anonymous_id": "uuid (public identifier)",
  "age": "integer",
  "interests": "JSONField (array of strings)",
  "hobbies": "JSONField (array of strings)",
  "relationship_intent": "string (choices: friendship, dating, casual)",
  "personality_tags": "JSONField (array of strings)",
  "avatar": "ImageField (with anonymity filter)",
  "bio": "text (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Chatroom Model
```python
{
  "id": "uuid",
  "name": "string",
  "description": "text",
  "is_active": "boolean",
  "created_by": "ForeignKey(User, null=True)",
  "created_at": "datetime",
  "member_count": "integer"
}
```

### Message Model
```python
{
  "id": "uuid",
  "chatroom": "ForeignKey(Chatroom, null=True)",
  "match": "ForeignKey(Match, null=True)",
  "sender": "ForeignKey(Profile)",
  "content": "text",
  "message_type": "string (choices: text, image, voice, system)",
  "media_url": "string (optional)",
  "is_edited": "boolean",
  "is_deleted": "boolean",
  "is_pinned": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### MessageReaction Model
```python
{
  "id": "uuid",
  "message": "ForeignKey(Message)",
  "profile": "ForeignKey(Profile)",
  "emoji": "string",
  "created_at": "datetime"
}
```

### ReadReceipt Model
```python
{
  "id": "uuid",
  "message": "ForeignKey(Message)",
  "profile": "ForeignKey(Profile)",
  "read_at": "datetime"
}
```

### Swipe Model
```python
{
  "id": "uuid",
  "swiper": "ForeignKey(Profile)",
  "swiped": "ForeignKey(Profile)",
  "direction": "string (choices: left, right)",
  "created_at": "datetime"
}
```

### Match Model
```python
{
  "id": "uuid",
  "profile1": "ForeignKey(Profile)",
  "profile2": "ForeignKey(Profile)",
  "matched_at": "datetime",
  "is_active": "boolean"
}
```

### Report Model
```python
{
  "id": "uuid",
  "reporter": "ForeignKey(Profile)",
  "reported": "ForeignKey(Profile)",
  "reason": "string (choices: harassment, spam, inappropriate, other)",
  "description": "text",
  "status": "string (choices: pending, reviewed, resolved)",
  "created_at": "datetime",
  "reviewed_by": "ForeignKey(User, null=True)",
  "reviewed_at": "datetime (null=True)"
}
```

### Block Model
```python
{
  "id": "uuid",
  "blocker": "ForeignKey(Profile)",
  "blocked": "ForeignKey(Profile)",
  "created_at": "datetime"
}
```

### Database Indexes
- User.email (unique)
- Profile.anonymous_id (unique, indexed)
- Profile.user (unique, indexed)
- Message.chatroom + created_at (composite index for pagination)
- Message.match + created_at (composite index for pagination)
- Swipe.swiper + swiped (composite unique index)
- Match.profile1 + profile2 (composite unique index)
- Block.blocker + blocked (composite unique index)


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication & Security Properties

**Property 1: Email domain validation**
*For any* email address submitted during registration, the system should accept it if and only if the domain is exactly "@iiti.ac.in"
**Validates: Requirements 1.1**

**Property 2: Verification email delivery**
*For any* valid institute email registration, the system should send a verification link to that email address
**Validates: Requirements 1.2**

**Property 3: Account activation via verification**
*For any* valid verification token, clicking the link should activate the account and enable profile creation
**Validates: Requirements 1.3**

**Property 4: Password hashing**
*For any* password submitted during registration, the stored password should be hashed and different from the plaintext input
**Validates: Requirements 1.5**

**Property 5: JWT token generation**
*For any* successful login with valid credentials, the system should generate both an access token and a refresh token
**Validates: Requirements 2.1**

**Property 6: Secure cookie storage**
*For any* generated refresh token, the system should store it in an HTTP-only cookie
**Validates: Requirements 2.2**

**Property 7: Token validation**
*For any* authenticated API request, the system should accept it if and only if the access token is valid and properly signed
**Validates: Requirements 2.3**

**Property 8: Token refresh round-trip**
*For any* expired access token with a valid refresh token, using the refresh token should produce a new valid access token
**Validates: Requirements 2.4**

**Property 9: Rate limiting on failed logins**
*For any* source making multiple failed login attempts, the system should block subsequent attempts after exceeding the threshold
**Validates: Requirements 2.5**

**Property 10: CSRF protection**
*For any* state-changing request without a valid CSRF token, the system should reject the request
**Validates: Requirements 12.2**

**Property 11: Input validation**
*For any* API endpoint receiving invalid input data, the system should reject the request with appropriate error messages
**Validates: Requirements 12.1**

**Property 12: File type validation**
*For any* file upload, the system should accept it if and only if the file type is in the allowed list
**Validates: Requirements 12.5**

### Anonymity & Privacy Properties

**Property 13: UUID assignment**
*For any* created profile, the system should assign a unique anonymous identifier in valid UUID format
**Validates: Requirements 3.1**

**Property 14: Personal information isolation**
*For any* API response containing profile or user data, the response should never include the user's institute email or real name
**Validates: Requirements 3.2, 3.4, 14.4**

**Property 15: Server-side profile validation**
*For any* profile update with invalid data (wrong types, out of range values), the system should reject the update
**Validates: Requirements 3.5**

**Property 16: Anonymous chatroom display**
*For any* user entering a chatroom, the system should display only the user's anonymous identifier, never their real name or email
**Validates: Requirements 4.1**

**Property 17: UUID format consistency**
*For any* entity created in the system (profiles, messages, matches, reports), the ID should be in valid UUID format
**Validates: Requirements 14.1**

**Property 18: Anonymous relationship storage**
*For any* relationship between users (matches, blocks, reports), the stored data should use anonymous identifiers without linking to institute emails
**Validates: Requirements 14.2**

**Property 19: Anonymous logging**
*For any* logged event, the log entry should contain only anonymous identifiers, never institute emails or real names
**Validates: Requirements 14.3**

### Chat & Messaging Properties

**Property 20: Real-time message broadcasting**
*For any* message sent to a chatroom, all connected participants should receive the message in real-time via WebSocket
**Validates: Requirements 4.2**

**Property 21: Media compression**
*For any* uploaded image or voice note, the stored file size should be smaller than the original upload
**Validates: Requirements 4.3**

**Property 22: Message mutation broadcasting**
*For any* message that is edited or deleted, all chatroom participants should receive the update in real-time
**Validates: Requirements 4.4**

**Property 23: Message pinning**
*For any* message that is pinned, the message's is_pinned flag should be set to true and the message should appear in the pinned messages list
**Validates: Requirements 4.5**

**Property 24: Typing indicator broadcasting**
*For any* user typing in a chat, other participants should receive a typing indicator via WebSocket
**Validates: Requirements 5.1**

**Property 25: Read receipt creation**
*For any* message marked as read by a user, a read receipt should be created and sent to the message sender
**Validates: Requirements 5.2, 8.5**

**Property 26: Anonymous presence updates**
*For any* user coming online, other participants should receive a status update containing only the user's anonymous identifier
**Validates: Requirements 5.3**

**Property 27: Reaction storage and broadcasting**
*For any* reaction added to a message, the reaction should be stored and broadcast to all chatroom participants
**Validates: Requirements 5.4**

**Property 28: Paginated message loading**
*For any* chatroom with more messages than the page size, loading messages should return them in batches ordered by creation time
**Validates: Requirements 5.5**

**Property 29: Admin broadcast designation**
*For any* broadcast message sent by an administrator, the message should be marked with admin designation
**Validates: Requirements 6.1**

**Property 30: Report escalation**
*For any* user receiving multiple reports exceeding the threshold, the system should notify administrators
**Validates: Requirements 6.3, 9.5**

**Property 31: Match chat message delivery**
*For any* message sent in a matched chat, the other user should receive the message in real-time via WebSocket
**Validates: Requirements 8.2**

**Property 32: Match chat typing indicator**
*For any* user typing in a matched chat, the other user should receive a typing indicator
**Validates: Requirements 8.4**

### Matchmaking Properties

**Property 33: Profile card completeness**
*For any* profile displayed in the matchmaking interface, the profile card should include interests, hobbies, age, relationship intent, and personality tags
**Validates: Requirements 7.1**

**Property 34: Swipe left recording**
*For any* profile swiped left, the system should create a swipe record with direction='left'
**Validates: Requirements 7.2**

**Property 35: Swipe right recording**
*For any* profile swiped right, the system should create a swipe record with direction='right' and check for mutual match
**Validates: Requirements 7.3**

**Property 36: Mutual match creation**
*For any* two users who both swipe right on each other, the system should create a match record
**Validates: Requirements 7.4**

**Property 37: Profile exclusion after swipe**
*For any* profile that a user has swiped on, that profile should not appear in subsequent profile fetches for that user
**Validates: Requirements 7.5**

**Property 38: Match chat initialization**
*For any* newly created match, an anonymous chat channel should be available for both users
**Validates: Requirements 8.1**

### Safety & Moderation Properties

**Property 39: Anonymous report creation**
*For any* report submitted, the report record should contain the reporter's anonymous identifier and the reported user's anonymous identifier, never their emails
**Validates: Requirements 9.1**

**Property 40: Block communication prevention**
*For any* two users where one has blocked the other, all message attempts between them should be rejected
**Validates: Requirements 9.2**

**Property 41: Anonymous admin notifications**
*For any* report submitted, administrator notifications should contain only anonymous identifiers
**Validates: Requirements 9.3**

**Property 42: Blocked profile filtering**
*For any* user who has been blocked, their profile should not appear in the blocker's matchmaking results
**Validates: Requirements 9.4**

### Search & UI Properties

**Property 43: Search scope limitation**
*For any* search query, results should only include messages from chats the user has access to
**Validates: Requirements 10.1, 10.4**

**Property 44: Search result highlighting**
*For any* search query with results, the matching text should be highlighted in the message preview
**Validates: Requirements 10.2**

**Property 45: Theme persistence round-trip**
*For any* theme selection (light or dark), saving and reloading the application should restore the same theme
**Validates: Requirements 11.2, 11.3**

**Property 46: Mobile media optimization**
*For any* media request from a mobile device, the system should serve compressed or resized media
**Validates: Requirements 13.4**

### Admin Properties

**Property 47: Anonymous admin dashboard**
*For any* pending report displayed in the admin dashboard, only anonymous user identifiers should be shown
**Validates: Requirements 15.1, 15.2**

**Property 48: Report action recording**
*For any* administrative action taken on a report, the system should record the action and update the report status
**Validates: Requirements 15.3**

**Property 49: Platform metrics calculation**
*For any* admin dashboard load, the system should display accurate metrics for active users and message volume
**Validates: Requirements 15.4**

## Error Handling

### Frontend Error Handling

1. **Network Errors**: Display user-friendly messages for connection failures with retry options
2. **Authentication Errors**: Redirect to login on 401, attempt token refresh on 403
3. **Validation Errors**: Display field-specific error messages from API responses
4. **WebSocket Disconnections**: Automatically attempt reconnection with exponential backoff
5. **Media Upload Failures**: Show progress and allow retry for failed uploads
6. **Form Validation**: Client-side validation before submission to reduce server load

### Backend Error Handling

1. **Invalid Input**: Return 400 with detailed validation errors in consistent format
2. **Authentication Failures**: Return 401 for invalid tokens, 403 for insufficient permissions
3. **Resource Not Found**: Return 404 with helpful error messages
4. **Rate Limiting**: Return 429 with retry-after header
5. **Server Errors**: Log full stack trace, return 500 with generic message to client
6. **Database Errors**: Wrap in transactions, rollback on failure, log for debugging
7. **WebSocket Errors**: Send error events to client, maintain connection when possible
8. **Media Processing Errors**: Queue for retry, notify user if persistent failure

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Email domain must be @iiti.ac.in"],
      "age": ["Age must be between 18 and 100"]
    }
  }
}
```

## Testing Strategy

### Unit Testing

The application will use comprehensive unit testing to verify specific behaviors and edge cases:

**Frontend Unit Tests (Jest + React Testing Library):**
- Component rendering with various props
- User interaction handlers (clicks, form submissions)
- State management logic (Zustand stores)
- Utility functions (validation, formatting)
- API client methods with mocked responses
- WebSocket event handlers

**Backend Unit Tests (pytest + Django TestCase):**
- Model validation and constraints
- Serializer validation and transformation
- View permission checks
- Business logic in service layer
- Utility functions (email validation, UUID generation)
- Middleware behavior (rate limiting, CSRF)

**Key Unit Test Areas:**
- Email domain validation with various invalid domains
- Password hashing verification
- Token generation and validation
- Profile creation with missing/invalid fields
- Message sending with various content types
- Swipe recording and match detection
- Block and report creation
- Search query parsing and filtering
- Theme persistence in local storage

### Property-Based Testing

The application will use property-based testing to verify universal properties across all inputs. We will use **Hypothesis** for Python backend testing and **fast-check** for TypeScript frontend testing.

**Configuration:**
- Each property-based test will run a minimum of 100 iterations
- Tests will use smart generators that constrain to valid input spaces
- Each test will be tagged with a comment referencing the correctness property from this design document

**Tag Format:**
```python
# Feature: ano-platform, Property 1: Email domain validation
```

**Backend Property Tests (Hypothesis):**
- Generate random email addresses and verify domain validation (Property 1)
- Generate random passwords and verify hashing (Property 4)
- Generate random profile data and verify UUID assignment (Property 13)
- Generate random messages and verify anonymity in responses (Property 14)
- Generate random swipes and verify match creation logic (Property 36)
- Generate random reports and verify anonymous storage (Property 39)
- Generate random API requests and verify input validation (Property 11)

**Frontend Property Tests (fast-check):**
- Generate random theme selections and verify persistence (Property 45)
- Generate random form inputs and verify validation (Property 11)
- Generate random search queries and verify result filtering (Property 43)

**Property Test Strategy:**
1. Write smart generators that produce valid test data within constraints
2. Test core business logic without mocking when possible
3. Use property tests to catch edge cases that unit tests might miss
4. Combine with unit tests for comprehensive coverage
5. Focus on invariants that must hold across all inputs

### Integration Testing

**API Integration Tests:**
- Full authentication flow (register → verify → login → refresh)
- Chatroom message flow (join → send → receive → react)
- Matchmaking flow (swipe → match → chat)
- Report and block flow (report → admin review → action)

**WebSocket Integration Tests:**
- Connect → authenticate → send → receive → disconnect
- Multiple clients in same chatroom
- Typing indicators and presence updates
- Reconnection after disconnect

### End-to-End Testing

**Critical User Flows (Playwright/Cypress):**
- New user registration and email verification
- Login and token refresh
- Create profile and enter chatroom
- Send messages and media in chatroom
- Swipe on profiles and create match
- Chat with match
- Report and block user
- Admin review reports

### Test Coverage Goals

- Unit test coverage: >80% for critical paths
- Property-based tests for all core business logic
- Integration tests for all API endpoints
- E2E tests for critical user journeys
- WebSocket tests for all real-time features

## Security Considerations

### Authentication Security

1. **Password Storage**: Argon2 hashing with salt
2. **JWT Tokens**: Short-lived access tokens (15 min), longer refresh tokens (7 days)
3. **Token Storage**: Access tokens in memory, refresh tokens in HTTP-only cookies
4. **Token Rotation**: Refresh tokens rotated on each use
5. **Session Management**: Logout invalidates refresh token

### API Security

1. **Rate Limiting**: Per-IP and per-user limits on all endpoints
2. **CSRF Protection**: CSRF tokens for all state-changing requests
3. **Input Validation**: Server-side validation on all inputs
4. **SQL Injection Prevention**: Django ORM parameterized queries
5. **XSS Prevention**: Content Security Policy headers, output escaping
6. **CORS**: Whitelist allowed origins

### Data Security

1. **Anonymity**: UUID-based identifiers, no PII in public APIs
2. **Access Control**: Users can only access their own data and public chatrooms
3. **Data Encryption**: HTTPS for transmission, encrypted database fields for sensitive data
4. **File Upload Security**: File type validation, size limits, virus scanning
5. **Media Anonymization**: Automatic filters on profile pictures

### WebSocket Security

1. **Authentication**: JWT token required for WebSocket connection
2. **Authorization**: Verify user has access to chatroom/match before allowing messages
3. **Rate Limiting**: Message rate limits per user
4. **Input Validation**: Validate all WebSocket message payloads

## Performance Considerations

### Database Optimization

1. **Indexing**: Composite indexes on frequently queried fields
2. **Query Optimization**: Select only needed fields, use prefetch_related for relationships
3. **Connection Pooling**: PostgreSQL connection pool for efficient connections
4. **Caching**: Redis cache for frequently accessed data (chatroom lists, user profiles)

### Frontend Performance

1. **Code Splitting**: Lazy load routes and heavy components
2. **Image Optimization**: Compress and resize images, lazy load off-screen images
3. **Virtual Scrolling**: Virtualize long message lists for smooth scrolling
4. **Debouncing**: Debounce search and typing indicators
5. **Optimistic Updates**: Update UI immediately, sync with server in background

### WebSocket Performance

1. **Connection Management**: Single WebSocket connection per user, multiplex channels
2. **Message Batching**: Batch typing indicators and presence updates
3. **Compression**: Enable WebSocket compression for large payloads
4. **Heartbeat**: Periodic ping/pong to detect dead connections

### Scalability

1. **Stateless API**: Enable horizontal scaling of API servers
2. **Redis Channel Layer**: Distributed WebSocket message routing
3. **Media Storage**: Use object storage (S3) for uploaded media
4. **Database Replication**: Read replicas for scaling read operations
5. **CDN**: Serve static assets from CDN

## Deployment Architecture

### Development Environment

```
- Frontend: React dev server (port 3000)
- Backend: Django runserver (port 8000)
- Database: PostgreSQL (port 5432)
- Redis: Redis server (port 6379)
- WebSocket: Daphne ASGI server (port 8001)
```

### Production Environment

```
┌─────────────┐
│   Nginx     │ (Reverse Proxy, SSL Termination)
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────┐
│React│  │Django│
│Build│  │ API  │
└─────┘  └──┬───┘
            │
    ┌───────┼───────┐
    │       │       │
┌───▼──┐ ┌──▼───┐ ┌▼────┐
│Gunic.│ │Daphne│ │Redis│
│(WSGI)│ │(ASGI)│ │     │
└──────┘ └──────┘ └─────┘
            │
        ┌───▼────┐
        │Postgres│
        └────────┘
```

### Environment Variables

**Frontend (.env):**
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8001/ws
REACT_APP_ENV=development
```

**Backend (.env):**
```
DEBUG=False
SECRET_KEY=<random-secret-key>
DATABASE_URL=postgresql://user:pass@localhost:5432/ano
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080
RATE_LIMIT_PER_MINUTE=60
```

## Development Workflow

### Project Structure

```
ano-platform/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── types/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── backend/
│   ├── ano/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── auth/
│   │   ├── profiles/
│   │   ├── chat/
│   │   ├── matchmaking/
│   │   ├── reports/
│   │   └── admin_dashboard/
│   ├── requirements.txt
│   └── manage.py
├── docker-compose.yml
└── README.md
```

### Git Workflow

1. Feature branches from `main`
2. Pull requests with code review
3. CI/CD pipeline runs tests
4. Merge to `main` after approval
5. Automatic deployment to staging
6. Manual promotion to production

### Code Quality

1. **Linting**: ESLint for TypeScript, Flake8 for Python
2. **Formatting**: Prettier for TypeScript, Black for Python
3. **Type Checking**: TypeScript strict mode, mypy for Python
4. **Pre-commit Hooks**: Run linting and formatting before commit
5. **Code Review**: Required for all pull requests
