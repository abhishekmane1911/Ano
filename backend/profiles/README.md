# Profile System

Anonymous profile management system for the Ano platform.

## Overview

The profile system enables users to create and manage anonymous profiles with interests, hobbies, and preferences while maintaining complete privacy. All profiles use UUID-based anonymous identifiers, and no personal information (email, real name) is ever exposed through the API.

## Features

- ✅ Anonymous profile creation with UUID identifiers
- ✅ Profile fields: age, interests, hobbies, relationship intent, personality tags, bio
- ✅ Avatar upload with validation
- ✅ Server-side validation on all inputs
- ✅ Complete privacy - no PII in API responses
- ✅ RESTful API endpoints
- ✅ Comprehensive test coverage

## Quick Start

### 1. Run migrations
```bash
python manage.py migrate profiles
```

### 2. Start the server
```bash
python manage.py runserver
```

### 3. Create a profile
```bash
# First, register and login to get an access token
# Then create a profile:
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "age": 22,
    "interests": ["coding", "music"],
    "hobbies": ["guitar", "hiking"],
    "relationship_intent": "friendship",
    "personality_tags": ["introverted", "creative"]
  }'
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/profiles/` | Create profile | Yes |
| GET | `/api/profiles/me/` | Get own profile | Yes |
| PUT | `/api/profiles/me/` | Update own profile | Yes |
| PATCH | `/api/profiles/me/` | Partial update | Yes |
| POST | `/api/profiles/avatar/` | Upload avatar | Yes |
| GET | `/api/profiles/{uuid}/` | Get by anonymous_id | Yes |

## Data Model

```python
Profile:
  - id: UUID (primary key)
  - user: OneToOne(User)
  - anonymous_id: UUID (public identifier)
  - age: Integer (18-100)
  - interests: JSON Array
  - hobbies: JSON Array
  - relationship_intent: String (friendship/dating/casual)
  - personality_tags: JSON Array
  - bio: Text (optional, max 500 chars)
  - avatar: Image (optional)
  - created_at: DateTime
  - updated_at: DateTime
```

## Validation Rules

### Age
- Must be between 18 and 100
- Required field

### Interests, Hobbies, Personality Tags
- Must be arrays of strings
- Can be empty arrays
- Required fields

### Relationship Intent
- Must be one of: `friendship`, `dating`, `casual`
- Required field

### Bio
- Optional field
- Maximum 500 characters

### Avatar
- Optional field
- Allowed types: JPEG, PNG, GIF
- Maximum size: 5MB

## Privacy & Security

### Anonymity
- Every profile has a unique `anonymous_id` (UUID)
- Profile can only be retrieved by `anonymous_id`
- No email or real name in any API response
- Profile string representation uses `anonymous_id` only

### Authentication
- All endpoints require JWT authentication
- Users can only update their own profile
- One profile per user (enforced)

### Validation
- All inputs validated on server-side
- File type and size validation on uploads
- Proper error messages for invalid data

## Testing

Run the test suite:
```bash
python manage.py test profiles
```

Test coverage:
- 12 unit tests
- Model validation tests
- API endpoint tests
- Authentication tests
- Privacy verification tests

## Files

- `models.py` - Profile model definition
- `serializers.py` - DRF serializers
- `views.py` - API views
- `urls.py` - URL routing
- `admin.py` - Admin interface
- `tests.py` - Test suite
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation notes
- `DEMO.md` - Demo and usage guide
- `VERIFICATION_CHECKLIST.md` - Requirements verification

## Requirements Satisfied

- ✅ 3.1 - UUID assignment for profiles
- ✅ 3.2 - Store profile data without identity
- ✅ 3.3 - Avatar upload with filters
- ✅ 3.4 - Never expose email/name
- ✅ 3.5 - Server-side validation
- ✅ 14.1 - UUID format for identifiers
- ✅ 14.2 - Anonymous relationship storage
- ✅ 14.4 - No PII in API responses

## Next Steps

1. Implement profile system frontend (Task 5)
2. Add property-based tests (Tasks 4.1-4.5, optional)
3. Future enhancements:
   - Advanced anonymity filters for avatars
   - Profile picture moderation
   - Profile completeness scoring
   - Profile verification badges

## Support

For issues or questions, refer to:
- `DEMO.md` - Usage examples
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `tests.py` - Test examples
