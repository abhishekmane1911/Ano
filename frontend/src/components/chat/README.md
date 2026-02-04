# Chat Components

This directory contains all the frontend components for the anonymous chat functionality.

## Components

### ChatPage
Main page component that combines ChatroomList and ChatWindow. Handles chatroom selection and routing.

### ChatroomList
Displays a list of available chatrooms with:
- Chatroom name and description
- Member count
- Unread message badges
- Refresh functionality

### ChatWindow
Main chat interface with:
- Real-time message display
- Infinite scroll for loading older messages
- Message sending via WebSocket
- Optimistic UI updates
- Connection status indicator
- Pinned messages section

### MessageBubble
Individual message component with:
- Sender identification (anonymous ID)
- Timestamp display
- Edit/delete actions (for own messages)
- Reaction support
- Pin/unpin functionality
- Media display (images, voice notes)
- Edited indicator

### MessageInput
Message composition component with:
- Text input with auto-resize
- Emoji picker integration
- Typing indicator triggers
- Send button
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)

### MessageReactions
Displays emoji reactions on messages with:
- Reaction count per emoji
- Click to add same reaction
- Grouped display

### TypingIndicator
Shows when other users are typing with:
- Animated dots
- Multiple user support
- Auto-cleanup of stale indicators

### PinnedMessages
Collapsible section showing pinned messages with:
- Message preview
- Click to navigate to message
- Unpin functionality

### MediaViewer
Full-screen media viewer with:
- Image/video display
- Zoom support
- Download option
- Keyboard shortcuts (Escape to close)

## WebSocket Service

The `websocket.ts` service handles:
- WebSocket connection management
- Automatic reconnection with exponential backoff
- Event handling for all chat events
- Heartbeat to keep connection alive
- Rate limiting awareness

## State Management

Chat state is managed using Zustand in `chatStore.ts`:
- Chatrooms list
- Messages per chatroom
- Typing users
- Online users
- WebSocket connection status
- Unread counts

## API Integration

The `chat.ts` API module provides:
- REST API calls for chatroom operations
- Message CRUD operations
- Media upload
- Pagination support

## Usage

```tsx
import { ChatPage } from './components/chat';

// In your router
<Route path="/chat" element={<ChatPage />} />
```

## Features Implemented

✅ Real-time messaging via WebSocket
✅ Infinite scroll for message history
✅ Optimistic UI updates
✅ Typing indicators
✅ Message reactions
✅ Message editing and deletion
✅ Message pinning
✅ Read receipts
✅ Online presence
✅ Automatic reconnection
✅ Unread message counts
✅ Media viewer
✅ Emoji picker
✅ Anonymous user identification

## Requirements Validated

- **4.1**: Anonymous chatroom display ✅
- **4.2**: Real-time message broadcasting ✅
- **4.3**: Media compression (backend) ✅
- **4.4**: Message mutation broadcasting ✅
- **4.5**: Message pinning ✅
- **5.1**: Typing indicators ✅
- **5.2**: Read receipts ✅
- **5.3**: Anonymous presence updates ✅
- **5.4**: Message reactions ✅
- **5.5**: Paginated message loading ✅
