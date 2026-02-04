# Authentication Frontend Implementation

This document describes the authentication frontend implementation for the Ano platform.

## Components Implemented

### 1. Zustand Store (`src/stores/authStore.ts`)
- Manages authentication state (user, access token, authentication status)
- Persists user data to localStorage
- Provides actions for login, logout, and state updates

### 2. Axios Configuration (`src/api/axios.ts`)
- Configured axios instance with base URL
- Request interceptor to add JWT access token to headers
- Response interceptor to handle 401 errors and automatic token refresh
- Refresh token stored in HTTP-only cookie (handled by backend)

### 3. Authentication API (`src/api/auth.ts`)
- API functions for all authentication endpoints:
  - `register()` - User registration with email validation
  - `verifyEmail()` - Email verification with token
  - `login()` - User login with credentials
  - `logout()` - User logout
  - `refreshToken()` - Token refresh
  - `requestPasswordReset()` - Request password reset email
  - `confirmPasswordReset()` - Confirm password reset with token
  - `getCurrentUser()` - Get current user info

### 4. Authentication Components

#### LandingPage (`src/components/auth/LandingPage.tsx`)
- Hero section with platform description
- Feature highlights (anonymity, chatrooms, matchmaking, IIT Indore exclusive)
- Call-to-action buttons for signup and login

#### SignupForm (`src/components/auth/SignupForm.tsx`)
- Email validation for @iiti.ac.in domain
- Password strength validation (min 8 chars, uppercase, lowercase, number)
- Password confirmation matching
- Error handling and display
- Success message with redirect to login

#### LoginForm (`src/components/auth/LoginForm.tsx`)
- Email and password input
- "Remember me" checkbox option
- Rate limiting error handling (429 status)
- Automatic redirect based on verification status
- Link to password reset

#### EmailVerification (`src/components/auth/EmailVerification.tsx`)
- Handles email verification via token in URL query params
- Shows verification status (verifying, success, error, pending)
- Resend verification email option
- Updates user verification status in store
- Redirects to profile creation on success

#### PasswordResetRequest (`src/components/auth/PasswordResetRequest.tsx`)
- Email input with @iiti.ac.in validation
- Sends password reset email
- Success message display

#### PasswordResetConfirm (`src/components/auth/PasswordResetConfirm.tsx`)
- Handles password reset via token in URL query params
- Password strength validation
- Password confirmation matching
- Redirects to login on success

### 5. Routing (`src/App.tsx`)
- React Router setup with protected and public routes
- `ProtectedRoute` component - redirects to login if not authenticated
- `PublicRoute` component - redirects to home if already authenticated
- Routes:
  - `/landing` - Landing page
  - `/signup` - Registration form
  - `/login` - Login form
  - `/verify-email` - Email verification
  - `/password-reset` - Password reset request
  - `/password-reset-confirm` - Password reset confirmation
  - `/` - Home (protected)

## Features Implemented

### Email Domain Validation
- Client-side validation ensures only @iiti.ac.in emails are accepted
- Regex pattern: `/^[^\s@]+@iiti\.ac\.in$/`
- Validates: Requirements 1.1

### Password Security
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Validates: Requirements 1.5

### JWT Token Handling
- Access token stored in memory (Zustand store)
- Refresh token stored in HTTP-only cookie (backend managed)
- Automatic token refresh on 401 responses
- Request interceptor adds token to Authorization header
- Validates: Requirements 2.1, 2.2, 2.3, 2.4

### Rate Limiting
- Handles 429 status code from backend
- Displays user-friendly error message
- Validates: Requirements 2.5

### User Experience
- Loading states during API calls
- Error messages for validation and API errors
- Success messages with automatic redirects
- Responsive design for mobile and desktop

## Environment Variables

Required environment variables in `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_ENV=development
```

## Dependencies

- `react` - UI library
- `react-router-dom` - Routing
- `zustand` - State management
- `axios` - HTTP client

## Usage

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## API Integration

The frontend expects the following backend endpoints:
- `POST /api/auth/register/` - User registration
- `POST /api/auth/verify-email/` - Email verification
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/password-reset/` - Password reset request
- `POST /api/auth/password-confirm/` - Password reset confirmation
- `GET /api/auth/me/` - Get current user

## Security Considerations

1. **Access Token Storage**: Stored in memory (Zustand store) to prevent XSS attacks
2. **Refresh Token**: Stored in HTTP-only cookie by backend, not accessible to JavaScript
3. **HTTPS**: All API calls should use HTTPS in production
4. **CSRF Protection**: Handled by backend with CSRF tokens
5. **Input Validation**: Client-side validation for better UX, server-side validation for security

## Next Steps

- Implement profile creation flow
- Add loading skeletons for better UX
- Implement toast notifications
- Add form field focus management
- Add accessibility improvements (ARIA labels, keyboard navigation)
