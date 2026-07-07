# AI Moderation System Implementation

## Overview

This implementation provides a comprehensive AI-powered content moderation system with heat tracking for repeat offenders. The system includes real-time content interception, asynchronous processing, and escalating penalties.

## Components Implemented

### 1. Models (`models.py`)
- **ModerationResult**: Stores AI moderation results for each message
- **ViolationHistory**: Tracks user violations with heat system integration
- **Shadowban**: Manages temporary user restrictions

### 2. AI Moderation Services (`services.py`)

#### OpenAIModerator
- Integrates with OpenAI Moderation API
- Provides detailed toxicity scoring and category detection
- Handles API failures gracefully

#### LocalModerator
- Uses better-profanity and vaderSentiment libraries
- Provides fallback when OpenAI is unavailable
- Includes custom harmful pattern detection

#### ModerationService
- Orchestrates moderation pipeline with fallback logic
- Integrates with heat system for escalating penalties
- Handles violation processing and shadowban application

### 3. Heat System (`services.py` - HeatSystem class)

#### Features
- **6-level heat system**: Clean → Warm → Hot → Burning → Scorching → Inferno
- **Escalating penalties**: Multipliers from 1.0x to 5.0x based on heat level
- **Rehabilitation mechanism**: Reduces heat level after good behavior
- **Comprehensive tracking**: Violation history and progression monitoring

#### Heat Levels
- **Level 0 (Clean)**: No violations, 1.0x penalty multiplier
- **Level 1 (Warm)**: 1 violation, 1.2x penalty multiplier
- **Level 2 (Hot)**: 3 violations, 1.5x penalty multiplier
- **Level 3 (Burning)**: 5 violations, 2.0x penalty multiplier
- **Level 4 (Scorching)**: 8 violations, 3.0x penalty multiplier
- **Level 5 (Inferno)**: 8+ violations, 5.0x penalty multiplier

### 4. Middleware (`middleware.py`)

#### AIModerationMiddleware
- **Real-time interception**: Processes content before database save
- **Quick toxicity check**: Immediate rejection for severe violations
- **Asynchronous queuing**: Detailed moderation happens in background
- **Penalty application**: Immediate shadowbans for high toxicity content

### 5. API Endpoints (`views.py`, `urls.py`)

#### Available Endpoints
- `GET /api/moderation/api/` - Get comprehensive moderation status
- `GET /api/moderation/api/heat/` - Get heat system information
- `POST /api/moderation/api/heat/` - Attempt rehabilitation
- `POST /api/moderation/api/report/` - Report content
- `GET /api/moderation/api/violations/` - Get violation history
- `GET /api/moderation/api/shadowban/status/` - Check shadowban status
- `GET /api/moderation/api/stats/` - Get moderation statistics (admin only)

### 6. Background Tasks (`tasks.py`)

#### Celery Tasks
- **moderate_message_async**: Detailed async moderation
- **cleanup_expired_shadowbans**: Remove expired restrictions
- **update_user_heat_scores**: Process rehabilitation and decay
- **process_moderation_queue**: Retry failed moderation attempts
- **generate_heat_report**: Generate monitoring reports

### 7. Serializers (`serializers.py`)
- **ViolationHistorySerializer**: Violation data serialization
- **ShadowbanSerializer**: Shadowban information with time remaining
- **HeatInfoSerializer**: Comprehensive heat system data
- **ReportContentSerializer**: Content reporting validation

## Configuration

### Environment Variables
Add to `.env`:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### Dependencies
Added to `requirements.txt`:
```
openai==1.58.1
better-profanity==0.7.0
vaderSentiment==3.3.2
```

### Middleware Configuration
Added to `settings.py` MIDDLEWARE:
```python
"moderation.middleware.AIModerationMiddleware",  # AI content moderation
```

## Usage

### Basic Moderation
```python
from moderation.services import ModerationService
from chat.models import Message

# Moderate a message
message = Message.objects.get(id=123)
result = ModerationService.moderate_content(message)
print(f"Action: {result.action_taken}, Score: {result.toxicity_score}")
```

### Heat System
```python
from moderation.services import HeatSystem
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(id=456)

# Get heat information
heat_info = HeatSystem.get_heat_info(user)
print(f"Heat Level: {heat_info['heat_level']} ({heat_info['heat_name']})")

# Attempt rehabilitation
if HeatSystem.attempt_rehabilitation(user):
    print("User successfully rehabilitated")
```

### Shadowban Check
```python
from moderation.services import ModerationService

# Check if user is shadowbanned
is_banned = ModerationService.is_user_shadowbanned(user)
if is_banned:
    print("User is currently shadowbanned")
```

## Features

### ✅ Implemented
- [x] AI content moderation with OpenAI and local fallback
- [x] Real-time content interception middleware
- [x] 6-level heat system with escalating penalties
- [x] Rehabilitation mechanism for good behavior
- [x] Comprehensive violation tracking
- [x] Shadowban system with automatic expiration
- [x] Asynchronous processing with Celery
- [x] REST API endpoints for all functionality
- [x] Admin statistics and monitoring
- [x] Graceful error handling and fallbacks

### 🔄 Asynchronous Processing
- Content moderation happens in background to maintain UI responsiveness
- Failed moderation attempts are retried automatically
- Heat scores are updated periodically for rehabilitation

### 🛡️ Security Features
- Input sanitization and validation
- Rate limiting integration ready
- Comprehensive logging for audit trails
- Graceful degradation when AI services fail

## Testing

The system includes comprehensive error handling and fallback mechanisms:
- OpenAI API failures fall back to local moderation
- Local library failures default to safe approval
- Database errors are logged but don't break user experience
- Middleware failures allow content through rather than blocking

## Monitoring

The system provides detailed logging and statistics:
- All moderation decisions are logged
- Heat level changes are tracked
- API failures and fallbacks are monitored
- Periodic reports can be generated for analysis

## Next Steps

To complete the implementation:
1. Install required dependencies: `pip install -r requirements.txt`
2. Set up OpenAI API key in environment variables
3. Run migrations: `python manage.py migrate`
4. Start Celery workers for background processing
5. Configure periodic tasks for cleanup and rehabilitation