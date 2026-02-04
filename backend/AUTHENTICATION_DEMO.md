# Authentication System Demo

## Quick Start

1. **Start Services:**
```bash
docker-compose up -d
```

2. **Run Migrations:**
```bash
cd backend
python manage.py migrate
```

3. **Start Development Server:**
```bash
python manage.py runserver
```

## Testing the Authentication Flow

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@iiti.ac.in",
    "username": "student123",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "email": "student@iiti.ac.in"
}
```

### 2. Get Verification Token

Since we're using console email backend in development, check the Django console output for the verification link, or get the token from the database:

```bash
python manage.py shell
```

```python
from authentication.models import User
user = User.objects.get(email='student@iiti.ac.in')
print(user.verification_token)
```

### 3. Verify Email

```bash
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR-VERIFICATION-TOKEN-HERE"
  }'
```

**Expected Response:**
```json
{
  "message": "Email verified successfully. You can now log in."
}
```

### 4. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@iiti.ac.in",
    "password": "SecurePass123!"
  }' \
  -c cookies.txt
```

**Expected Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid-here",
    "email": "student@iiti.ac.in",
    "username": "student123",
    "is_verified": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

### 5. Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR-ACCESS-TOKEN-HERE"
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "email": "student@iiti.ac.in",
  "username": "student123",
  "is_verified": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

### 6. Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR-REFRESH-TOKEN-HERE"
  }'
```

Or use the cookie:

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -b cookies.txt \
  -c cookies.txt
```

**Expected Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 7. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR-ACCESS-TOKEN-HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR-REFRESH-TOKEN-HERE"
  }'
```

**Expected Response:**
```json
{
  "message": "Logged out successfully"
}
```

## Testing Invalid Scenarios

### Invalid Email Domain

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@gmail.com",
    "username": "student123",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Expected Response (400):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid registration data",
    "details": {
      "email": ["Email must be from @iiti.ac.in domain"]
    }
  }
}
```

### Login Before Verification

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "unverified@iiti.ac.in",
    "password": "SecurePass123!"
  }'
```

**Expected Response (401):**
```json
{
  "error": {
    "code": "ACCOUNT_NOT_VERIFIED",
    "message": "Please verify your email before logging in"
  }
}
```

### Rate Limiting Test

Make 6 failed login attempts rapidly:

```bash
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{
      "email": "student@iiti.ac.in",
      "password": "wrongpassword"
    }'
  echo "\nAttempt $i"
done
```

**Expected Response on 6th attempt (429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many failed login attempts. Please try again later.",
    "retry_after": 300
  }
}
```

## Running Automated Tests

```bash
cd backend
python manage.py test authentication
```

**Expected Output:**
```
Found 15 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...............
----------------------------------------------------------------------
Ran 15 tests in 1.504s

OK
Destroying test database for alias 'default'...
```

## Key Features Demonstrated

✅ Email domain validation (@iiti.ac.in only)
✅ Email verification flow
✅ Argon2 password hashing
✅ JWT token generation
✅ HTTP-only cookie for refresh token
✅ Token refresh with rotation
✅ Token blacklisting on logout
✅ Rate limiting on failed logins
✅ Protected endpoints with JWT authentication
✅ Comprehensive error handling

## Security Notes

- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Refresh tokens are rotated on each use
- Tokens are blacklisted on logout
- Rate limiting prevents brute-force attacks
- Passwords are hashed with Argon2
- Refresh tokens stored in HTTP-only cookies
- All endpoints validate input server-side
