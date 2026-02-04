# Profile System Demo

## Quick Start

### 1. Run the Django server
```bash
cd backend
python manage.py runserver
```

### 2. Test the API endpoints

#### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@iiti.ac.in",
    "password": "TestPass123!",
    "password2": "TestPass123!"
  }'
```

#### Login to get access token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@iiti.ac.in",
    "password": "TestPass123!"
  }'
```

Save the `access` token from the response.

#### Create a profile
```bash
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "age": 22,
    "interests": ["coding", "music", "reading"],
    "hobbies": ["guitar", "hiking", "photography"],
    "relationship_intent": "friendship",
    "personality_tags": ["introverted", "creative", "analytical"],
    "bio": "Love coding and music!"
  }'
```

Response will include `anonymous_id` - save this!

#### Get your own profile
```bash
curl -X GET http://localhost:8000/api/profiles/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update your profile
```bash
curl -X PATCH http://localhost:8000/api/profiles/me/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "age": 23,
    "bio": "Updated bio!"
  }'
```

#### Get profile by anonymous_id
```bash
curl -X GET http://localhost:8000/api/profiles/ANONYMOUS_ID_HERE/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Upload avatar
```bash
curl -X POST http://localhost:8000/api/profiles/avatar/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "avatar=@/path/to/your/image.jpg"
```

## Key Features Demonstrated

### 1. Anonymity
- Every profile gets a unique `anonymous_id` (UUID)
- No email or username in API responses
- Profile can be retrieved by `anonymous_id` only

### 2. Validation
- Age must be 18-100
- Relationship intent must be: friendship, dating, or casual
- Interests, hobbies, personality_tags must be arrays of strings
- Avatar must be JPEG, PNG, or GIF (max 5MB)

### 3. Security
- All endpoints require authentication
- Server-side validation on all inputs
- File type and size validation on uploads

### 4. Privacy
- No personal information (email, real name) exposed in any response
- Only anonymous_id is public
- User can only update their own profile

## Example Response

```json
{
  "anonymous_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "age": 22,
  "interests": ["coding", "music", "reading"],
  "hobbies": ["guitar", "hiking", "photography"],
  "relationship_intent": "friendship",
  "personality_tags": ["introverted", "creative", "analytical"],
  "bio": "Love coding and music!",
  "avatar": "/media/avatars/avatar_xyz.jpg",
  "created_at": "2024-12-02T10:30:00Z",
  "updated_at": "2024-12-02T10:30:00Z"
}
```

Note: No `email`, `username`, or `user` fields in the response!

## Run Tests

```bash
cd backend
python manage.py test profiles
```

All 12 tests should pass!
