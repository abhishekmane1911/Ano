# Authentication Module

This module implements the authentication system for the Ano platform with IIT Indore email validation, JWT tokens, and rate limiting.

## Features

- ✅ Custom User model with UUID primary keys
- ✅ Email domain validation (@iiti.ac.in only)
- ✅ Argon2 password hashing
- ✅ JWT authentication with access and refresh tokens
- ✅ Email verification flow
- ✅ Rate limiting on login attempts
- ✅ HTTP-only cookie storage for refresh tokens
- ✅ Token blacklisting on logout

## API Endpoints

### POST /api/auth/register/
Register a new user with IIT Indore email.

**Request:**
```json
{
  "email": "user@iiti.ac.in",
  "username": "username",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "user@iiti.ac.in"
}
```

### POST /api/auth/verify-email/
Verify email address with token sent via email.

**Request:**
```json
{
  "token": "uuid-token-from-email"
}
```

**Response (200):**
```json
{
  "message": "Email verified successfully. You can now log in."
}
```

### POST /api/auth/login/
Login with email and password.

**Request:**
```json
{
  "email": "user@iiti.ac.in",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@iiti.ac.in",
    "username": "username",
    "is_verified": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

**Note:** Refresh token is also set in HTTP-only cookie.

### POST /api/auth/refresh/
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Or use the refresh token from HTTP-only cookie (no body needed).

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### POST /api/auth/logout/
Logout and blacklist refresh token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Or use the refresh token from HTTP-only cookie (no body needed).

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### GET /api/auth/me/
Get current authenticated user details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@iiti.ac.in",
  "username": "username",
  "is_verified": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

The authentication system implements rate limiting on login attempts to prevent brute-force attacks:

- **Max Attempts:** 5 failed login attempts
- **Lockout Duration:** 5 minutes
- **Time Window:** 5 minutes

After 5 failed login attempts from the same IP address, subsequent attempts will be blocked for 5 minutes.

**Rate Limit Response (429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many failed login attempts. Please try again later.",
    "retry_after": 300
  }
}
```

## Security Features

1. **Password Hashing:** Argon2 algorithm (most secure)
2. **JWT Tokens:** 
   - Access token lifetime: 15 minutes
   - Refresh token lifetime: 7 days
   - Token rotation enabled
3. **HTTP-only Cookies:** Refresh tokens stored securely
4. **Email Verification:** Accounts inactive until verified
5. **Rate Limiting:** Protection against brute-force attacks
6. **Token Blacklisting:** Invalidated tokens on logout

## Models

### User Model
Extends Django's AbstractUser with:
- UUID primary key
- Email as username field
- Email domain validation
- Verification token
- is_verified flag

## Testing

Run the test suite:
```bash
python manage.py test authentication
```

All tests should pass:
- User model tests
- Registration API tests
- Email verification tests
- Login API tests
- Token refresh tests
- Rate limiting tests
- Logout tests

## Requirements Validated

This implementation validates the following requirements:

- **1.1:** Email domain validation for @iiti.ac.in
- **1.2:** Verification email sent on registration
- **1.3:** Account activation via email verification
- **1.5:** Argon2 password hashing
- **2.1:** JWT token generation on login
- **2.3:** Token validation on authenticated requests
- **2.4:** Token refresh functionality
- **2.5:** Rate limiting on failed login attempts
