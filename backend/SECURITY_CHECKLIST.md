# Security Checklist for Ano Platform

This checklist ensures all security measures are properly configured before deployment.

## Pre-Deployment Security Checklist

### Django Configuration

- [ ] **SECRET_KEY**: Generate a strong, random secret key (50+ characters)
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```

- [ ] **DEBUG**: Set to `False` in production
  ```python
  DEBUG = False
  ```

- [ ] **ALLOWED_HOSTS**: Configure with production domain(s)
  ```python
  ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
  ```

### HTTPS/SSL Configuration

- [ ] **SSL Certificate**: Install valid SSL certificate (Let's Encrypt, etc.)

- [ ] **SECURE_SSL_REDIRECT**: Enabled automatically when DEBUG=False
  ```python
  SECURE_SSL_REDIRECT = True
  ```

- [ ] **HSTS Headers**: Configured for 1 year
  ```python
  SECURE_HSTS_SECONDS = 31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_PRELOAD = True
  ```

- [ ] **Secure Cookies**: Enabled automatically when DEBUG=False
  ```python
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True
  ```

### CORS Configuration

- [ ] **CORS_ALLOWED_ORIGINS**: Set to production frontend URL(s)
  ```python
  CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']
  ```

- [ ] **CORS_ALLOW_CREDENTIALS**: Enabled for cookie-based auth
  ```python
  CORS_ALLOW_CREDENTIALS = True
  ```

### CSRF Protection

- [ ] **CSRF Middleware**: Enabled in MIDDLEWARE
  ```python
  'django.middleware.csrf.CsrfViewMiddleware'
  ```

- [ ] **CSRF_TRUSTED_ORIGINS**: Set to production domain(s)
  ```python
  CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
  ```

- [ ] **Frontend Integration**: CSRF token included in requests
  ```javascript
  headers: { 'X-CSRFToken': getCookie('csrftoken') }
  ```

### Database Security

- [ ] **Strong Password**: Use strong, random database password

- [ ] **Limited Access**: Database user has minimal required permissions

- [ ] **Connection Security**: Use SSL for database connections if remote

- [ ] **Backup Strategy**: Regular automated backups configured

### File Upload Security

- [ ] **File Validation**: All upload endpoints use `validate_uploaded_file()`

- [ ] **Size Limits**: Configured in settings
  ```python
  FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
  DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
  ```

- [ ] **File Permissions**: Proper permissions on uploaded files
  ```python
  FILE_UPLOAD_PERMISSIONS = 0o644
  ```

- [ ] **Malware Scanning**: Consider integrating ClamAV for production

### Authentication & Authorization

- [ ] **Password Hashing**: Argon2 configured as primary hasher
  ```python
  PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher', ...]
  ```

- [ ] **JWT Configuration**: Short-lived access tokens (15 minutes)
  ```python
  ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
  ```

- [ ] **Token Rotation**: Refresh token rotation enabled
  ```python
  ROTATE_REFRESH_TOKENS = True
  BLACKLIST_AFTER_ROTATION = True
  ```

- [ ] **Rate Limiting**: Enabled on authentication endpoints

### Input Validation

- [ ] **Serializer Validation**: All serializers validate input

- [ ] **Custom Validators**: Applied where needed using decorators

- [ ] **SQL Injection**: Using Django ORM (parameterized queries)

- [ ] **XSS Prevention**: HTML sanitization on user content

### Security Headers

- [ ] **Security Middleware**: All security middleware enabled
  ```python
  'ano_backend.middleware.HTTPSRedirectMiddleware'
  'ano_backend.middleware.SecurityHeadersMiddleware'
  ```

- [ ] **CSP Headers**: Content Security Policy configured

- [ ] **X-Frame-Options**: Set to DENY

- [ ] **X-Content-Type-Options**: Set to nosniff

- [ ] **X-XSS-Protection**: Enabled

### Email Security

- [ ] **Email Backend**: Configured for production SMTP

- [ ] **TLS/SSL**: Email encryption enabled
  ```python
  EMAIL_USE_TLS = True
  ```

- [ ] **App Password**: Using app-specific password (not account password)

- [ ] **Rate Limiting**: Email sending rate limited to prevent abuse

### Redis Security

- [ ] **Password Protection**: Redis password configured

- [ ] **Bind Address**: Redis bound to localhost or private network

- [ ] **Firewall Rules**: Redis port not exposed to public internet

### Logging & Monitoring

- [ ] **Error Logging**: Configured to log errors without exposing sensitive data

- [ ] **Access Logging**: Nginx/Apache access logs enabled

- [ ] **Security Events**: Failed login attempts logged

- [ ] **Anonymous Logging**: All logs use anonymous identifiers

### Infrastructure Security

- [ ] **Firewall**: Configured to allow only necessary ports (80, 443, 22)

- [ ] **SSH Access**: Key-based authentication only, no password auth

- [ ] **System Updates**: OS and packages up to date

- [ ] **Fail2ban**: Configured to block brute-force attempts

- [ ] **Backup Access**: Backups stored securely with encryption

### Environment Variables

- [ ] **Secure Storage**: Environment variables not in version control

- [ ] **Production Values**: All production values configured

- [ ] **Secret Rotation**: Plan for rotating secrets periodically

### Testing

- [ ] **Security Tests**: Run security test suite
  ```bash
  python test_security.py
  ```

- [ ] **Deployment Check**: Run Django deployment check
  ```bash
  python manage.py check --deploy
  ```

- [ ] **Penetration Testing**: Consider professional security audit

### Documentation

- [ ] **Security Policy**: Document security procedures

- [ ] **Incident Response**: Plan for security incidents

- [ ] **User Guidelines**: Security best practices for users

## Post-Deployment Verification

### Immediate Checks

- [ ] **HTTPS**: Verify all pages load over HTTPS
  ```bash
  curl -I https://yourdomain.com
  ```

- [ ] **HSTS Header**: Verify HSTS header present
  ```bash
  curl -I https://yourdomain.com | grep -i strict-transport-security
  ```

- [ ] **CSP Header**: Verify CSP header present
  ```bash
  curl -I https://yourdomain.com | grep -i content-security-policy
  ```

- [ ] **CORS**: Test CORS from frontend domain

- [ ] **CSRF**: Test CSRF protection on POST requests

- [ ] **Rate Limiting**: Test rate limiting on login endpoint

### Security Scanning

- [ ] **SSL Labs**: Test SSL configuration
  - Visit: https://www.ssllabs.com/ssltest/
  - Target grade: A or A+

- [ ] **Security Headers**: Test security headers
  - Visit: https://securityheaders.com/
  - Target grade: A or A+

- [ ] **Mozilla Observatory**: Comprehensive security scan
  - Visit: https://observatory.mozilla.org/

### Ongoing Monitoring

- [ ] **Log Monitoring**: Set up alerts for suspicious activity

- [ ] **Uptime Monitoring**: Monitor service availability

- [ ] **Security Updates**: Subscribe to Django security announcements

- [ ] **Dependency Scanning**: Regular scans for vulnerable dependencies
  ```bash
  pip-audit
  ```

## Common Security Issues to Avoid

### ❌ Don't Do This

1. **Hardcoded Secrets**: Never hardcode passwords, API keys, or secret keys
2. **Debug Mode**: Never run with DEBUG=True in production
3. **Weak Passwords**: Don't use weak or default passwords
4. **Unvalidated Input**: Never trust user input without validation
5. **Exposed Admin**: Don't expose Django admin at /admin/ (change URL)
6. **Missing HTTPS**: Never run production without HTTPS
7. **Outdated Dependencies**: Don't ignore security updates
8. **Verbose Errors**: Don't expose stack traces to users
9. **Unrestricted CORS**: Don't use CORS_ALLOW_ALL_ORIGINS
10. **Missing Rate Limiting**: Don't forget rate limiting on sensitive endpoints

### ✅ Do This Instead

1. **Environment Variables**: Use environment variables for all secrets
2. **Production Mode**: Always set DEBUG=False in production
3. **Strong Passwords**: Use password managers and generate strong passwords
4. **Input Validation**: Validate all input on server side
5. **Custom Admin URL**: Change admin URL to something non-obvious
6. **Force HTTPS**: Use SECURE_SSL_REDIRECT and HSTS
7. **Regular Updates**: Keep all dependencies up to date
8. **Generic Errors**: Show generic error messages to users
9. **Specific Origins**: Whitelist only necessary CORS origins
10. **Rate Limiting**: Implement rate limiting on all sensitive endpoints

## Emergency Procedures

### Security Incident Response

1. **Identify**: Determine the nature and scope of the incident
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove the threat
4. **Recover**: Restore systems to normal operation
5. **Document**: Record all actions taken
6. **Review**: Analyze incident and improve security

### Secret Rotation

If secrets are compromised:

1. **Immediate**: Rotate compromised secrets
2. **Database Password**: Update and restart services
3. **SECRET_KEY**: Generate new key, invalidates all sessions
4. **JWT Secret**: Generate new key, invalidates all tokens
5. **API Keys**: Rotate all third-party API keys
6. **Notify**: Inform affected users if necessary

## Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)

## Contact

For security concerns or to report vulnerabilities:
- Email: security@yourdomain.com
- Use responsible disclosure practices
