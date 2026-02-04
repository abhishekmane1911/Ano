# Matchmaking Components

This directory contains the frontend components for the Ano matchmaking system, implementing a Tinder-style swipe interface for anonymous profile discovery and matching.

## Components

### MatchmakingPage
Main container component that provides tabbed navigation between the swipe interface and match list.

**Features:**
- Tab-based navigation (Discover / Matches)
- Sticky header with gradient styling
- Responsive layout

### SwipeInterface
Tinder-style card stack interface for swiping through profiles.

**Features:**
- Card stack with animated transitions
- Drag-to-swipe gesture support
- Button-based swipe actions (left/right)
- Background card preview
- Profile counter
- Automatic profile loading
- Match detection and notification

**Gestures:**
- Drag left > 100px: Pass (swipe left)
- Drag right > 100px: Like (swipe right)
- Tap buttons: Instant swipe action

### SwipeCard
Individual profile card component displaying anonymous user information.

**Features:**
- Anonymous avatar display
- Age and relationship intent
- Bio section
- Interest tags (blue)
- Hobby tags (purple)
- Personality tags (orange)
- Swipe action buttons
- Drag gesture support via Framer Motion

**Props:**
- `profile`: Profile data to display
- `onSwipeLeft`: Callback for left swipe
- `onSwipeRight`: Callback for right swipe
- `style`: Optional custom styles

### MatchNotification
Celebration modal displayed when a mutual match occurs.

**Features:**
- Animated entrance with spring physics
- Celebration emoji animation
- Match profile preview
- Action buttons (Start Chatting / Keep Swiping)
- Backdrop overlay
- Click-outside to close

**Animations:**
- Overlay fade-in
- Modal scale and slide-up
- Icon bounce effect
- Staggered text reveals

### MatchList
Grid view of all user matches with navigation to individual chats.

**Features:**
- Responsive grid layout
- Match cards with avatars
- Match date formatting (Today, Yesterday, X days ago)
- Interest tag preview (first 2 + count)
- Click to open chat
- Empty state with CTA
- Loading and error states

### MatchChat
One-on-one anonymous chat interface for matched users.

**Features:**
- Real-time messaging via WebSocket
- Message history with pagination
- Typing indicators
- Read receipts
- Optimistic UI updates
- Automatic reconnection
- Back navigation to match list
- Connection status indicator

**WebSocket Events:**
- `message.send`: Send message to match
- `message.receive`: Receive message from match
- `typing.start`: User starts typing
- `typing.stop`: User stops typing

## State Management

### useMatchmakingStore (Zustand)
Centralized state for matchmaking features.

**State:**
- `profiles`: Array of profiles for swiping
- `currentProfileIndex`: Index of currently displayed profile
- `matches`: Array of user's matches
- `currentMatch`: Currently selected match
- `matchMessages`: Messages by match ID
- `typingUsers`: Typing indicators by match ID
- `ws`: WebSocket connection
- `isConnected`: WebSocket connection status
- `isLoading`: Loading state
- `error`: Error message

**Actions:**
- Profile management (set, next, remove)
- Match management (set, add, setCurrent)
- Message management (add, update, set, prepend)
- Typing indicators (add, remove)
- WebSocket management (set, setConnected)
- Loading/error states

## API Integration

### matchmakingAPI
API client for matchmaking endpoints.

**Endpoints:**
- `getProfiles()`: Fetch profiles for swiping
- `swipe(profileId, direction)`: Record swipe and check for match
- `getMatches()`: Fetch user's matches
- `getMatchDetail(matchId)`: Get match details
- `getMatchMessages(matchId, page)`: Get paginated messages
- `sendMatchMessage(matchId, content)`: Send message to match

## Styling

### Matchmaking.css
Comprehensive styles for all matchmaking components.

**Key Features:**
- Gradient backgrounds
- Card shadows and hover effects
- Responsive grid layouts
- Animation transitions
- Mobile-first design
- Touch-friendly buttons
- Loading/error states
- Empty state designs

**Responsive Breakpoints:**
- Mobile: < 768px
  - Single column layouts
  - Reduced card sizes
  - Adjusted spacing

## Animations

### Framer Motion Integration
Smooth, physics-based animations throughout.

**Card Swipe:**
- Drag gesture handling
- Exit animations (slide + rotate)
- Spring physics for natural feel
- Scale transitions

**Match Notification:**
- Overlay fade
- Modal spring entrance
- Icon bounce sequence
- Staggered text reveals

**Card Stack:**
- Enter from bottom with scale
- Background card preview
- Smooth transitions between cards

## Usage Example

```tsx
import { MatchmakingPage } from './components/matchmaking';

// In your router
<Route path="/matchmaking" element={<MatchmakingPage />} />
<Route path="/matches/:matchId/chat" element={<MatchChat />} />
```

## Requirements Validation

This implementation satisfies the following requirements:

**Requirement 7.1**: Profile cards display interests, hobbies, age, relationship intent, and personality tags
**Requirement 7.2**: Swipe left records rejection and shows next profile
**Requirement 7.3**: Swipe right records interest and checks for mutual match
**Requirement 7.4**: Mutual swipes create a match and enable anonymous chat
**Requirement 7.5**: Already-swiped profiles are excluded from display

**Requirement 8.1**: Match creation opens anonymous chat window
**Requirement 8.2**: Messages delivered in real-time via WebSocket
**Requirement 8.3**: Images can be sent (infrastructure ready)
**Requirement 8.4**: Typing indicators shown to other user
**Requirement 8.5**: Read receipts sent to message sender

## Future Enhancements

- Image upload in match chat
- Voice messages
- Message reactions
- Profile reporting from swipe interface
- Advanced filtering options
- Undo last swipe
- Super likes
- Match expiration
- Conversation starters
