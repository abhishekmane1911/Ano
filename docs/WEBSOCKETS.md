# WebSocket Documentation

Complete WebSocket events and payloads reference for real-time features.

## Overview

Ano uses WebSocket connections for real-time communication in chatrooms and match chats. The WebSocket implementation is built on Django Channels with Redis as the channel layer.

## Connection URLs

### Development
- **Chat**: `ws://localhost:8000/ws/chat/{chatroom_id}/`
- **Match**: `ws://localhost:8000/ws/match/{match_id}/`

### Production
- **Chat**: `wss://your-domain.com/ws/chat/{chatroom_id}/`
- **Match**: `wss://your-domain.com/ws/match/{match_id}/`

## Authentication

WebSocket connections require JWT authentication via query parameter:

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/${chatroomId}/?token=${accessToken}`
);
```

**Authentication Flow**:
1. Client connects with JWT token in query string
2. Server validates token
3. If valid, connection established
4. If invalid, connection closed with code 4001

## Connection Lifecycle

### 1. Connect

```javascript
const socket = new WebSocket(url);

socket.onopen = () => {
  console.log('Connected to WebSocket');
};
```

### 2. Send/Receive Messages

```javascript
// Send message
socket.send(JSON.stringify({
  type: 'message.send',
  data: { content: 'Hello!' }
}));

// Receive message
socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### 3. Handle Errors

```javascript
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### 4. Disconnect

```javascript
socket.onclose = (event) => {
  console.log('Disconnected:', event.code, event.reason);
};

// Manual close
socket.close();
```

## Message Format

All WebSocket messages follow this format:

```json
{
  "type": "event.name",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Chat WebSocket Events

Connection: `/ws/chat/{chatroom_id}/`

### Client → Server Events

#### message.send

Send a new message to the chatroom.

**Payload**:
```json
{
  "type": "message.send",
  "data": {
    "content": "Hello everyone!",
    "message_type": "text"
  }
}
```

**Message Types**: `text`, `image`, `voice`

---

#### message.edit

Edit an existing message (own messages only).

**Payload**:
```json
{
  "type": "message.edit",
  "data": {
    "message_id": "uuid",
    "content": "Updated message"
  }
}
```

---

#### message.delete

Delete a message (own messages only).

**Payload**:
```json
{
  "type": "message.delete",
  "data": {
    "message_id": "uuid"
  }
}
```

---

#### message.react

Add emoji reaction to a message.

**Payload**:
```json
{
  "type": "message.react",
  "data": {
    "message_id": "uuid",
    "emoji": "👍"
  }
}
```

---

#### typing.start

Indicate user started typing.

**Payload**:
```json
{
  "type": "typing.start",
  "data": {}
}
```

**Note**: Automatically expires after 3 seconds if not followed by message or typing.stop

---

#### typing.stop

Indicate user stopped typing.

**Payload**:
```json
{
  "type": "typing.stop",
  "data": {}
}
```

---

### Server → Client Events

#### message.receive

New message received in chatroom.

**Payload**:
```json
{
  "type": "message.receive",
  "data": {
    "id": "uuid",
    "sender": {
      "anonymous_id": "uuid",
      "avatar": "https://example.com/avatar.jpg"
    },
    "content": "Hello everyone!",
    "message_type": "text",
    "media_url": null,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

#### message.updated

Message was edited.

**Payload**:
```json
{
  "type": "message.updated",
  "data": {
    "message_id": "uuid",
    "content": "Updated message",
    "is_edited": true,
    "updated_at": "2024-01-01T12:05:00Z"
  },
  "timestamp": "2024-01-01T12:05:00Z"
}
```

---

#### message.deleted

Message was deleted.

**Payload**:
```json
{
  "type": "message.deleted",
  "data": {
    "message_id": "uuid"
  },
  "timestamp": "2024-01-01T12:05:00Z"
}
```

---

#### message.reaction

New reaction added to message.

**Payload**:
```json
{
  "type": "message.reaction",
  "data": {
    "message_id": "uuid",
    "emoji": "👍",
    "user": "uuid",
    "reactions": [
      {
        "emoji": "👍",
        "count": 5,
        "users": ["uuid1", "uuid2", "uuid3"]
      }
    ]
  },
  "timestamp": "2024-01-01T12:05:00Z"
}
```

---

#### typing.indicator

User is typing.

**Payload**:
```json
{
  "type": "typing.indicator",
  "data": {
    "user": {
      "anonymous_id": "uuid",
      "avatar": "https://example.com/avatar.jpg"
    },
    "is_typing": true
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

#### user.joined

User joined the chatroom.

**Payload**:
```json
{
  "type": "user.joined",
  "data": {
    "user": {
      "anonymous_id": "uuid",
      "avatar": "https://example.com/avatar.jpg"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

#### user.left

User left the chatroom.

**Payload**:
```json
{
  "type": "user.left",
  "data": {
    "user": {
      "anonymous_id": "uuid"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

#### read.receipt

Message was read by user.

**Payload**:
```json
{
  "type": "read.receipt",
  "data": {
    "message_id": "uuid",
    "user": "uuid",
    "read_at": "2024-01-01T12:05:00Z"
  },
  "timestamp": "2024-01-01T12:05:00Z"
}
```

---

#### error

Error occurred during message processing.

**Payload**:
```json
{
  "type": "error",
  "data": {
    "code": "INVALID_MESSAGE",
    "message": "Message content is required",
    "details": {}
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Match Chat WebSocket Events

Connection: `/ws/match/{match_id}/`

### Client → Server Events

#### message.send

Send message to match.

**Payload**:
```json
{
  "type": "message.send",
  "data": {
    "content": "Hey! How are you?",
    "message_type": "text"
  }
}
```

---

#### typing.start

Indicate typing in match chat.

**Payload**:
```json
{
  "type": "typing.start",
  "data": {}
}
```

---

#### typing.stop

Stop typing indicator.

**Payload**:
```json
{
  "type": "typing.stop",
  "data": {}
}
```

---

#### read.receipt

Mark message as read.

**Payload**:
```json
{
  "type": "read.receipt",
  "data": {
    "message_id": "uuid"
  }
}
```

---

### Server → Client Events

#### message.receive

New message from match.

**Payload**:
```json
{
  "type": "message.receive",
  "data": {
    "id": "uuid",
    "sender": {
      "anonymous_id": "uuid",
      "avatar": "https://example.com/avatar.jpg"
    },
    "content": "Hey! I'm good, thanks!",
    "message_type": "text",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

#### typing.indicator

Match is typing.

**Payload**:
```json
{
  "type": "typing.indicator",
  "data": {
    "is_typing": true
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

#### read.receipt

Match read your message.

**Payload**:
```json
{
  "type": "read.receipt",
  "data": {
    "message_id": "uuid",
    "read_at": "2024-01-01T12:05:00Z"
  },
  "timestamp": "2024-01-01T12:05:00Z"
}
```

---

## Connection Management

### Reconnection Strategy

Implement exponential backoff for reconnections:

```javascript
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const baseDelay = 1000; // 1 second

function connect() {
  const socket = new WebSocket(url);
  
  socket.onclose = (event) => {
    if (reconnectAttempts < maxReconnectAttempts) {
      const delay = baseDelay * Math.pow(2, reconnectAttempts);
      setTimeout(() => {
        reconnectAttempts++;
        connect();
      }, delay);
    }
  };
  
  socket.onopen = () => {
    reconnectAttempts = 0; // Reset on successful connection
  };
}
```

### Heartbeat/Ping-Pong

Server sends ping every 30 seconds. Client should respond with pong:

```javascript
socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'ping') {
    socket.send(JSON.stringify({ type: 'pong' }));
  }
};
```

### Connection Limits

- Maximum 10 concurrent connections per user
- Idle connections closed after 5 minutes
- Rate limit: 100 messages per minute per connection

## Error Codes

WebSocket close codes:

| Code | Description |
|------|-------------|
| 1000 | Normal closure |
| 1001 | Going away (client navigating away) |
| 1002 | Protocol error |
| 1003 | Unsupported data |
| 4001 | Authentication failed |
| 4002 | Invalid chatroom/match |
| 4003 | Permission denied |
| 4004 | Rate limit exceeded |
| 4005 | Connection limit exceeded |

## Rate Limiting

WebSocket connections are rate limited:

- **Messages**: 100 per minute per connection
- **Typing indicators**: 10 per minute
- **Reactions**: 50 per minute

Exceeding limits results in:
1. Warning message
2. Temporary throttling
3. Connection closure (if persistent)

## Best Practices

### 1. Connection Management

```javascript
class WebSocketManager {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.messageQueue = [];
  }
  
  connect() {
    this.socket = new WebSocket(this.url);
    this.socket.onopen = () => this.onOpen();
    this.socket.onmessage = (e) => this.onMessage(e);
    this.socket.onerror = (e) => this.onError(e);
    this.socket.onclose = (e) => this.onClose(e);
  }
  
  send(message) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }
  
  onOpen() {
    // Flush queued messages
    while (this.messageQueue.length > 0) {
      this.send(this.messageQueue.shift());
    }
  }
}
```

### 2. Typing Indicators

Debounce typing indicators to reduce server load:

```javascript
let typingTimeout;

function handleTyping() {
  // Send typing.start
  socket.send(JSON.stringify({ type: 'typing.start' }));
  
  // Clear existing timeout
  clearTimeout(typingTimeout);
  
  // Set timeout to send typing.stop
  typingTimeout = setTimeout(() => {
    socket.send(JSON.stringify({ type: 'typing.stop' }));
  }, 3000);
}
```

### 3. Message Deduplication

Handle duplicate messages on reconnection:

```javascript
const receivedMessages = new Set();

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'message.receive') {
    if (receivedMessages.has(message.data.id)) {
      return; // Duplicate, ignore
    }
    receivedMessages.add(message.data.id);
    // Process message
  }
};
```

### 4. Optimistic Updates

Update UI immediately, rollback on error:

```javascript
function sendMessage(content) {
  const tempId = `temp-${Date.now()}`;
  
  // Add to UI immediately
  addMessageToUI({ id: tempId, content, pending: true });
  
  // Send to server
  socket.send(JSON.stringify({
    type: 'message.send',
    data: { content, tempId }
  }));
}

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'message.receive') {
    // Replace temp message with real one
    replaceMessageInUI(message.data.tempId, message.data);
  }
};
```

### 5. Error Handling

```javascript
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Show user-friendly error message
  showNotification('Connection error. Retrying...');
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'error') {
    // Handle specific errors
    switch (message.data.code) {
      case 'RATE_LIMIT_EXCEEDED':
        showNotification('Sending too fast. Please slow down.');
        break;
      case 'INVALID_MESSAGE':
        showNotification('Message could not be sent.');
        break;
      default:
        showNotification('An error occurred.');
    }
  }
};
```

## Testing WebSockets

### Manual Testing

Use browser console or tools like `wscat`:

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c "ws://localhost:8000/ws/chat/uuid/?token=your-jwt-token"

# Send message
> {"type": "message.send", "data": {"content": "Hello!"}}
```

### Automated Testing

Example using Python:

```python
import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://localhost:8000/ws/chat/uuid/?token=token"
    
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "message.send",
            "data": {"content": "Test message"}
        }))
        
        # Receive response
        response = await websocket.recv()
        message = json.loads(response)
        print(f"Received: {message}")

asyncio.run(test_chat())
```

## Security Considerations

### 1. Authentication

- Always validate JWT tokens on connection
- Reject connections with invalid/expired tokens
- Use secure WebSocket (WSS) in production

### 2. Authorization

- Verify user has access to chatroom/match
- Validate message ownership for edit/delete
- Check permissions for admin actions

### 3. Input Validation

- Validate all incoming message payloads
- Sanitize user content
- Enforce message length limits

### 4. Rate Limiting

- Implement per-user rate limits
- Track message frequency
- Temporarily ban abusive users

### 5. Data Privacy

- Never expose email or real names
- Use anonymous UUIDs only
- Filter sensitive data from broadcasts

## Monitoring

### Metrics to Track

- Active connections count
- Messages per second
- Average message latency
- Connection errors
- Reconnection rate
- Rate limit violations

### Logging

Log important events:
- Connection established/closed
- Authentication failures
- Rate limit violations
- Errors and exceptions

Example log format:
```
[2024-01-01 12:00:00] INFO: WebSocket connected - user: uuid, chatroom: uuid
[2024-01-01 12:00:05] WARNING: Rate limit exceeded - user: uuid
[2024-01-01 12:00:10] ERROR: Message send failed - user: uuid, error: Invalid content
```

## Troubleshooting

### Connection Issues

**Problem**: WebSocket won't connect

**Solutions**:
- Check JWT token is valid and not expired
- Verify WebSocket URL is correct
- Check CORS settings
- Ensure Redis is running
- Check firewall/proxy settings

### Message Not Received

**Problem**: Messages sent but not received by others

**Solutions**:
- Check connection is still open
- Verify message format is correct
- Check server logs for errors
- Ensure user has permission to send
- Check rate limits not exceeded

### Frequent Disconnections

**Problem**: WebSocket keeps disconnecting

**Solutions**:
- Implement proper reconnection logic
- Check network stability
- Verify server resources (memory, CPU)
- Check Redis connection
- Review server logs for errors

## Support

For WebSocket issues:
- Check this documentation
- Review browser console for errors
- Check server logs
- Test with wscat or similar tool
- Open an issue on GitHub
