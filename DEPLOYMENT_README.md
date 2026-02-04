# Ano Platform - Deployment Documentation

## Overview

This document provides a comprehensive guide for deploying the Ano platform to production. The deployment uses Docker containers orchestrated with Docker Compose for easy management and scalability.

## Architecture

The production deployment consists of the following services:

1. **Frontend (Nginx)** - Serves React application and acts as reverse proxy
2. **Backend WSGI (Gunicorn)** - Handles REST API requests
3. **Backend ASGI (Daphne)** - Handles WebSocket connections
4. **PostgreSQL** - Primary database with connection pooling
5. **Redis** - Cache and WebSocket channel layer
6. **Celery Worker** - Async task processing
7. **Celery Beat** - Scheduled task management

## Files Overview

### Docker Configuration
- `frontend/Dockerfile` - Multi-stage build for React frontend
- `frontend/nginx.conf` - Nginx configuration for HTTP
- `frontend/nginx-ssl.conf` - Nginx configuration with SSL/TLS
- `backend/Dockerfile` - Python backend container
- `backend/docker-entrypoint.sh` - Backend startup script
- `docker-compose.prod.yml` - Production orchestration
- `docker-compose.yml` - Development orchestration

### Configuration Files
- `.env.production.example` - Production environment template
- `init-db.sql` - PostgreSQL initialization and optimization
- `backend/.dockerignore` - Files to exclude from backend build
- `frontend/.dockerignore` - Files to exclude from frontend build

### Scripts
- `deploy.sh` - Deployment automation script
- `monitor.sh` - Health monitoring script

### Documentation
- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `PRODUCTION_SETUP.md` - Quick reference guide
- `DEPLOYMENT_README.md` - This file

## Quick Start

### Prerequisites

1. **Server Requirements**
   - Ubuntu 20.04+ or similar Linux distribution
   - Minimum 2GB RAM, 2 CPU cores
   - 20GB available storage
   - Docker Engine 20.10+
   - Docker Compose 2.0+

2. **Domain & DNS**
   - Domain name registered
   - DNS A records pointing to your server
   - (Optional) SSL certificates ready

3. **External Services**
   - SMTP server for email (Gmail, SendGrid, etc.)
   - (Optional) Monitoring service

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd ano-platform
   ```

2. **Configure Environment**
   ```bash
   cp .env.production.example .env.production
   nano .env.production  # Edit with your values
   ```

3. **Deploy**
   ```bash
   ./deploy.sh setup
   ```

4. **Verify**
   ```bash
   ./deploy.sh health
   ```

## Configuration

### Required Environment Variables

Edit `.env.production` with these critical values:

```bash
# Security
SECRET_KEY=<generate-with-django>
DEBUG=False

# Domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Database
DB_PASSWORD=<strong-password>

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>

# Admin
DJANGO_SUPERUSER_EMAIL=admin@iiti.ac.in
DJANGO_SUPERUSER_PASSWORD=<strong-password>
```

### Generate Django Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Deployment Commands

### Using deploy.sh Script

```bash
# Initial setup
./deploy.sh setup

# Build containers
./deploy.sh build

# Start services
./deploy.sh start

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# View logs
./deploy.sh logs
./deploy.sh logs backend  # Specific service

# Check health
./deploy.sh health

# Run migrations
./deploy.sh migrate

# Create superuser
./deploy.sh superuser

# Backup database
./deploy.sh backup

# Restore database
./deploy.sh restore backups/db_backup_20240101.sql.gz

# Update application
./deploy.sh update

# Show status
./deploy.sh status

# Cleanup unused resources
./deploy.sh cleanup
```

### Manual Docker Compose Commands

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Start
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose -f docker-compose.prod.yml stop

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Execute command in container
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)

1. **Install Certbot**
   ```bash
   sudo apt-get update
   sudo apt-get install certbot
   ```

2. **Obtain Certificates**
   ```bash
   sudo certbot certonly --standalone \
     -d yourdomain.com \
     -d www.yourdomain.com
   ```

3. **Configure Nginx**
   ```bash
   # Use SSL configuration
   cp frontend/nginx-ssl.conf frontend/nginx.conf
   
   # Update docker-compose.prod.yml to mount certificates
   # Add under frontend service volumes:
   #   - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/ssl:ro
   ```

4. **Restart Frontend**
   ```bash
   docker-compose -f docker-compose.prod.yml restart frontend
   ```

5. **Auto-renewal**
   ```bash
   # Add to crontab
   0 0 * * * certbot renew --quiet && docker-compose -f /path/to/ano-platform/docker-compose.prod.yml restart frontend
   ```

### Option 2: Custom Certificates

1. Place certificates in a directory
2. Update `docker-compose.prod.yml` to mount them
3. Update `frontend/nginx-ssl.conf` with correct paths

## Monitoring

### Health Checks

The platform includes built-in health check endpoints:

- Backend: `http://localhost:8000/api/health/`
- Frontend: `http://localhost/health`

### Using monitor.sh Script

```bash
# Run single check
./monitor.sh check

# Show current status
./monitor.sh status

# Continuous monitoring
./monitor.sh watch
```

### Manual Monitoring

```bash
# Container status
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Database connections
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U ano_user -d ano_db -c "SELECT count(*) FROM pg_stat_activity;"

# Redis info
docker-compose -f docker-compose.prod.yml exec redis redis-cli info
```

## Backup and Restore

### Automated Backups

Create a backup script and add to crontab:

```bash
# Create backup script
sudo nano /usr/local/bin/backup-ano.sh

# Add content (see PRODUCTION_SETUP.md)

# Make executable
sudo chmod +x /usr/local/bin/backup-ano.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ano.sh
```

### Manual Backup

```bash
# Using deploy.sh
./deploy.sh backup

# Manual
docker exec ano_postgres pg_dump -U ano_user ano_db > backup.sql
gzip backup.sql
```

### Restore

```bash
# Using deploy.sh
./deploy.sh restore backups/backup.sql.gz

# Manual
gunzip -c backup.sql.gz | docker exec -i ano_postgres psql -U ano_user ano_db
```

## Scaling

### Increase Backend Workers

Edit `.env.production`:
```bash
GUNICORN_WORKERS=8
GUNICORN_THREADS=4
```

Restart:
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Scale Celery Workers

```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

### Database Connection Pooling

Already configured in `init-db.sql` with optimized settings:
- max_connections: 200
- shared_buffers: 256MB
- effective_cache_size: 1GB

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check logs: `./deploy.sh logs backend`
   - Verify environment variables
   - Check database connection

2. **Database connection failed**
   - Ensure PostgreSQL is running
   - Verify credentials in `.env.production`
   - Check network connectivity

3. **WebSocket not working**
   - Check Daphne logs: `./deploy.sh logs backend_asgi`
   - Verify Redis is running
   - Check nginx WebSocket proxy configuration

4. **Email not sending**
   - Check Celery worker logs
   - Verify SMTP credentials
   - Test SMTP connection manually

5. **High memory usage**
   - Check container stats: `docker stats`
   - Reduce Gunicorn workers
   - Adjust Redis memory limit

### Debug Mode

To enable debug logging temporarily:

```bash
# Edit .env.production
DEBUG=True

# Restart services
./deploy.sh restart

# View detailed logs
./deploy.sh logs

# Remember to disable debug after troubleshooting
DEBUG=False
./deploy.sh restart
```

## Security

### Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure SSL/TLS
- [ ] Enable firewall (UFW)
- [ ] Configure fail2ban
- [ ] Regular security updates
- [ ] Automated backups
- [ ] Monitor logs
- [ ] Rate limiting enabled
- [ ] CORS properly configured

### Firewall Setup

```bash
# Install UFW
sudo apt-get install ufw

# Configure
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Enable
sudo ufw enable
```

### Fail2ban Setup

```bash
# Install
sudo apt-get install fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Performance Optimization

### Database

- Indexes already configured in models
- Connection pooling enabled
- Query optimization in `init-db.sql`

### Redis

- Memory limit configured
- LRU eviction policy
- Persistent storage for important data

### Nginx

- Gzip compression enabled
- Static file caching
- Proxy caching available

### Application

- Gunicorn with multiple workers
- Celery for async tasks
- Optimistic UI updates in frontend

## Maintenance

### Regular Updates

```bash
# Pull latest code
git pull origin main

# Update application
./deploy.sh update
```

### Database Maintenance

```bash
# Vacuum database
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U ano_user -d ano_db -c "VACUUM ANALYZE;"

# Check database size
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U ano_user -d ano_db -c "SELECT pg_size_pretty(pg_database_size('ano_db'));"
```

### Log Rotation

Logs are stored in `backend/logs/`. Configure logrotate:

```bash
sudo nano /etc/logrotate.d/ano-platform

# Add configuration (see DEPLOYMENT_GUIDE.md)
```

## Support

### Getting Help

1. Check logs first: `./deploy.sh logs`
2. Review this documentation
3. Check Django/Docker documentation
4. Contact system administrator

### Useful Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## License

[Your License Here]

## Contact

- Technical Support: support@yourdomain.com
- System Administrator: admin@yourdomain.com
- Emergency: emergency@yourdomain.com
