# Reports and Blocking System

This Django app implements the reports and blocking functionality for the Ano platform, allowing users to report inappropriate behavior and block other users while maintaining complete anonymity.

## Features

- **Report Submission**: Users can report other users with anonymous identifiers
- **Report Escalation**: Automatic admin notification when a user receives multiple reports
- **User Blocking**: Users can block other users to prevent all communication
- **Block Filtering**: Blocked users are automatically filtered from matchmaking and chat
- **Anonymous Operations**: All operations use anonymous UUIDs, never exposing real identities

## Models

### Report Model

Stores reports submitted by users about inappropriate behavior.

**Fields:**
- `id`: UUID primary key
- `reporter`: ForeignKey to Profile (who submitted the report)
- `reported`: ForeignKey to Profile (who is being reported)
- `reason`: Choice field (harassment, spam, inappropriate, other)
- `description`: Text description of the issue
- `status`: Choice field (pending, reviewed, resolved)
- `created_at`: Timestamp of report creation
- `reviewed_by`: ForeignKey to User (admin who reviewed)
- `reviewed_at`: Timestamp of review

### Block Model

Stores blocking relationships between users.

**Fields:**
- `id`: UUID primary key
- `blocker`: ForeignKey to Profile (who initiated the block)
- `blocked`: ForeignKey to Profile (who is being blocked)
- `created_at`: Timestamp of block creation

**Constraints:**
- Unique constraint on (blocker, blocked) to prevent duplicate blocks

## API Endpoints

### Report Endpoints

#### Create Report
```
POST /api/reports/
```

**Request Body:**
```json
{
  "reported_id": "uuid-of-reported-user",
  "reason": "harassment",
  "description": "Detailed description of the issue"
}
```

**Response:**
```json
{
  "id": "report-uuid",
  "reporter_id": "reporter-anonymous-uuid",
  "reason": "harassment",
  "description": "Detailed description",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Features:**
- Automatically escalates to admins if user receives 3+ pending reports
- Prevents self-reporting
- Uses anonymous identifiers only

### Block Endpoints

#### Create Block
```
POST /api/reports/block/
```

**Request Body:**
```json
{
  "blocked_id": "uuid-of-user-to-block"
}
```

**Response:**
```json
{
  "id": "block-uuid",
  "blocker_id": "blocker-anonymous-uuid",
  "blocked_id": "blocked-anonymous-uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### List Blocked Users
```
GET /api/reports/blocked/
```

**Response:**
```json
[
  {
    "id": "block-uuid",
    "anonymous_id": "blocked-user-anonymous-uuid",
    "blocked_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Unblock User
```
DELETE /api/reports/block/{anonymous_id}/
```

**Response:**
```json
{
  "message": "User unblocked successfully"
}
```

## Utility Functions

### `get_blocked_profile_ids(profile)`

Returns a set of profile IDs that are blocked by or have blocked the given profile.

```python
from reports.utils import get_blocked_profile_ids

blocked_ids = get_blocked_profile_ids(user_profile)
```

### `filter_blocked_profiles(queryset, profile)`

Filters a Profile queryset to exclude blocked users.

```python
from reports.utils import filter_blocked_profiles

profiles = Profile.objects.all()
filtered_profiles = filter_blocked_profiles(profiles, user_profile)
```

### `is_blocked(profile1, profile2)`

Checks if either profile has blocked the other (bidirectional check).

```python
from reports.utils import is_blocked

if is_blocked(profile1, profile2):
    # Prevent communication
    pass
```

## Integration with Other Apps

### Matchmaking Integration

The matchmaking app uses `filter_blocked_profiles()` to exclude blocked users from the swipe interface:

```python
from reports.utils import filter_blocked_profiles

profiles = Profile.objects.exclude(id=user_profile.id)
profiles = filter_blocked_profiles(profiles, user_profile)
```

### Match Chat Integration

The match consumer uses `is_blocked()` to prevent blocked users from communicating:

```python
from reports.utils import is_blocked

if is_blocked(profile1, profile2):
    await self.close(code=4004)
    return
```

## Report Escalation

When a user receives 3 or more pending reports, the system automatically:

1. Sends an email notification to all admin users
2. Includes the reported user's anonymous ID
3. Includes the total count of pending reports
4. Directs admins to review in the admin dashboard

**Escalation Threshold:** 3 pending reports (configurable in views.py)

## Admin Interface

The admin interface provides:

- List view of all reports with filtering by status and reason
- Search by anonymous IDs
- Ability to update report status
- List view of all blocks
- Search by blocker/blocked anonymous IDs

## Security & Privacy

- All API responses use anonymous UUIDs only
- No email addresses or real names are exposed
- Admin notifications use anonymous identifiers
- Blocks work bidirectionally (both users can't see each other)
- Self-reporting and self-blocking are prevented

## Testing

Run the test suite:

```bash
python manage.py test reports
```

The test suite includes:
- Model creation and validation tests
- API endpoint tests (authenticated and unauthenticated)
- Utility function tests
- Block filtering tests
- Report escalation tests

## Requirements Validation

This implementation satisfies the following requirements:

- **9.1**: Anonymous report creation with anonymous IDs
- **9.2**: Block communication prevention
- **9.3**: Anonymous admin notifications
- **9.4**: Blocked profile filtering from matchmaking
- **9.5**: Report escalation for multiple reports
