# Environment Variables Reference

Complete reference for all environment variables used in the Ano platform.

## Backend Environment Variables

Location: `backend/.env`

### Django Settings

#### SECRET_KEY
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Description**: Django secret key for cryptographic signing
- **Example**: `your-secret-key-here-change-in-production`
- **Production**: Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- **Security**: Never commit to version control, use strong random value

#### DEBUG
- **Type**: Boolean
- **Required**: Yes
- **Default**: `False`
- **Description**: Enable Django debug mode
- **Values**: `True` or `False`
- **Development**: `True`
- **Production**: `False`
- **Warning**: Never enable in production (exposes sensitive information)

#### ALLOWED_HOSTS
- **Type**: Comma-separated list
- **Required**: Yes (when DEBUG=False)
- **Default**: Empty
- **Description**: List of host/domain names that Django can serve
- **Development**: `localhost,127.0.0.1`
- **Production**: `your-domain.com,www.your-domain.com`
- **Example**: `example.com,api.example.com`

### Database Settings

#### DB_NAME
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Description**: PostgreSQL database name
- **Example**: `ano_db`
- **Production**: Use descriptive name like `ano_production`

#### DB_USER
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Description**: PostgreSQL username
- **Example**: `ano_user`
- **Production**: Use strong username, not `postgres`

#### DB_PASSWORD
- **Type**: String
- **Required**: Yes
- **Default**: None
- **Description**: PostgreSQL password
- **Example**: `ano_password`
- **Production**: Use strong random password (20+ characters)
- **Security**: Never commit to version control

#### DB_HOST
- **Type**: String
- **Required**: Yes
- **Default**: `localhost`
- **Description**: PostgreSQL host address
- **Development**: `localhost`
- **Docker**: `db` (service name)
- **Production**: Database server IP or hostname

#### DB_PORT
- **Type**: Integer
- **Required**: Yes
- **Default**: `5432`
- **Description**: PostgreSQL port
- **Standard**: `5432`

### Redis Settings

#### REDIS_HOST
- **Type**: String
- **Required**: Yes
- **Default**: `localhost`
- **Description**: Redis host address
- **Development**: `localhost`
- **Docker**: `redis` (service name)
- **Production**: Redis server IP or hostname

#### REDIS_PORT
- **Type**: Integer
- **Required**: Yes
- **Default**: `6379`
- **Description**: Redis port
- **Standard**: `6379`

### JWT Settings

#### JWT_ACCESS_TOKEN_LIFETIME
- **Type**: Integer (minutes)
- **Required**: No
- **Default**: `15`
- **Description**: Access token expiration time in minutes
- **Recommended**: 15-30 minutes
- **Security**: Shorter is more secure but requires more refreshes

#### JWT_REFRESH_TOKEN_LIFETIME
- **Type**: Integer (minutes)
- **Required**: No
- **Default**: `10080` (7 days)
- **Description**: Refresh token expiration time in minutes
- **Recommended**: 7-30 days
- **Note**: 10080 minutes = 7 days

### Email Settings

#### EMAIL_BACKEND
- **Type**: String
- **Required**: Yes
- **Default**: `django.core.mail.backends.console.EmailBackend`
- **Description**: Django email backend to use
- **Development**: `django.core.mail.backends.console.EmailBackend` (prints to console)
- **Production**: `django.core.mail.backends.smtp.EmailBackend`
- **Testing**: `django.core.mail.backends.locmem.EmailBackend`

#### EMAIL_HOST
- **Type**: String
- **Required**: Yes (for SMTP)
- **Default**: None
- **Description**: SMTP server hostname
- **Gmail**: `smtp.gmail.com`
- **SendGrid**: `smtp.sendgrid.net`
- **AWS SES**: `email-smtp.region.amazonaws.com`

#### EMAIL_PORT
- **Type**: Integer
- **Required**: Yes (for SMTP)
- **Default**: `587`
- **Description**: SMTP server port
- **TLS**: `587`
- **SSL**: `465`

#### EMAIL_USE_TLS
- **Type**: Boolean
- **Required**: No
- **Default**: `True`
- **Description**: Use TLS encryption for email
- **Recommended**: `True`

#### EMAIL_HOST_USER
- **Type**: String
- **Required**: Yes (for SMTP)
- **Default**: None
- **Description**: SMTP username/email
- **Example**: `your-email@example.com`
- **Gmail**: Your Gmail address
- **SendGrid**: `apikey`

#### EMAIL_HOST_PASSWORD
- **Type**: String
- **Required**: Yes (for SMTP)
- **Default**: None
- **Description**: SMTP password
- **Gmail**: App Password (not regular password)
- **SendGrid**: API key
- **Security**: Never commit to version control
- **Gmail Setup**: https://myaccount.google.com/apppasswords

### CORS Settings

#### CORS_ALLOWED_ORIGINS
- **Type**: Comma-separated list
- **Required**: Yes
- **Default**: Empty
- **Description**: List of origins allowed to make cross-origin requests
- **Development**: `http://localhost:5173,http://127.0.0.1:5173`
- **Production**: `https://your-domain.com,https://www.your-domain.com`
- **Format**: Include protocol (http/https)
- **Security**: Only include trusted domains

### Celery Settings

#### CELERY_BROKER_URL
- **Type**: String (URL)
- **Required**: Yes
- **Default**: None
- **Description**: Celery message broker URL
- **Format**: `redis://host:port/db`
- **Example**: `redis://localhost:6379/0`
- **Docker**: `redis://redis:6379/0`

#### CELERY_RESULT_BACKEND
- **Type**: String (URL)
- **Required**: No
- **Default**: None
- **Description**: Celery result backend URL
- **Format**: Same as CELERY_BROKER_URL
- **Example**: `redis://localhost:6379/0`

### Application Settings

#### FRONTEND_URL
- **Type**: String (URL)
- **Required**: Yes
- **Default**: None
- **Description**: Frontend application URL (for email links)
- **Development**: `http://localhost:5173`
- **Production**: `https://your-domain.com`
- **Usage**: Used in verification and password reset emails

#### CSRF_TRUSTED_ORIGINS
- **Type**: Comma-separated list
- **Required**: Yes (when not DEBUG)
- **Default**: Empty
- **Description**: Trusted origins for CSRF protection
- **Development**: `http://localhost:5173,http://127.0.0.1:5173`
- **Production**: `https://your-domain.com,https://www.your-domain.com`
- **Format**: Include protocol

### Optional Settings

#### SENTRY_DSN
- **Type**: String (URL)
- **Required**: No
- **Default**: None
- **Description**: Sentry error tracking DSN
- **Example**: `https://key@sentry.io/project`
- **Production**: Recommended for error monitoring

#### LOG_LEVEL
- **Type**: String
- **Required**: No
- **Default**: `INFO`
- **Description**: Logging level
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Development**: `DEBUG`
- **Production**: `INFO` or `WARNING`

---

## Frontend Environment Variables

Location: `frontend/.env`

All frontend environment variables must be prefixed with `VITE_` to be exposed to the client.

### API Configuration

#### VITE_API_BASE_URL
- **Type**: String (URL)
- **Required**: Yes
- **Default**: None
- **Description**: Backend API base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.your-domain.com`
- **Format**: No trailing slash
- **Usage**: Prepended to all API requests

#### VITE_WS_BASE_URL
- **Type**: String (URL)
- **Required**: Yes
- **Default**: None
- **Description**: WebSocket base URL
- **Development**: `ws://localhost:8000/ws`
- **Production**: `wss://api.your-domain.com/ws`
- **Format**: Use `ws://` for development, `wss://` for production
- **Usage**: Used for WebSocket connections

### Application Settings

#### VITE_ENV
- **Type**: String
- **Required**: No
- **Default**: `development`
- **Description**: Application environment
- **Values**: `development`, `staging`, `production`
- **Usage**: Can be used for environment-specific features

#### VITE_APP_NAME
- **Type**: String
- **Required**: No
- **Default**: `Ano`
- **Description**: Application name
- **Usage**: Displayed in UI, page titles

#### VITE_APP_VERSION
- **Type**: String
- **Required**: No
- **Default**: None
- **Description**: Application version
- **Example**: `1.0.0`
- **Usage**: Displayed in footer, about page

### Feature Flags

#### VITE_ENABLE_ANALYTICS
- **Type**: Boolean
- **Required**: No
- **Default**: `false`
- **Description**: Enable analytics tracking
- **Values**: `true` or `false`
- **Production**: `true` (if using analytics)

#### VITE_ENABLE_SENTRY
- **Type**: Boolean
- **Required**: No
- **Default**: `false`
- **Description**: Enable Sentry error tracking
- **Values**: `true` or `false`
- **Production**: `true` (recommended)

#### VITE_SENTRY_DSN
- **Type**: String (URL)
- **Required**: No (if VITE_ENABLE_SENTRY=true)
- **Default**: None
- **Description**: Sentry DSN for frontend
- **Example**: `https://key@sentry.io/project`

---

## Docker Environment Variables

Location: `docker-compose.yml` or `docker-compose.prod.yml`

### PostgreSQL Container

#### POSTGRES_DB
- **Description**: Database name to create
- **Example**: `ano_db`

#### POSTGRES_USER
- **Description**: PostgreSQL superuser name
- **Example**: `ano_user`

#### POSTGRES_PASSWORD
- **Description**: PostgreSQL superuser password
- **Example**: `ano_password`
- **Security**: Use strong password in production

### Redis Container

Redis typically doesn't require environment variables for basic setup.

---

## Environment-Specific Configurations

### Development Environment

**Backend** (`backend/.env`):
```bash
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ano_db
DB_USER=ano_user
DB_PASSWORD=ano_password
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

FRONTEND_URL=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_ENV=development
```

### Production Environment

**Backend** (`backend/.env`):
```bash
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,api.your-domain.com

DB_NAME=ano_production
DB_USER=ano_prod_user
DB_PASSWORD=<strong-random-password>
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@your-domain.com
EMAIL_HOST_PASSWORD=<app-password>

CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

FRONTEND_URL=https://your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

SENTRY_DSN=https://key@sentry.io/project
LOG_LEVEL=INFO
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_BASE_URL=https://api.your-domain.com
VITE_WS_BASE_URL=wss://api.your-domain.com/ws
VITE_ENV=production
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_SENTRY=true
VITE_SENTRY_DSN=https://key@sentry.io/project
```

---

## Security Best Practices

### 1. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.local
.env.production
*.env
```

### 2. Use Strong Passwords

- Minimum 20 characters
- Mix of letters, numbers, symbols
- Use password generator
- Different for each service

### 3. Rotate Secrets Regularly

- Change passwords every 90 days
- Rotate API keys quarterly
- Update JWT secret keys periodically

### 4. Use Environment-Specific Files

- `.env.development` - Development
- `.env.staging` - Staging
- `.env.production` - Production
- Never mix environments

### 5. Limit Access

- Only necessary team members
- Use secret management tools (AWS Secrets Manager, HashiCorp Vault)
- Audit access logs

### 6. Validate Configuration

Check required variables on startup:
```python
# settings.py
import os

REQUIRED_ENV_VARS = [
    'SECRET_KEY',
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")
```

---

## Troubleshooting

### Issue: Environment variables not loading

**Solutions**:
1. Check file name is exactly `.env`
2. Verify file is in correct directory
3. Restart application after changes
4. Check for syntax errors (no spaces around `=`)

### Issue: Frontend variables undefined

**Solutions**:
1. Ensure variables are prefixed with `VITE_`
2. Restart dev server after adding variables
3. Check browser console for errors
4. Verify `.env` file is in `frontend/` directory

### Issue: Database connection failed

**Solutions**:
1. Verify database is running
2. Check DB_HOST, DB_PORT, DB_NAME
3. Verify DB_USER has correct permissions
4. Test connection with psql: `psql -h localhost -U ano_user -d ano_db`

### Issue: Email not sending

**Solutions**:
1. Check EMAIL_BACKEND is set correctly
2. Verify SMTP credentials
3. For Gmail, use App Password not regular password
4. Check firewall allows SMTP port (587/465)
5. Review email logs in console (development)

---

## Quick Reference

### Generate Secret Key

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Generate Random Password

```bash
openssl rand -base64 32
```

### Check Environment Variables

**Backend**:
```bash
cd backend
source venv/bin/activate
python manage.py shell
>>> import os
>>> os.getenv('SECRET_KEY')
```

**Frontend**:
```bash
cd frontend
npm run dev
# Check browser console: import.meta.env
```

### Load from File

**Backend** (automatic with python-decouple or django-environ)

**Frontend** (automatic with Vite)

---

## Support

For environment configuration issues:
- Check this documentation
- Review `.env.example` files
- Verify syntax (no spaces, quotes)
- Check application logs
- Contact DevOps team
