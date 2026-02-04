# API Documentation

Complete REST API reference for the Ano platform.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

All authenticated endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- **Access Token**: Valid for 15 minutes
- **Refresh Token**: Valid for 7 days, stored in HTTP-only cookie
- **Token Refresh**: Use `/api/auth/refresh/` before access token expires

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Success message"
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field_name": ["Error description"]
    }
  }
}
```

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute per IP
- **API endpoints**: 100 requests per minute per user
- **WebSocket connections**: 10 connections per user

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

## Authentication Endpoints

### Register User

Create a new user account with IIT Indore email.

**Endpoint**: `POST /api/auth/register/`

**Authentication**: None

**Request Body**:
```json
{
  "email": "student@iiti.ac.in",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!"
}
```

**Validation Rules**:
- Email must end with `@iiti.ac.in`
- Password minimum 8 characters
- Password must contain uppercase, lowercase, number, and special character

**Success Response** (201 Created):
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "user": {
    "id": "uuid",
    "email": "student@iiti.ac.in",
    "is_verified": false
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email domain or weak password
- `409 Conflict`: Email already registered

---

### Verify Email

Verify email address using token sent to email.

**Endpoint**: `POST /api/auth/verify-email/`

**Authentication**: None

**Request Body**:
```json
{
  "token": "verification-token-from-email"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Email verified successfully. You can now log in."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token

---

### Login

Authenticate user and receive JWT tokens.

**Endpoint**: `POST /api/auth/login/`

**Authentication**: None

**Request Body**:
```json
{
  "email": "student@iiti.ac.in",
  "password": "SecurePassword123!"
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "student@iiti.ac.in",
    "is_verified": true
  }
}
```

**Notes**:
- Refresh token is also set in HTTP-only cookie
- Access token should be stored in memory (not localStorage)

**Error Responses**:
- `400 Bad Request`: Missing credentials
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Email not verified
- `429 Too Many Requests`: Rate limit exceeded

---

### Refresh Token

Get a new access token using refresh token.

**Endpoint**: `POST /api/auth/refresh/`

**Authentication**: Refresh token (from cookie or body)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

---

### Logout

Invalidate refresh token and logout user.

**Endpoint**: `POST /api/auth/logout/`

**Authentication**: Required

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (200 OK):
```json
{
  "message": "Logout successful"
}
```

---

### Request Password Reset

Request password reset email.

**Endpoint**: `POST /api/auth/password-reset/`

**Authentication**: None

**Request Body**:
```json
{
  "email": "student@iiti.ac.in"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Password reset email sent"
}
```

---

### Confirm Password Reset

Reset password using token from email.

**Endpoint**: `POST /api/auth/password-reset-confirm/`

**Authentication**: None

**Request Body**:
```json
{
  "token": "reset-token-from-email",
  "password": "NewSecurePassword123!",
  "password_confirm": "NewSecurePassword123!"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Password reset successful"
}
```

---

### Get Current User

Get authenticated user information.

**Endpoint**: `GET /api/auth/me/`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "email": "student@iiti.ac.in",
  "is_verified": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

---

## Profile Endpoints

### Create Profile

Create anonymous profile for authenticated user.

**Endpoint**: `POST /api/profiles/`

**Authentication**: Required

**Request Body**:
```json
{
  "age": 21,
  "interests": ["coding", "music", "sports"],
  "hobbies": ["guitar", "basketball"],
  "relationship_intent": "friendship",
  "personality_tags": ["introverted", "creative"],
  "bio": "Optional bio text"
}
```

**Validation Rules**:
- `age`: 18-100
- `relationship_intent`: One of ["friendship", "dating", "casual"]
- `interests`, `hobbies`, `personality_tags`: Arrays of strings

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "anonymous_id": "uuid",
  "age": 21,
  "interests": ["coding", "music", "sports"],
  "hobbies": ["guitar", "basketball"],
  "relationship_intent": "friendship",
  "personality_tags": ["introverted", "creative"],
  "bio": "Optional bio text",
  "avatar": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid data
- `409 Conflict`: Profile already exists

---

### Get Own Profile

Get authenticated user's profile.

**Endpoint**: `GET /api/profiles/me/`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "anonymous_id": "uuid",
  "age": 21,
  "interests": ["coding", "music", "sports"],
  "hobbies": ["guitar", "basketball"],
  "relationship_intent": "friendship",
  "personality_tags": ["introverted", "creative"],
  "bio": "Optional bio text",
  "avatar": "https://example.com/media/avatars/uuid.jpg",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

---

### Update Profile

Update authenticated user's profile.

**Endpoint**: `PUT /api/profiles/me/`

**Authentication**: Required

**Request Body**: Same as Create Profile

**Success Response** (200 OK): Same as Get Own Profile

---

### Upload Avatar

Upload profile picture with anonymity filters.

**Endpoint**: `POST /api/profiles/avatar/`

**Authentication**: Required

**Request**: Multipart form data
```
avatar: <image file>
```

**Validation**:
- File types: JPEG, PNG, WebP
- Max size: 5MB
- Image will be processed with anonymity filters

**Success Response** (200 OK):
```json
{
  "avatar": "https://example.com/media/avatars/uuid.jpg"
}
```

---

### Get Profile by UUID

Get any user's anonymous profile.

**Endpoint**: `GET /api/profiles/{anonymous_id}/`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "anonymous_id": "uuid",
  "age": 21,
  "interests": ["coding", "music", "sports"],
  "hobbies": ["guitar", "basketball"],
  "relationship_intent": "friendship",
  "personality_tags": ["introverted", "creative"],
  "bio": "Optional bio text",
  "avatar": "https://example.com/media/avatars/uuid.jpg"
}
```

**Note**: Response never includes email or real identity

---

## Chatroom Endpoints

### List Chatrooms

Get all available public chatrooms.

**Endpoint**: `GET /api/chatrooms/`

**Authentication**: Required

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Success Response** (200 OK):
```json
{
  "count": 10,
  "next": "http://api/chatrooms/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "General Chat",
      "description": "General discussion",
      "member_count": 42,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Get Chatroom Details

Get details of a specific chatroom.

**Endpoint**: `GET /api/chatrooms/{chatroom_id}/`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "General Chat",
  "description": "General discussion",
  "member_count": 42,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Chatroom Messages

Get messages from a chatroom with pagination.

**Endpoint**: `GET /api/chatrooms/{chatroom_id}/messages/`

**Authentication**: Required

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 100)
- `before`: Get messages before this timestamp (ISO 8601)

**Success Response** (200 OK):
```json
{
  "count": 1000,
  "next": "http://api/chatrooms/uuid/messages/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "sender": {
        "anonymous_id": "uuid",
        "avatar": "https://example.com/media/avatars/uuid.jpg"
      },
      "content": "Hello everyone!",
      "message_type": "text",
      "media_url": null,
      "is_edited": false,
      "is_deleted": false,
      "is_pinned": false,
      "reactions": [
        {
          "emoji": "👍",
          "count": 5,
          "users": ["uuid1", "uuid2"]
        }
      ],
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

### Send Message

Send a message to a chatroom.

**Endpoint**: `POST /api/chatrooms/{chatroom_id}/messages/`

**Authentication**: Required

**Request Body**:
```json
{
  "content": "Hello everyone!",
  "message_type": "text"
}
```

**Message Types**: `text`, `image`, `voice`, `system`

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "sender": {
    "anonymous_id": "uuid",
    "avatar": "https://example.com/media/avatars/uuid.jpg"
  },
  "content": "Hello everyone!",
  "message_type": "text",
  "created_at": "2024-01-01T12:00:00Z"
}
```

---

### Edit Message

Edit a message (only own messages).

**Endpoint**: `PUT /api/chatrooms/messages/{message_id}/`

**Authentication**: Required

**Request Body**:
```json
{
  "content": "Updated message content"
}
```

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "content": "Updated message content",
  "is_edited": true,
  "updated_at": "2024-01-01T12:05:00Z"
}
```

---

### Delete Message

Delete a message (only own messages).

**Endpoint**: `DELETE /api/chatrooms/messages/{message_id}/`

**Authentication**: Required

**Success Response** (204 No Content)

---

### React to Message

Add emoji reaction to a message.

**Endpoint**: `POST /api/chatrooms/messages/{message_id}/react/`

**Authentication**: Required

**Request Body**:
```json
{
  "emoji": "👍"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Reaction added",
  "reactions": [
    {
      "emoji": "👍",
      "count": 6,
      "users": ["uuid1", "uuid2", "uuid3"]
    }
  ]
}
```

---

### Pin/Unpin Message

Pin or unpin a message in chatroom.

**Endpoint**: `POST /api/chatrooms/messages/{message_id}/pin/`

**Authentication**: Required (moderator only)

**Request Body**:
```json
{
  "pinned": true
}
```

**Success Response** (200 OK):
```json
{
  "message": "Message pinned",
  "is_pinned": true
}
```

---

## Matchmaking Endpoints

### Get Profiles for Swiping

Get profiles to swipe on (excludes already swiped).

**Endpoint**: `GET /api/matchmaking/profiles/`

**Authentication**: Required

**Query Parameters**:
- `limit`: Number of profiles to return (default: 10, max: 50)

**Success Response** (200 OK):
```json
{
  "profiles": [
    {
      "anonymous_id": "uuid",
      "age": 21,
      "interests": ["coding", "music"],
      "hobbies": ["guitar"],
      "relationship_intent": "friendship",
      "personality_tags": ["introverted"],
      "bio": "Love coding and music",
      "avatar": "https://example.com/media/avatars/uuid.jpg"
    }
  ]
}
```

---

### Record Swipe

Record a left or right swipe on a profile.

**Endpoint**: `POST /api/matchmaking/swipe/`

**Authentication**: Required

**Request Body**:
```json
{
  "swiped_profile": "uuid",
  "direction": "right"
}
```

**Direction**: `left` or `right`

**Success Response** (200 OK):

If no match:
```json
{
  "matched": false,
  "message": "Swipe recorded"
}
```

If mutual match:
```json
{
  "matched": true,
  "match": {
    "id": "uuid",
    "profile": {
      "anonymous_id": "uuid",
      "age": 21,
      "avatar": "https://example.com/media/avatars/uuid.jpg"
    },
    "matched_at": "2024-01-01T12:00:00Z"
  }
}
```

---

### Get Matches

Get all current matches.

**Endpoint**: `GET /api/matchmaking/matches/`

**Authentication**: Required

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Success Response** (200 OK):
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "profile": {
        "anonymous_id": "uuid",
        "age": 21,
        "avatar": "https://example.com/media/avatars/uuid.jpg"
      },
      "matched_at": "2024-01-01T12:00:00Z",
      "is_active": true,
      "last_message": {
        "content": "Hey!",
        "created_at": "2024-01-01T12:05:00Z"
      }
    }
  ]
}
```

---

### Get Match Details

Get details of a specific match.

**Endpoint**: `GET /api/matchmaking/matches/{match_id}/`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "profile": {
    "anonymous_id": "uuid",
    "age": 21,
    "interests": ["coding", "music"],
    "avatar": "https://example.com/media/avatars/uuid.jpg"
  },
  "matched_at": "2024-01-01T12:00:00Z",
  "is_active": true
}
```

---

### Get Match Messages

Get messages from a match chat.

**Endpoint**: `GET /api/matchmaking/matches/{match_id}/messages/`

**Authentication**: Required

**Query Parameters**: Same as chatroom messages

**Success Response** (200 OK): Same format as chatroom messages

---

### Send Match Message

Send message to a match.

**Endpoint**: `POST /api/matchmaking/matches/{match_id}/messages/`

**Authentication**: Required

**Request Body**:
```json
{
  "content": "Hey! How are you?",
  "message_type": "text"
}
```

**Success Response** (201 Created): Same format as chatroom message

---

## Reports Endpoints

### Create Report

Report a user for inappropriate behavior.

**Endpoint**: `POST /api/reports/`

**Authentication**: Required

**Request Body**:
```json
{
  "reported_user": "uuid",
  "reason": "harassment",
  "description": "Detailed description of the issue"
}
```

**Reason Options**: `harassment`, `spam`, `inappropriate`, `other`

**Success Response** (201 Created):
```json
{
  "id": "uuid",
  "reason": "harassment",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z"
}
```

---

### Block User

Block a user to prevent all communication.

**Endpoint**: `POST /api/reports/block/`

**Authentication**: Required

**Request Body**:
```json
{
  "blocked_user": "uuid"
}
```

**Success Response** (201 Created):
```json
{
  "message": "User blocked successfully",
  "blocked_user": "uuid",
  "created_at": "2024-01-01T12:00:00Z"
}
```

---

### Get Blocked Users

Get list of blocked users.

**Endpoint**: `GET /api/reports/blocked/`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "blocked_users": [
    {
      "anonymous_id": "uuid",
      "blocked_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

### Unblock User

Unblock a previously blocked user.

**Endpoint**: `DELETE /api/reports/block/{anonymous_id}/`

**Authentication**: Required

**Success Response** (204 No Content)

---

## Admin Endpoints

All admin endpoints require admin/staff privileges.

### List Reports

Get all user reports for moderation.

**Endpoint**: `GET /api/admin/reports/`

**Authentication**: Required (Admin)

**Query Parameters**:
- `status`: Filter by status (`pending`, `reviewed`, `resolved`)
- `page`: Page number

**Success Response** (200 OK):
```json
{
  "count": 50,
  "results": [
    {
      "id": "uuid",
      "reporter": "uuid",
      "reported": "uuid",
      "reason": "harassment",
      "description": "Description",
      "status": "pending",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

### Update Report Status

Update the status of a report.

**Endpoint**: `PUT /api/admin/reports/{report_id}/`

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "status": "resolved",
  "admin_notes": "Action taken"
}
```

**Success Response** (200 OK):
```json
{
  "id": "uuid",
  "status": "resolved",
  "reviewed_by": "admin-uuid",
  "reviewed_at": "2024-01-01T13:00:00Z"
}
```

---

### Get User Details

Get user details for moderation (anonymous IDs only).

**Endpoint**: `GET /api/admin/users/{anonymous_id}/`

**Authentication**: Required (Admin)

**Success Response** (200 OK):
```json
{
  "anonymous_id": "uuid",
  "profile": {
    "age": 21,
    "interests": ["coding"]
  },
  "reports_received": 3,
  "reports_made": 1,
  "is_banned": false,
  "joined_at": "2024-01-01T00:00:00Z"
}
```

---

### Ban User

Ban a user from the platform.

**Endpoint**: `POST /api/admin/users/{anonymous_id}/ban/`

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "reason": "Multiple violations",
  "duration_days": 7
}
```

**Success Response** (200 OK):
```json
{
  "message": "User banned successfully",
  "banned_until": "2024-01-08T00:00:00Z"
}
```

---

### Send Broadcast Message

Send message to all users or specific chatroom.

**Endpoint**: `POST /api/admin/broadcast/`

**Authentication**: Required (Admin)

**Request Body**:
```json
{
  "message": "Important announcement",
  "chatroom": "uuid",
  "type": "announcement"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Broadcast sent successfully",
  "recipients": 150
}
```

---

### Get Platform Metrics

Get platform health and usage metrics.

**Endpoint**: `GET /api/admin/metrics/`

**Authentication**: Required (Admin)

**Query Parameters**:
- `period`: Time period (`day`, `week`, `month`)

**Success Response** (200 OK):
```json
{
  "active_users": 500,
  "total_users": 1000,
  "messages_sent": 10000,
  "matches_created": 250,
  "reports_pending": 5,
  "chatrooms_active": 10
}
```

---

## Search Endpoints

### Search Messages

Search through message history.

**Endpoint**: `GET /api/chatrooms/search/`

**Authentication**: Required

**Query Parameters**:
- `q`: Search query (required)
- `chatroom`: Filter by chatroom UUID (optional)
- `page`: Page number

**Success Response** (200 OK):
```json
{
  "count": 25,
  "results": [
    {
      "message": {
        "id": "uuid",
        "content": "This is the <mark>search term</mark> in context",
        "sender": {
          "anonymous_id": "uuid"
        },
        "created_at": "2024-01-01T12:00:00Z"
      },
      "chatroom": {
        "id": "uuid",
        "name": "General Chat"
      }
    }
  ]
}
```

**Note**: Search results include HTML `<mark>` tags for highlighting

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `PERMISSION_DENIED` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource conflict (e.g., duplicate) |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |

---

## HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful request with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Pagination

All list endpoints support pagination with the following parameters:

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default varies by endpoint)

**Response Format**:
```json
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering and Sorting

Some endpoints support filtering and sorting:

**Query Parameters**:
- `ordering`: Sort field (prefix with `-` for descending)
- `search`: Text search
- Custom filters vary by endpoint

Example: `GET /api/chatrooms/?ordering=-created_at&search=general`

---

## CORS

CORS is configured to allow requests from:
- Development: `http://localhost:5173`
- Production: Your configured frontend domain

Allowed methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`

---

## Versioning

Current API version: `v1`

API versioning is not yet implemented but will follow the pattern:
- `/api/v1/...`
- `/api/v2/...`

---

## Deprecation Policy

When endpoints are deprecated:
1. Announcement 30 days before deprecation
2. Deprecation header added: `Deprecation: true`
3. Alternative endpoint provided in `Link` header
4. Minimum 90 days before removal

---

## Support

For API issues or questions:
- Check this documentation
- Review error messages and codes
- Open an issue on GitHub
- Contact the development team
