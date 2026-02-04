# Search Functionality - User Guide

## How to Use the Search Feature

### Opening Search

1. Navigate to the Chat page
2. Look for the search icon (🔍) in the chatroom list header
3. Click the search icon to open the search modal

### Searching for Messages

1. The search input will be automatically focused
2. Type your search query (e.g., "python", "meeting", "hello")
3. Press Enter or wait for the search to execute
4. Results will appear below the search bar

### Understanding Search Results

Each search result shows:
- **Location**: The chatroom name or "Match Chat"
- **Time**: When the message was sent (e.g., "2h ago")
- **Sender**: The anonymous ID of the sender (first 8 characters)
- **Content**: The message text with your search term highlighted in yellow
- **Pin indicator**: 📌 if the message is pinned

### Navigating to Messages

1. Click on any search result
2. The app will navigate to the chat containing that message
3. The search modal will close automatically

### Clearing Search

- Click the X button in the search bar to clear your query
- Click outside the modal to close it
- The search state will reset when you close the modal

### Search Scope

The search will find messages in:
- ✅ All public chatrooms
- ✅ Your match chats (one-on-one conversations)

The search will NOT find messages in:
- ❌ Other users' private match chats
- ❌ Deleted messages

### Tips for Better Searches

1. **Use specific keywords**: "python programming" is better than just "p"
2. **Try different terms**: If you don't find what you're looking for, try synonyms
3. **Check spelling**: The search is case-insensitive but spelling matters
4. **Use multiple words**: You can search for phrases like "machine learning"

### Search Limitations

- Maximum 50 results per search
- Results are ordered by relevance
- Only searches message text content (not media captions yet)
- Requires at least one character to search

### Empty States

**No Query Entered**
- You'll see a search icon and prompt: "Enter a search query to find messages"

**No Results Found**
- You'll see: "No messages found for '[your query]'"
- Suggestion: "Try different keywords"

**Loading**
- You'll see a spinner and "Searching..." while the search is in progress

### Keyboard Shortcuts (Future)

Coming soon:
- `Cmd/Ctrl + K`: Open search
- `Escape`: Close search modal
- `Arrow keys`: Navigate results
- `Enter`: Open selected result

### Mobile Usage

On mobile devices:
- Tap the search icon (🔍) to open search
- The keyboard will appear automatically
- Tap a result to navigate
- Tap outside the modal to close

### Troubleshooting

**Search not working?**
- Make sure you're logged in
- Check your internet connection
- Try refreshing the page

**Not finding expected messages?**
- Verify you have access to the chat
- Check if the message was deleted
- Try different search terms

**Search is slow?**
- This is normal for very large message histories
- Results are limited to 50 for performance

### Privacy & Security

- Search only shows messages you have access to
- Your search queries are not stored
- Results use anonymous identifiers (no real names)
- Search respects all privacy settings

### Examples

**Good searches:**
- "python" - finds all messages mentioning Python
- "meeting tomorrow" - finds messages about meetings
- "project deadline" - finds project-related messages
- "hello everyone" - finds greetings

**Less effective searches:**
- "a" - too short, too many results
- "asdfghjkl" - random characters won't match anything
- "" - empty search is not allowed

### Getting Help

If you encounter issues with search:
1. Try refreshing the page
2. Clear your browser cache
3. Check the browser console for errors
4. Contact support with details about the issue

## Technical Details (For Developers)

### Search Algorithm

- Uses PostgreSQL full-text search
- GIN index for performance
- Results ranked by relevance
- Case-insensitive matching

### API Endpoint

```
GET /api/chat/search/?q=<query>
```

### Response Format

```json
{
  "query": "python",
  "count": 2,
  "results": [
    {
      "id": "uuid",
      "chatroom_name": "General Chat",
      "sender_id": "uuid",
      "content": "I love Python",
      "highlighted_content": "I love <mark>Python</mark>",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Performance

- Searches are fast even with thousands of messages
- Results limited to 50 for optimal performance
- Database indexes ensure quick lookups

### Future Enhancements

Planned improvements:
- Advanced filters (date, chatroom, sender)
- Search history and suggestions
- Real-time search as you type
- Search in media captions
- Export search results
