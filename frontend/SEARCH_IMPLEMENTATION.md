# Search Functionality - Frontend Implementation

## Overview

The search functionality provides a user-friendly interface for searching messages across all accessible chats in the Ano platform.

## Components

### SearchBar

**Location:** `src/components/chat/SearchBar.tsx`

A focused search input component with the following features:
- Search icon for visual clarity
- Auto-focus on mount for immediate typing
- Clear button to reset search
- Form submission on Enter key

**Props:**
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  onClose?: () => void;
  placeholder?: string;
}
```

**Usage:**
```tsx
<SearchBar
  onSearch={handleSearch}
  onClose={handleClose}
  placeholder="Search messages..."
/>
```

### SearchResults

**Location:** `src/components/chat/SearchResults.tsx`

Displays search results with highlighting and metadata.

**Features:**
- Highlighted search terms using `<mark>` tags
- Message context (chatroom name or "Match Chat")
- Sender anonymous ID badge
- Relative timestamps (e.g., "2h ago")
- Pinned message indicator
- Click to navigate to message
- Empty states for no query and no results
- Loading state with spinner

**Props:**
```typescript
interface SearchResultsProps {
  query: string;
  results: SearchResult[];
  count: number;
  loading?: boolean;
  onResultClick?: (result: SearchResult) => void;
}
```

**SearchResult Type:**
```typescript
interface SearchResult {
  id: string;
  chatroom: string | null;
  chatroom_name: string | null;
  match_id: string | null;
  sender_id: string;
  content: string;
  highlighted_content: string;
  message_type: string;
  is_pinned: boolean;
  created_at: string;
}
```

### SearchModal

**Location:** `src/components/chat/SearchModal.tsx`

A full-screen modal that integrates SearchBar and SearchResults.

**Features:**
- Modal overlay with backdrop
- Integrates search bar and results
- Handles API calls to search endpoint
- Loading and error states
- Click outside to close
- Resets state when closed

**Props:**
```typescript
interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Usage:**
```tsx
<SearchModal 
  isOpen={isSearchOpen}
  onClose={() => setIsSearchOpen(false)}
/>
```

## Integration

### ChatPage Integration

The search functionality is integrated into the ChatPage component:

```tsx
const [isSearchOpen, setIsSearchOpen] = useState(false);

// Pass search handler to ChatroomList
<ChatroomList 
  onSelectChatroom={handleSelectChatroom}
  onOpenSearch={() => setIsSearchOpen(true)}
/>

// Render search modal
<SearchModal 
  isOpen={isSearchOpen}
  onClose={() => setIsSearchOpen(false)}
/>
```

### ChatroomList Integration

A search button is added to the chatroom list header:

```tsx
<button 
  onClick={onOpenSearch} 
  className="refresh-button" 
  title="Search messages"
>
  🔍
</button>
```

## API Integration

### Chat API

**Location:** `src/api/chat.ts`

Added `searchMessages` function:

```typescript
searchMessages: async (query: string): Promise<{
  query: string;
  count: number;
  results: SearchResult[];
}> => {
  const response = await axiosInstance.get(`${API_BASE}/search/`, {
    params: { q: query },
  });
  return response.data;
}
```

## Styling

### CSS Classes

**Location:** `src/components/chat/Chat.css`

Key CSS classes:
- `.search-bar` - Search bar container
- `.search-input-container` - Input wrapper with icon
- `.search-input` - Text input field
- `.search-clear-btn` - Clear button
- `.search-results` - Results container
- `.search-result-item` - Individual result card
- `.search-result-content mark` - Highlighted text
- `.search-overlay` - Modal backdrop
- `.search-modal` - Modal container
- `.search-loading` - Loading spinner
- `.search-empty` - Empty state

### Responsive Design

The search interface is fully responsive:
- Mobile: Full-width modal (95% width)
- Tablet/Desktop: Centered modal (max 700px width)
- Touch-friendly result cards
- Optimized font sizes for mobile

## User Experience

### Search Flow

1. User clicks search icon in chatroom list
2. Search modal opens with auto-focused input
3. User types search query
4. User presses Enter or search happens on input
5. Loading spinner shows while searching
6. Results display with highlighting
7. User clicks result to navigate to message
8. Modal closes and chat opens to that message

### Empty States

1. **No Query**: Shows search icon and prompt to enter query
2. **No Results**: Shows "No messages found" with suggestion to try different keywords
3. **Loading**: Shows spinner with "Searching..." text

### Error Handling

- Network errors display error message
- Invalid queries show validation error
- Failed searches allow retry

## Navigation

### Result Click Behavior

When a user clicks a search result:

1. **Chatroom Message**: Navigate to `/chat/{chatroomId}` with message ID in state
2. **Match Message**: Navigate to `/matchmaking` with match ID and message ID in state
3. Modal closes automatically

Future enhancement: Scroll to and highlight the specific message.

## Performance

### Optimizations

1. **Debouncing**: Can add debounced search for real-time results
2. **Result Limit**: Backend limits to 50 results
3. **Lazy Loading**: Results render efficiently with React
4. **Modal Unmounting**: State resets when modal closes

## Accessibility

1. **Keyboard Navigation**: Enter to search, Escape to close (future)
2. **ARIA Labels**: Buttons have descriptive labels
3. **Focus Management**: Auto-focus on search input
4. **Screen Reader Support**: Semantic HTML structure

## Testing

### Manual Testing Checklist

- [ ] Search button appears in chatroom list
- [ ] Clicking search button opens modal
- [ ] Search input is auto-focused
- [ ] Typing and pressing Enter performs search
- [ ] Results display with highlighting
- [ ] Clicking result navigates to message
- [ ] Clear button resets search
- [ ] Clicking outside modal closes it
- [ ] Empty states display correctly
- [ ] Loading state shows during search
- [ ] Error messages display on failure
- [ ] Mobile responsive layout works
- [ ] Search works for chatroom messages
- [ ] Search works for match messages
- [ ] Search respects access scope

## Future Enhancements

### Planned Features

1. **Keyboard Shortcuts**
   - Cmd/Ctrl+K to open search
   - Escape to close
   - Arrow keys to navigate results
   - Enter to select result

2. **Advanced Filters**
   - Filter by chatroom
   - Filter by date range
   - Filter by sender
   - Filter by message type

3. **Search History**
   - Recent searches dropdown
   - Clear history option
   - Search suggestions

4. **Real-time Search**
   - Debounced search as you type
   - Cancel previous requests
   - Show partial results

5. **Message Preview**
   - Hover to see more context
   - Show surrounding messages
   - Preview media attachments

6. **Search Analytics**
   - Track search usage
   - Popular search terms
   - Search success rate

## Requirements Validation

✅ **Requirement 10.1**: Search through all accessible messages
✅ **Requirement 10.2**: Highlight matching text in results
✅ **Requirement 10.3**: Navigate to message in chat history
✅ **Requirement 10.4**: Only search accessible chats

## Component Exports

All search components are exported from `src/components/chat/index.ts`:

```typescript
export { default as SearchBar } from './SearchBar';
export { default as SearchResults } from './SearchResults';
export { default as SearchModal } from './SearchModal';
```

## Dependencies

- React 18+
- React Router v6 (for navigation)
- Axios (for API calls)
- CSS (no external UI libraries)

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android
