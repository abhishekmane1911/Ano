# Admin Dashboard

The admin dashboard provides comprehensive tools for platform moderation, monitoring, and communication.

## Components

### AdminDashboard
Main dashboard component with tabbed interface for accessing different admin functions.

**Features:**
- Reports management
- Platform metrics monitoring
- Broadcast messaging

### ReportsList
Displays all user reports with filtering and pagination.

**Features:**
- Filter by status (pending, reviewed, resolved)
- Pagination support
- Real-time report selection
- Status badges for quick identification

### ReportDetail
Shows detailed information about a selected report.

**Features:**
- Full report information display
- Status update controls
- User details expansion
- Reviewer tracking

### UserModerationPanel
Displays user profile and activity statistics for moderation purposes.

**Features:**
- Anonymous profile information
- Activity statistics (reports, messages, matches)
- Account information
- User ban functionality with reason tracking

**Privacy:**
- Only displays anonymous IDs
- No email or real name exposure
- Maintains platform anonymity principles

### BroadcastMessageForm
Allows admins to send messages to chatrooms.

**Features:**
- Send to all chatrooms or specific chatroom
- Character count (max 1000)
- Message preview
- Success/error feedback

**Message Format:**
- Messages are prefixed with [ADMIN BROADCAST]
- Sent as system messages
- Visible to all chatroom participants

### PlatformMetrics
Displays comprehensive platform health and usage statistics.

**Metrics Tracked:**
- User activity (today, week, total)
- Message volume (today, week, total)
- Match statistics
- Report statistics
- Chatroom count

**Features:**
- Auto-refresh capability
- Last update timestamp
- Calculated summary statistics
- Visual metric cards

## API Integration

All components use the `adminAPI` client from `src/api/admin.ts`:

```typescript
import { adminAPI } from '../../api/admin';

// List reports
const reports = await adminAPI.listReports(status, ordering, page);

// Update report
const updated = await adminAPI.updateReport(reportId, { status });

// Get user details
const user = await adminAPI.getUserDetail(anonymousId);

// Ban user
await adminAPI.banUser(anonymousId, { reason });

// Broadcast message
await adminAPI.broadcastMessage({ content, chatroom_id });

// Get metrics
const metrics = await adminAPI.getPlatformMetrics();
```

## Route Protection

The admin dashboard is protected by the `AdminRoute` component in `App.tsx`:

```typescript
<Route
  path="/admin"
  element={
    <AdminRoute>
      <AdminDashboard />
    </AdminRoute>
  }
/>
```

**Access Requirements:**
- User must be authenticated
- User must have `isAdmin: true` in their profile
- Non-admin users are redirected to home page

## Styling

All admin components use styles from `Admin.css`:

**Design Principles:**
- Clean, professional interface
- Color-coded status indicators
- Responsive grid layouts
- Accessible form controls
- Clear visual hierarchy

**Status Colors:**
- Pending: Yellow
- Reviewed: Blue
- Resolved: Green
- Harassment: Red
- Spam: Yellow
- Inappropriate: Pink

## Usage

### Accessing the Dashboard

1. Log in as an admin user
2. Navigate to `/admin`
3. Use tabs to switch between functions

### Managing Reports

1. Go to Reports tab
2. Filter by status if needed
3. Click on a report to view details
4. Update status as needed
5. View user details for context
6. Take moderation action if required

### Monitoring Platform

1. Go to Platform Metrics tab
2. Review current statistics
3. Click Refresh to update data
4. Monitor pending reports count
5. Track user engagement trends

### Broadcasting Messages

1. Go to Broadcast Message tab
2. Enter message content
3. Optionally specify chatroom ID
4. Click Send Broadcast
5. Confirm success message

## Requirements Validation

This implementation satisfies:

- **Requirement 6.1**: Admin broadcast messages with designation
- **Requirement 15.1**: Anonymous admin dashboard display
- **Requirement 15.2**: Report context without revealing identities
- **Requirement 15.3**: Report action recording
- **Requirement 15.4**: Platform health metrics display

## Security Considerations

- All API calls require admin authentication
- Only anonymous IDs are displayed
- No email or real name exposure
- Ban actions are logged with reasons
- Report updates track reviewer information
