# Chat API Demo

This guide demonstrates how to use the Chat API endpoints.

## Prerequisites

1. Start the Django server:
```bash
cd backend
python manage.py runserver
```

2. Create a test chatroom in Django shell:
```bash
python manage.py shell
```

```python
from chat.models import Chatroom
chatroom = Chatroom.objects.create(
    name='General',
    description='General discussion for all students'
)
print(f"Created chatroom: {chatroom.id}")
exit()
```

## API Demo Flow

### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "chatdemo",
    "email": "chatdemo@iiti.ac.in",
    "password": "DemoPass123!",
    "password2": "DemoPass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "chatdemo@iiti.ac.in",
    "password": "DemoPass123!"
  }'
```

Save the access token from the response.

### 2. Create Profile

```bash
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "age": 21,
    "interests": ["coding", "music"],
    "hobbies": ["reading"],
    "relationship_intent": "friendship",
    "personality_tags": ["introverted"],
    "bio": "Chat demo user"
  }'
```

### 3. List Chatrooms

```bash
curl -X GET http://localhost:8000/api/chat/chatrooms/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
[
  {
    "id": "chatroom-uuid",
    "name": "General",
    "description": "General discussion for all students",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "member_count": 0
  }
]
```

### 4. Get Chatroom Details

```bash
curl -X GET http://localhost:8000/api/chat/chatrooms/CHATROOM_UUID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Send a Message

```bash
curl -X POST http://localhost:8000/api/chat/chatrooms/CHATROOM_UUID/send_message/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "content": "Hello everyone! This is my first message.",
    "message_type": "text"
  }'
```

Response:
```json
{
  "id": "message-uuid",
  "chatroom": "chatroom-uuid",
  "sender_id": "anonymous-uuid",
  "content": "Hello everyone! This is my first message.",
  "message_type": "text",
  "media_url": "",
  "is_edited": false,
  "is_deleted": false,
  "is_pinned": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "reactions": [],
  "reaction_count": {}
}
```

### 6. Get Chatroom Messages

```bash
curl -X GET "http://localhost:8000/api/chat/chatrooms/CHATROOM_UUID/messages/?page=1&page_size=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "message-uuid",
      "chatroom": "chatroom-uuid",
      "sender_id": "anonymous-uuid",
      "content": "Hello everyone! This is my first message.",
      "message_type": "text",
      "media_url": "",
      "is_edited": false,
      "is_deleted": false,
      "is_pinned": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "reactions": [],
      "reaction_count": {}
    }
  ]
}
```

### 7. Edit a Message

```bash
curl -X PUT http://localhost:8000/api/chat/messages/MESSAGE_UUID/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "content": "Hello everyone! This is my edited message."
  }'
```

Response:
```json
{
  "id": "message-uuid",
  "chatroom": "chatroom-uuid",
  "sender_id": "anonymous-uuid",
  "content": "Hello everyone! This is my edited message.",
  "message_type": "text",
  "media_url": "",
  "is_edited": true,
  "is_deleted": false,
  "is_pinned": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:01:00Z",
  "reactions": [],
  "reaction_count": {}
}
```

### 8. React to a Message

```bash
curl -X POST http://localhost:8000/api/chat/messages/MESSAGE_UUID/react/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "emoji": "👍"
  }'
```

Response:
```json
{
  "id": "reaction-uuid",
  "emoji": "👍",
  "profile_id": "anonymous-uuid",
  "created_at": "2024-01-01T00:02:00Z"
}
```

### 9. Pin a Message

```bash
curl -X POST http://localhost:8000/api/chat/messages/MESSAGE_UUID/pin/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "id": "message-uuid",
  "chatroom": "chatroom-uuid",
  "sender_id": "anonymous-uuid",
  "content": "Hello everyone! This is my edited message.",
  "message_type": "text",
  "media_url": "",
  "is_edited": true,
  "is_deleted": false,
  "is_pinned": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:03:00Z",
  "reactions": [
    {
      "id": "reaction-uuid",
      "emoji": "👍",
      "profile_id": "anonymous-uuid",
      "created_at": "2024-01-01T00:02:00Z"
    }
  ],
  "reaction_count": {
    "👍": 1
  }
}
```

### 10. Delete a Message

```bash
curl -X DELETE http://localhost:8000/api/chat/messages/MESSAGE_UUID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response: 204 No Content

The message will be soft-deleted (content replaced with "[Message deleted]").

## Python Script Demo

Run the automated test script:

```bash
cd backend
python test_chat_manual.py
```

This script will:
1. Register/login a user
2. Create a profile
3. List chatrooms
4. Send a message
5. Edit the message
6. React to the message
7. Pin/unpin the message
8. Delete the message

## Notes

- All endpoints require JWT authentication
- Users can only edit/delete their own messages
- All responses use anonymous identifiers (no emails or real names)
- Messages are soft-deleted (is_deleted flag set to true)
- Reactions are unique per profile per message per emoji
- Pagination defaults to 50 messages per page

## Error Handling

### 400 Bad Request
- Empty message content
- Invalid message type
- Missing required fields

### 403 Forbidden
- Attempting to edit/delete another user's message

### 404 Not Found
- Chatroom or message doesn't exist
- Inactive chatroom

### 401 Unauthorized
- Missing or invalid JWT token
- Token expired

## Next Steps

After testing the REST API:
1. Implement WebSocket support for real-time updates (Task 7)
2. Build the frontend chat interface (Task 8)
3. Add search functionality (Task 16)
