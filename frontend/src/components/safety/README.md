# Safety Components

This directory contains components for reporting and blocking users to maintain a safe community.

## Components

### ReportModal
A modal dialog for reporting users with inappropriate behavior.

**Features:**
- Multiple report reason options (harassment, spam, inappropriate content, other)
- Required description field with character counter
- Anonymous reporting (uses anonymous IDs)
- Success confirmation message
- Error handling

**Props:**
- `reportedUserId`: Anonymous ID of the user being reported
- `reportedUserName`: Display name (defaults to "Anonymous User")
- `onClose`: Callback when modal is closed
- `onSuccess`: Optional callback when report is successfully submitted

**Usage:**
```tsx
<ReportModal
  reportedUserId="user-uuid"
  reportedUserName="Anonymous User"
  onClose={() => setShowModal(false)}
  onSuccess={() => console.log('Report submitted')}
/>
```

### BlockConfirmation
A confirmation dialog for blocking users.

**Features:**
- Clear explanation of blocking consequences
- Confirmation required before blocking
- Success confirmation message
- Error handling

**Props:**
- `blockedUserId`: Anonymous ID of the user being blocked
- `blockedUserName`: Display name (defaults to "Anonymous User")
- `onClose`: Callback when modal is closed
- `onSuccess`: Optional callback when user is successfully blocked

**Usage:**
```tsx
<BlockConfirmation
  blockedUserId="user-uuid"
  blockedUserName="Anonymous User"
  onClose={() => setShowModal(false)}
  onSuccess={() => navigate('/matchmaking')}
/>
```

### SafetySettings
A full page component for managing blocked users and viewing privacy tips.

**Features:**
- List of all blocked users
- Unblock functionality
- Privacy and safety tips
- Empty state when no users are blocked

**Usage:**
```tsx
<Route path="/safety" element={<SafetySettings />} />
```

## Integration Points

### Chat Components
Report and block buttons are integrated into:
- **ChatWindow**: Buttons appear in message actions for other users' messages
- **MessageBubble**: Report (🚩) and Block (🚫) buttons in message action menu

### Matchmaking Components
Report and block buttons are integrated into:
- **SwipeCard**: Safety action buttons at the bottom of profile cards
- **MatchChat**: Header action buttons for reporting/blocking match

## API Integration

All components use the `reportsAPI` from `src/api/reports.ts`:

```typescript
// Create a report
await reportsAPI.createReport({
  reported_id: 'user-uuid',
  reason: 'harassment',
  description: 'Description of the issue'
});

// Block a user
await reportsAPI.blockUser({
  blocked_id: 'user-uuid'
});

// Get blocked users
const blockedUsers = await reportsAPI.getBlockedUsers();

// Unblock a user
await reportsAPI.unblockUser('user-uuid');
```

## Styling

All components use `Safety.css` which includes:
- Modal backdrop and content styles
- Form elements (radio buttons, textarea)
- Success/error message styles
- Responsive design for mobile devices
- Smooth animations and transitions

## Requirements Validation

This implementation satisfies the following requirements:

**Requirement 9.1**: Anonymous report creation
- Reports use anonymous IDs only
- No personal information exposed

**Requirement 9.2**: Block communication prevention
- Blocked users cannot send messages
- Blocked profiles hidden from matchmaking

**Requirement 9.3**: Anonymous admin notifications
- Reports sent to admins with anonymous IDs only
- Backend handles escalation notifications

**Requirement 9.4**: Blocked profile filtering
- Blocked users excluded from matchmaking
- Backend filters blocked users from results

## User Experience

### Report Flow
1. User clicks report button (🚩)
2. Modal opens with reason selection
3. User selects reason and provides description
4. Report submitted to backend
5. Success message displayed
6. Modal closes automatically

### Block Flow
1. User clicks block button (🚫)
2. Confirmation modal shows consequences
3. User confirms block action
4. Block created in backend
5. Success message displayed
6. User redirected or modal closes

### Safety Settings
1. User navigates to /safety route
2. View list of blocked users
3. Unblock users with confirmation
4. View privacy and safety tips

## Accessibility

- All buttons have proper `title` attributes
- Modal can be closed with backdrop click
- Keyboard navigation supported
- Clear visual feedback for all actions
- Error messages are descriptive

## Future Enhancements

Potential improvements:
- Add report history for users
- Implement temporary mute functionality
- Add more granular blocking options
- Include report status tracking
- Add appeal process for blocked users
