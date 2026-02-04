# Matchmaking App

The matchmaking app provides Tinder-style profile swiping and anonymous match chat functionality for the Ano platform.

## Features

### Profile Swiping
- Browse anonymous profiles with interests, hobbies, age, and personality tags
- Swipe left to reject, swipe right to express interest
- Profiles are never shown twice
- Blocked users are filtered out (when Block model is implemented)

### Match Detection
- Automatic match creation when both users swipe right
- Instant notification of mutual matches
- Match records track both profiles and creation time

### Match Chat
- Anonymous one-on-one messaging between matched users
- Messages stored with match reference
- Paginated message history
- Real-time delivery via WebSocket (to be implemented)

## API Endpoints

### Get Profiles for Swiping
```
GET /api/matchmaking/profiles/
```
Returns profiles that haven't been swiped on yet.

**Response:**
```json
[
  {
    "anonymous_id": "uuid",
    "age": 22,
    "interests": ["coding", "music"],
    "hobbies": ["reading"],
    "relationship_intent": "friendship",
    "personality_tags": ["introverted"],
    "bio": "Optional bio text",
    "avatar": "/media/avatars/...",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### Record Swipe
```
POST /api/matchmaking/swipe/
```

**Request:**
```json
{
  "swiped": "profile-uuid",
  "direction": "left" | "right"
}
```

**Response (no match):**
```json
{
  "swipe": {
    "id": "uuid",
    "swiper": "profile-uuid",
    "swiped": "profile-uuid",
    "direction": "right",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "is_match": false
}
```

**Response (with match):**
```json
{
  "swipe": { ... },
  "match": {
    "id": "uuid",
    "profile1": { ... },
    "profile2": { ... },
    "other_profile": { ... },
    "matched_at": "2024-01-01T00:00:00Z",
    "is_active": true
  },
  "is_match": true
}
```

### List Matches
```
GET /api/matchmaking/matches/
```
Returns all active matches for the current user.

### Get Match Detail
```
GET /api/matchmaking/matches/{match_id}/
```
Returns details of a specific match.

### Get Match Messages
```
GET /api/matchmaking/matches/{match_id}/messages/
```
Returns paginated messages for a match chat.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 50)

### Send Match Message
```
POST /api/matchmaking/matches/{match_id}/messages/send/
```

**Request:**
```json
{
  "content": "Hello!",
  "message_type": "text" | "image" | "voice"
}
```

## Models

### Swipe
- `id`: UUID primary key
- `swiper`: Profile that performed the swipe
- `swiped`: Profile that was swiped on
- `direction`: "left" or "right"
- `created_at`: Timestamp

**Constraints:**
- Unique together: (swiper, swiped)
- Cannot swipe on own profile
- Cannot swipe on same profile twice

### Match
- `id`: UUID primary key
- `profile1`: First profile in the match
- `profile2`: Second profile in the match
- `matched_at`: Timestamp
- `is_active`: Boolean

**Methods:**
- `get_other_profile(profile)`: Returns the other profile in the match
- `has_profile(profile)`: Checks if a profile is part of the match

## Security

- All endpoints require authentication
- Users can only access their own matches
- Profile data never includes email or real names
- Only anonymous identifiers are exposed

## Testing

Run tests with:
```bash
python manage.py test matchmaking
```

All 12 tests should pass, covering:
- Profile retrieval and filtering
- Swipe recording and validation
- Match creation logic
- Match chat messaging
- Authorization checks
