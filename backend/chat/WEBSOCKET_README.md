# WebSocket Chat Implementation

## Overview

This implementation provides real-time chat functionality using Django Channels and WebSockets. It supports all the features required for the Ano platform including message sending, editing, deleting, reactions, typing indicators, presence updates, and read receipts.

## Architecture

- **Django Channels**: ASGI framework for WebSocket support
- **Redis**: Channel layer backend for message broadcasting
- **JWT Authentication**: Secure WebSocket connections using JWT tokens
- **Rate Limiting**: Prevents message spam (10 messages per 10 seconds)

## WebSocket Endpoint

```
ws://localhost:8000/ws/chat/<chatroom_id>/?token=<jwt_access_token>
```

### Authentication

WebSocket connections require a valid JWT access token passed as a query parameter. The token is validated on connection, and if invalid, the connection is closed with code 4001.

## Supported Events

### Client → Server Events

#### 1. Send Message
```json
{
  "type": "message.send",
  "content": "Hello, World!",
  "message_type": "text",
  "media_url": ""
}
```

#### 2. Edit Message
```json
{
  "type": "message.edit",
  "message_id": "uuid-here",
  "content": "Updated content"
}
```

#### 3. Delete Message
```json
{
  "type": "message.delete",
  "message_id": "uuid-here"
}
```

#### 4. React to Message
```json
{
  "type": "message.react",
  "message_id": "uuid-here",
  "emoji": "👍"
}
```

#### 5. Typing Start
```json
{
  "type": "typing.start"
}
```

#### 6. Typing Stop
```json
{
  "type": "typing.stop"
}
```

#### 7. Read Receipt
```json
{
  "type": "read.receipt",
  "message_id": "uuid-here"
}
```

### Server → Client Events

#### 1. Message Received
```json
{
  "type": "message.receive",
  "message": {
    "id": "uuid",
    "chatroom_id": "uuid",
    "sender_id": "anonymous-uuid",
    "content": "Hello, World!",
    "message_type": "text",
    "media_url": "",
    "is_edited": false,
    "is_deleted": false,
    "is_pinned": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 2. Message Edited
```json
{
  "type": "message.edit",
  "message": {
    "id": "uuid",
    "content": "Updated content",
    "is_edited": true,
    ...
  }
}
```

#### 3. Message Deleted
```json
{
  "type": "message.delete",
  "message_id": "uuid",
  "timestamp": 1234567890.123
}
```

#### 4. Message Reaction
```json
{
  "type": "message.react",
  "message_id": "uuid",
  "emoji": "👍",
  "profile_id": "anonymous-uuid",
  "reaction_id": "uuid",
  "timestamp": 1234567890.123
}
```

#### 5. Typing Indicator
```json
{
  "type": "typing.start",
  "profile_id": "anonymous-uuid",
  "timestamp": 1234567890.123
}
```

```json
{
  "type": "typing.stop",
  "profile_id": "anonymous-uuid",
  "timestamp": 1234567890.123
}
```

#### 6. User Join/Leave
```json
{
  "type": "user.join",
  "profile_id": "anonymous-uuid",
  "timestamp": 1234567890.123
}
```

```json
{
  "type": "user.leave",
  "profile_id": "anonymous-uuid",
  "timestamp": 1234567890.123
}
```

#### 7. Read Receipt
```json
{
  "type": "read.receipt",
  "message_id": "uuid",
  "profile_id": "anonymous-uuid",
  "timestamp": 1234567890.123
}
```

#### 8. Error
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Security Features

### JWT Authentication
- Tokens are validated on connection
- Invalid tokens result in connection closure (code 4001)
- Tokens are passed via query parameter: `?token=<jwt_token>`

### Rate Limiting
- Maximum 10 messages per 10 seconds per user
- Applies to all WebSocket events
- Exceeding limit returns error message

### Authorization
- Users can only edit/delete their own messages
- Chatroom existence is verified on connection
- User must have a profile to connect

## Error Codes

- **4001**: Authentication failed (invalid or missing token)
- **4003**: Profile not found
- **4004**: Chatroom not found

## Testing

The implementation includes comprehensive tests covering:
- Connection with/without authentication
- Message sending, editing, and deleting
- Reactions and read receipts
- Typing indicators
- Rate limiting

Run tests with:
```bash
pytest chat/test_websocket.py -v
```

## Frontend Integration Example

```javascript
// Connect to WebSocket
const token = localStorage.getItem('access_token');
const chatroomId = 'your-chatroom-uuid';
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${chatroomId}/?token=${token}`);

// Handle connection
ws.onopen = () => {
  console.log('Connected to chat');
};

// Handle incoming messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'message.receive':
      // Add message to UI
      addMessageToChat(data.message);
      break;
    case 'typing.start':
      // Show typing indicator
      showTypingIndicator(data.profile_id);
      break;
    case 'user.join':
      // Update online users
      updateOnlineUsers(data.profile_id, true);
      break;
    // ... handle other events
  }
};

// Send a message
function sendMessage(content) {
  ws.send(JSON.stringify({
    type: 'message.send',
    content: content,
    message_type: 'text'
  }));
}

// Send typing indicator
function startTyping() {
  ws.send(JSON.stringify({
    type: 'typing.start'
  }));
}

// Handle disconnection
ws.onclose = (event) => {
  console.log('Disconnected from chat', event.code);
  // Implement reconnection logic
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

## Running the Server

### Development
```bash
# Start Django with Daphne (ASGI server)
daphne -b 0.0.0.0 -p 8000 ano_backend.asgi:application
```

### Production
Configure Daphne with systemd or supervisor for production deployment.

## Requirements

- Django Channels 4.3.2
- channels-redis 4.3.0
- daphne 4.2.0
- Redis server running on localhost:6379

## Configuration

WebSocket configuration is in `settings.py`:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
    },
}
```

## Troubleshooting

### Connection Refused
- Ensure Redis is running: `redis-cli ping`
- Check ASGI application is running with Daphne

### Authentication Errors
- Verify JWT token is valid and not expired
- Check token is passed correctly in query parameter

### Messages Not Broadcasting
- Verify Redis channel layer is configured correctly
- Check multiple users are in the same chatroom group
