# Admin Dashboard API

This module provides administrative endpoints for managing the Ano platform. All endpoints require admin/staff authentication and use anonymous identifiers to maintain user privacy.

## Features

- **Reports Management**: View and update user reports
- **User Moderation**: View user details and ban users (using anonymous IDs only)
- **Broadcast Messages**: Send system messages to chatrooms
- **Platform Metrics**: Monitor platform health and activity

## API Endpoints

### Reports Management

#### List Reports
```
GET /api/admin/reports/
```

Query parameters:
- `status`: Filter by status (pending, reviewed, resolved)
- `ordering`: Order by field (created_at, -created_at)
- `page`: Page number
- `page_size`: Results per page (max 100)

Response:
```json
{
  "count": 10,
  "next": "http://...",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "reporter_anonymous_id": "uuid",
      "reported_anonymous_id": "uuid",
      "reason": "harassment",
      "description": "...",
      "status": "pending",
      "created_at": "2024-01-01T00:00:00Z",
      "reviewed_by_email": null,
      "reviewed_at": null
    }
  ]
}
```

#### Update Report Status
```
PUT /api/admin/reports/{report_id}/
PATCH /api/admin/reports/{report_id}/
```

Request body:
```json
{
  "status": "reviewed"
}
```

Response:
```json
{
  "id": "uuid",
  "reporter_anonymous_id": "uuid",
  "reported_anonymous_id": "uuid",
  "reason": "harassment",
  "description": "...",
  "status": "reviewed",
  "created_at": "2024-01-01T00:00:00Z",
  "reviewed_by_email": "admin@iiti.ac.in",
  "reviewed_at": "2024-01-02T00:00:00Z"
}
```

### User Moderation

#### Get User Details
```
GET /api/admin/users/{anonymous_id}/
```

Response:
```json
{
  "anonymous_id": "uuid",
  "age": 20,
  "interests": ["coding", "music"],
  "hobbies": ["reading"],
  "relationship_intent": "friendship",
  "personality_tags": ["introverted"],
  "bio": "...",
  "reports_received_count": 2,
  "reports_made_count": 0,
  "messages_sent_count": 150,
  "matches_count": 5,
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T00:00:00Z"
}
```

#### Ban User
```
POST /api/admin/users/{anonymous_id}/ban/
```

Request body:
```json
{
  "reason": "Violation of terms of service"
}
```

Response:
```json
{
  "message": "User banned successfully",
  "anonymous_id": "uuid",
  "reason": "Violation of terms of service"
}
```

### Broadcast Messages

#### Send Broadcast Message
```
POST /api/admin/broadcast/
```

Request body (all chatrooms):
```json
{
  "content": "Important platform announcement"
}
```

Request body (specific chatroom):
```json
{
  "content": "Chatroom-specific announcement",
  "chatroom_id": "uuid"
}
```

Response:
```json
{
  "message": "Broadcast sent successfully",
  "chatrooms_count": 5,
  "message_ids": ["uuid1", "uuid2", "..."]
}
```

### Platform Metrics

#### Get Platform Metrics
```
GET /api/admin/metrics/
```

Response:
```json
{
  "active_users_today": 150,
  "active_users_week": 450,
  "total_users": 1000,
  "total_profiles": 950,
  "total_messages_today": 5000,
  "total_messages_week": 35000,
  "total_messages": 100000,
  "total_matches": 2500,
  "total_reports_pending": 10,
  "total_reports": 50,
  "total_chatrooms": 15
}
```

## Authentication

All endpoints require:
1. Valid JWT access token in Authorization header
2. User must have `is_staff=True` or `is_superuser=True`

Example:
```
Authorization: Bearer <access_token>
```

## Privacy & Anonymity

All admin endpoints are designed to maintain user anonymity:
- User details are accessed via anonymous UUID, not email
- API responses never include email addresses or real names
- Only anonymous identifiers are exposed in all responses
- Admin actions are logged with anonymous identifiers

## Testing

Run tests:
```bash
python manage.py test admin_dashboard
```

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 6.1**: Admin broadcast messages are marked with admin designation
- **Requirement 6.2**: Auto-moderation flagging (handled by reports system)
- **Requirement 6.3**: Multiple reports trigger admin notifications
- **Requirement 15.1**: Admin dashboard displays reports with anonymous IDs
- **Requirement 15.2**: Report review maintains anonymity
- **Requirement 15.3**: Admin actions are recorded
- **Requirement 15.4**: Platform metrics are calculated and displayed
