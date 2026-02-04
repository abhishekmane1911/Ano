# Password Reset Functionality - Development Guide

## Current Status
✅ **Password reset functionality is working correctly!**

The backend logs show that password reset emails are being sent successfully:
```
[2026-02-04 07:18:47] INFO [ano_platform:318] password_reset_request_view - Password reset email task queued for user_6de20ea0-ddbd-42aa-8fa2-9daf95a667d2
[2026-02-04 07:18:47] INFO [ano_platform:86] send_password_reset_email - Password reset email sent successfully to user_6de20ea0-ddbd-42aa-8fa2-9daf95a667d2
```

## The Issue
In development mode, emails are not sent to your actual email inbox. Instead, they are handled by Django's development email backends.

## Current Configuration
Your `.env` file is set to use console email backend:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Solutions

### Option 1: Get Reset URL from Database (Recommended for Development)

I've created a test script that can get your reset URL directly:

```bash
cd backend
python test_password_reset.py
```

This will output something like:
```
Reset URL: http://localhost:5173/password-reset-confirm?token=1906e8e8-d1f9-4170-bc82-7fe08524224f
```

Copy this URL and paste it in your browser to reset your password.

### Option 2: Check Console Output
When you request a password reset, check the Django server console output. The reset URL should be printed there.

### Option 3: Use File-Based Email Backend
Change your `.env` file to:
```
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/app-messages
```

Then restart the Django server. Password reset emails will be saved as files in `/tmp/app-messages/`.

### Option 4: Use Real Email (For Production-like Testing)
To test with real emails, update your `.env` file:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Note:** You'll need to create an App Password in your Gmail account for this to work.

## Testing the Reset Flow

1. **Request Password Reset:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/password-reset/ \
     -H "Content-Type: application/json" \
     -d '{"email": "cse240001025@iiti.ac.in"}'
   ```

2. **Get Reset URL** (using the test script):
   ```bash
   cd backend
   python test_password_reset.py
   ```

3. **Use the Reset URL** in your browser:
   ```
   http://localhost:5173/password-reset-confirm?token=YOUR_TOKEN_HERE
   ```

4. **Test Password Reset API** (optional):
   ```bash
   curl -X POST http://localhost:8000/api/auth/password-reset-confirm/ \
     -H "Content-Type: application/json" \
     -d '{
       "token": "YOUR_TOKEN_HERE",
       "password": "NewPassword123!",
       "password_confirm": "NewPassword123!"
     }'
   ```

## Verification

I've tested the password reset functionality and confirmed:
- ✅ Password reset request API works
- ✅ Reset tokens are generated correctly
- ✅ Reset tokens are valid
- ✅ Password reset confirmation API works
- ✅ Frontend routes are configured correctly
- ✅ API endpoints match between frontend and backend

## Next Steps

1. Use the test script to get your reset URL
2. Test the complete flow in your browser
3. If you want to receive actual emails, configure SMTP settings
4. For production, make sure to use proper email service (SendGrid, AWS SES, etc.)

The password reset functionality is working perfectly - it's just a matter of accessing the reset link in development mode!