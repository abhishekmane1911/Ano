# Chat App

The chat app provides anonymous chatroom functionality for the Ano platform, including real-time messaging, reactions, read receipts, and media support.

## Features

- **Public Chatrooms**: Anonymous group chat with multiple participants
- **Message Management**: Send, edit, delete messages with soft delete
- **Reactions**: Emoji reactions on messages
- **Message Pinning**: Pin important messages in chatrooms
- **Read Receipts**: Track when messages are read
- **Media Support**: Upload and compress images for chat
- **Pagination**: Efficient message loading with infinite scroll support
- **Anonymity**: All messages use anonymous profile identifiers

## Models

### Chatroom
- Public chatroom for group communication
- Fields: name, description, is_active, member_count
- UUID-based identifier

### Message
- Message in a chatroom or match chat
- Fields: content, message_type (text/image/voice/system), media_url
- Flags: is_edited, is_deleted, is_pinned
- Supports both chatroom and match messages (match field added later)

### MessageReaction
- Emoji reaction to a message
- Unique constraint: one emoji per profile per message
- Fields: emoji, profile, message

### ReadReceipt
- Track when a message is read
- Unique constraint: one receipt per profile per message
- Fields: profile, message, read_at

## API Endpoints

### Chatroom Endpoints

#### List Chatrooms
```
GET /api/chat/chatrooms/
```
Returns all active chatrooms.

#### Get Chatroom Details
```
GET /api/chat/chatrooms/{id}/
```
Returns details for a specific chatroom.

#### Get Chatroom Messages
```
GET /api/chat/chatrooms/{id}/messages/
```
Returns paginated messages for a chatroom (50 per page).

Query parameters:
- `page`: Page number
- `page_size`: Number of messages per page (max 100)

#### Send Message
```
POST /api/chat/chatrooms/{id}/send_message/
```
Send a message to a chatroom.

Request body:
```json
{
  "content": "Message text",
  "message_type": "text",
  "media_url": "optional_url"
}
```

### Message Endpoints

#### Edit Message
```
PUT /api/chat/messages/{id}/
```
Edit a message (only by sender).

Request body:
```json
{
  "content": "Updated message text"
}
```

#### Delete Message
```
DELETE /api/chat/messages/{id}/
```
Soft delete a message (only by sender). Sets is_deleted=True and clears content.

#### React to Message
```
POST /api/chat/messages/{id}/react/
```
Add an emoji reaction to a message.

Request body:
```json
{
  "emoji": "👍"
}
```

#### Pin/Unpin Message
```
POST /api/chat/messages/{id}/pin/
```
Toggle pin status of a message.

#### Upload Media
```
POST /api/chat/messages/{id}/upload_media/
```
Upload and compress an image for a message.

Request: multipart/form-data with 'file' field

Response:
```json
{
  "media_url": "/media/chat_media/filename.jpg"
}
```

## Database Indexes

For optimal query performance:
- `messages`: Composite index on (chatroom, created_at)
- `messages`: Index on sender
- `messages`: Index on is_pinned
- `message_reactions`: Unique together (message, profile, emoji)
- `read_receipts`: Unique together (message, profile)

## Testing

Run tests:
```bash
python manage.py test chat
```

Manual API testing:
```bash
# Start the server first
python manage.py runserver

# In another terminal
python test_chat_manual.py
```

## Usage Example

```python
from chat.models import Chatroom, Message
from profiles.models import Profile

# Create a chatroom
chatroom = Chatroom.objects.create(
    name='General',
    description='General discussion'
)

# Send a message
profile = Profile.objects.get(user=request.user)
message = Message.objects.create(
    chatroom=chatroom,
    sender=profile,
    content='Hello everyone!',
    message_type='text'
)

# React to a message
from chat.models import MessageReaction
reaction = MessageReaction.objects.create(
    message=message,
    profile=profile,
    emoji='👍'
)

# Pin a message
message.is_pinned = True
message.save()
```

## Security

- All endpoints require authentication (JWT token)
- Users can only edit/delete their own messages
- All API responses use anonymous identifiers (no emails or real names)
- Input validation on all endpoints
- Media uploads are validated and compressed

## Future Enhancements

- WebSocket support for real-time updates (Task 7)
- Voice message support
- Message search functionality (Task 16)
- Admin moderation tools (Task 14)
