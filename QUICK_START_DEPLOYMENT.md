# Ano Platform - Quick Start Deployment Guide

## 🚀 Deploy in 5 Minutes

This guide will get you up and running quickly. For detailed information, see `DEPLOYMENT_GUIDE.md`.

## Prerequisites

- Server with Docker and Docker Compose installed
- Domain name (optional for testing)
- SMTP credentials for email

## Step 1: Clone and Configure (2 minutes)

```bash
# Clone repository
git clone <repository-url>
cd ano-platform

# Create environment file
cp .env.production.example .env.production

# Generate Django secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit environment file with your values
nano .env.production
```

**Minimum required changes in `.env.production`:**
```bash
SECRET_KEY=<paste-generated-key-here>
DB_PASSWORD=<create-strong-password>
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DJANGO_SUPERUSER_EMAIL=admin@iiti.ac.in
DJANGO_SUPERUSER_PASSWORD=<create-admin-password>
```

## Step 2: Deploy (2 minutes)

```bash
# Make scripts executable
chmod +x deploy.sh monitor.sh

# Run deployment
./deploy.sh setup
```

This will:
- Build all Docker containers
- Start all services
- Run database migrations
- Create superuser
- Collect static files

## Step 3: Verify (1 minute)

```bash
# Check service health
./deploy.sh health

# View logs
./deploy.sh logs

# Check status
./deploy.sh status
```

## Access Your Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/
- **Admin Panel**: http://localhost/admin/
- **Health Check**: http://localhost/health

## Common Commands

```bash
# View logs
./deploy.sh logs
./deploy.sh logs backend  # Specific service

# Restart services
./deploy.sh restart

# Run migrations
./deploy.sh migrate

# Backup database
./deploy.sh backup

# Monitor health
./monitor.sh check
```

## Troubleshooting

### Services won't start
```bash
# Check logs
./deploy.sh logs

# Check environment variables
cat .env.production
```

### Can't access application
```bash
# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# Check firewall
sudo ufw status
```

### Database connection error
```bash
# Verify PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check database logs
./deploy.sh logs postgres
```

## Next Steps

### For Testing
You're ready to test! Register a user at http://localhost

### For Production

1. **Set up SSL/TLS**
   ```bash
   # Install certbot
   sudo apt-get install certbot
   
   # Get certificates
   sudo certbot certonly --standalone -d yourdomain.com
   
   # Use SSL nginx config
   cp frontend/nginx-ssl.conf frontend/nginx.conf
   
   # Restart frontend
   ./deploy.sh restart frontend
   ```

2. **Configure Firewall**
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

3. **Set up Backups**
   ```bash
   # Add to crontab
   crontab -e
   
   # Add this line for daily backups at 2 AM
   0 2 * * * /path/to/ano-platform/deploy.sh backup
   ```

4. **Enable Monitoring**
   ```bash
   # Run continuous monitoring
   ./monitor.sh watch
   
   # Or add to crontab for periodic checks
   */5 * * * * /path/to/ano-platform/monitor.sh check
   ```

## Production Checklist

Before going live, ensure:

- [ ] `.env.production` has all correct values
- [ ] `DEBUG=False` in `.env.production`
- [ ] Strong passwords for database and admin
- [ ] SSL/TLS certificates configured
- [ ] Firewall configured
- [ ] Backups automated
- [ ] Monitoring set up
- [ ] Domain DNS configured
- [ ] Email sending tested
- [ ] All features tested

## Getting Help

- **Detailed Guide**: See `DEPLOYMENT_GUIDE.md`
- **Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Quick Reference**: See `PRODUCTION_SETUP.md`
- **Summary**: See `DEPLOYMENT_SUMMARY.md`

## Architecture Overview

```
Internet → Nginx (Frontend) → Gunicorn (API) → PostgreSQL
                            → Daphne (WebSocket) → Redis
                            → Celery (Tasks)
```

## Default Credentials

**Admin Panel**: http://localhost/admin/
- Email: Value from `DJANGO_SUPERUSER_EMAIL`
- Password: Value from `DJANGO_SUPERUSER_PASSWORD`

**Database**:
- Host: localhost
- Port: 5432
- Database: ano_db
- User: ano_user
- Password: Value from `DB_PASSWORD`

## Important Notes

⚠️ **Security**: Change all default passwords before production use

⚠️ **Email**: Configure SMTP correctly for user registration to work

⚠️ **Domain**: Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` with your domain

⚠️ **SSL**: Use HTTPS in production (Let's Encrypt is free)

⚠️ **Backups**: Set up automated backups immediately

## Success Indicators

✅ All containers running: `docker-compose -f docker-compose.prod.yml ps`

✅ Health checks passing: `./deploy.sh health`

✅ No errors in logs: `./deploy.sh logs`

✅ Frontend accessible: http://localhost

✅ Backend responding: http://localhost/api/health/

✅ Can register new user

✅ Can send and receive messages

## Support

For issues:
1. Check logs: `./deploy.sh logs`
2. Review documentation
3. Check Docker/Django documentation
4. Contact system administrator

---

**Deployment Time**: ~5 minutes
**Difficulty**: Easy
**Prerequisites**: Docker, Docker Compose

Happy deploying! 🎉
