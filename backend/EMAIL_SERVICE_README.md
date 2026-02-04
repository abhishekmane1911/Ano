# Email Service Implementation

This document describes the email service implementation for the Ano platform, including verification emails and password reset functionality.

## Overview

The email service uses Django's email backend with Celery for asynchronous email sending. This ensures that email operations don't block API responses and provides retry capabilities for failed deliveries.

## Features

- ✅ **Async Email Sending**: Uses Celery tasks for non-blocking email delivery
- ✅ **Email Verification**: Sends verification links to new users
- ✅ **Password Reset**: Sends secure password reset links
- ✅ **HTML Email Templates**: Professional, responsive email templates
- ✅ **Retry Logic**: Automatic retry on email delivery failures (max 3 attempts)
- ✅ **Token Expiry**: Security tokens expire after set time periods
- ✅ **Anonymous Logging**: All email operations logged with anonymous identifiers

## Architecture

### Components

1. **Celery Tasks** (`authentication/tasks.py`)
   - `send_verification_email`: Sends email verification link
   - `send_password_reset_email`: Sends password reset link

2. **Email Templates** (`authentication/templates/authentication/`)
   - `verification_email.html`: Verification email template
   - `password_reset_email.html`: Password reset email template

3. **API Endpoints**
   - `POST /api/auth/register/`: Triggers verification email
   - `POST /api/auth/password-reset/`: Requests password reset
   - `POST /api/auth/password-reset-confirm/`: Confirms password reset

4. **User Model Extensions** (`authentication/models.py`)
   - `password_reset_token`: UUID token for password reset
   - `password_reset_token_created`: Timestamp for token expiry
   - `generate_password_reset_token()`: Creates new reset token
   - `is_password_reset_token_valid()`: Checks token validity (1 hour)
   - `clear_password_reset_token()`: Clears token after use

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:5173
```

### Development vs Production

**Development** (default):
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails are printed to console for testing.

**Production**:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```
Emails are sent via SMTP server.

### Gmail Configuration

If using Gmail:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password at: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password) in `EMAIL_HOST_PASSWORD`

## Email Flows

### 1. Email Verification Flow

```
User Registration
    ↓
User Created (inactive)
    ↓
Celery Task Queued
    ↓
Verification Email Sent
    ↓
User Clicks Link
    ↓
Account Activated
```

**API Endpoints:**
- `POST /api/auth/register/` - Creates user and queues verification email
- `POST /api/auth/verify-email/` - Verifies token and activates account

**Token Expiry:** 24 hours (recommended, not enforced in current implementation)

### 2. Password Reset Flow

```
User Requests Reset
    ↓
Token Generated
    ↓
Celery Task Queued
    ↓
Reset Email Sent
    ↓
User Clicks Link
    ↓
User Sets New Password
    ↓
Token Cleared
```

**API Endpoints:**
- `POST /api/auth/password-reset/` - Generates token and queues email
- `POST /api/auth/password-reset-confirm/` - Validates token and updates password

**Token Expiry:** 1 hour

## Email Templates

### Verification Email

**Subject:** Verify your Ano account

**Content:**
- Welcome message
- Verification button with link
- Plain text link as fallback
- Security notice about expiry
- Branding and footer

### Password Reset Email

**Subject:** Reset your Ano password

**Content:**
- Reset request confirmation
- Reset button with link
- Plain text link as fallback
- Security warning (1 hour expiry)
- Advice to ignore if not requested
- Branding and footer

## Celery Configuration

### Starting Celery Worker

Development:
```bash
cd backend
celery -A ano_backend worker --loglevel=info
```

Production (with multiple workers):
```bash
celery -A ano_backend worker --loglevel=info --concurrency=4
```

### Monitoring Tasks

Check Celery logs for email delivery status:
```bash
[2025-12-03 08:10:49] INFO ano_platform - Verification email sent successfully to user_xxx
[2025-12-03 08:10:49] INFO ano_platform - Password reset email sent successfully to user_xxx
```

## Testing

### Unit Tests

Run email service tests:
```bash
python manage.py test authentication.tests.EmailServiceTest
python manage.py test authentication.tests.PasswordResetTokenTest
python manage.py test authentication.tests.PasswordResetRequestAPITest
python manage.py test authentication.tests.PasswordResetConfirmAPITest
```

### Manual Testing

Run the manual test script:
```bash
python test_email_service.py
```

This will:
- Verify email templates exist
- Send test verification email
- Send test password reset email
- Display email content in console

### Testing with Real SMTP

1. Configure SMTP settings in `.env`
2. Change `EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend`
3. Run manual test script
4. Check your inbox for emails

## Security Considerations

### Token Security

- ✅ Tokens are UUIDs (cryptographically random)
- ✅ Password reset tokens expire after 1 hour
- ✅ Tokens are cleared after successful use
- ✅ Invalid tokens return generic error messages
- ✅ Email enumeration prevented (always return success)

### Email Security

- ✅ HTTPS links in production
- ✅ No sensitive data in email content
- ✅ Anonymous identifiers in logs
- ✅ TLS encryption for SMTP
- ✅ Secure token generation

### Rate Limiting

Email endpoints are protected by the rate limiting middleware:
- Maximum 5 failed attempts per IP
- Prevents email spam and abuse

## Troubleshooting

### Emails Not Sending

1. **Check Celery is running:**
   ```bash
   celery -A ano_backend worker --loglevel=info
   ```

2. **Check email backend configuration:**
   ```python
   # In Django shell
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   print(settings.EMAIL_HOST)
   ```

3. **Check Celery logs for errors:**
   Look for task failures or SMTP errors

4. **Test SMTP connection:**
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

### Gmail Authentication Errors

- Ensure 2FA is enabled
- Use App Password, not regular password
- Check "Less secure app access" is disabled (use App Passwords instead)
- Verify EMAIL_HOST_USER matches the Gmail account

### Template Not Found Errors

Ensure templates are in correct location:
```
backend/authentication/templates/authentication/
├── verification_email.html
└── password_reset_email.html
```

## API Examples

### Request Password Reset

```bash
curl -X POST http://localhost:8000/api/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@iiti.ac.in"}'
```

Response:
```json
{
  "message": "If an account exists with this email, you will receive password reset instructions."
}
```

### Confirm Password Reset

```bash
curl -X POST http://localhost:8000/api/auth/password-reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "5c2b716c-991b-4e07-ae79-26bdcb71d8e1",
    "password": "NewSecurePass123!",
    "password_confirm": "NewSecurePass123!"
  }'
```

Response:
```json
{
  "message": "Password reset successful. You can now log in with your new password."
}
```

## Production Checklist

- [ ] Configure SMTP settings in production `.env`
- [ ] Set `EMAIL_BACKEND` to SMTP backend
- [ ] Add valid `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- [ ] Set `FRONTEND_URL` to production domain
- [ ] Start Celery worker with supervisor/systemd
- [ ] Configure Celery monitoring (Flower)
- [ ] Set up email delivery monitoring
- [ ] Test email delivery in production
- [ ] Configure email rate limiting
- [ ] Set up email bounce handling

## Future Enhancements

- [ ] Email templates with user's preferred language
- [ ] Email delivery status tracking
- [ ] Resend verification email endpoint
- [ ] Email notification preferences
- [ ] HTML email preview in admin dashboard
- [ ] Email analytics and metrics
- [ ] Custom email templates per institution
- [ ] Email queue monitoring dashboard

## Related Files

- `backend/authentication/tasks.py` - Celery tasks
- `backend/authentication/views.py` - API endpoints
- `backend/authentication/models.py` - User model with token methods
- `backend/authentication/serializers.py` - Request/response serializers
- `backend/authentication/templates/` - Email templates
- `backend/authentication/tests.py` - Unit tests
- `backend/test_email_service.py` - Manual test script
- `backend/.env` - Configuration
- `backend/ano_backend/celery.py` - Celery configuration
