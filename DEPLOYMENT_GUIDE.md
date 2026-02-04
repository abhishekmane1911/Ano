# Ano Platform - Production Deployment Guide

This guide covers deploying the Ano platform to production using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Domain name with DNS configured
- SSL/TLS certificates (Let's Encrypt recommended)
- SMTP server credentials for email
- Minimum 2GB RAM, 2 CPU cores, 20GB storage

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ano-platform
```

### 2. Configure Environment Variables

Copy the production environment template:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` and fill in all required values:

```bash
nano .env.production
```

**Critical settings to configure:**
- `SECRET_KEY`: Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD`: Strong database password
- `ALLOWED_HOSTS`: Your domain names
- `CORS_ALLOWED_ORIGINS`: Your frontend URLs
- `EMAIL_*`: SMTP configuration
- `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD`: Admin credentials

### 3. Build and Start Services

```bash
# Build all containers
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Verify Deployment

Check health endpoints:

```bash
# Backend health check
curl http://localhost:8000/api/health/

# Frontend health check
curl http://localhost/health
```

### 5. Access the Application

- Frontend: http://localhost (or your domain)
- Backend API: http://localhost/api/
- Django Admin: http://localhost/api/admin/

## Architecture Overview

```
┌─────────────┐
│   Nginx     │ :80, :443 (Frontend + Reverse Proxy)
└──────┬──────┘
       │
       ├─────────────────────────────────┐
       │                                 │
┌──────▼──────┐                  ┌──────▼──────┐
│  Gunicorn   │ :8000            │   Daphne    │ :8001
│   (WSGI)    │                  │   (ASGI)    │
└──────┬──────┘                  └──────┬──────┘
       │                                │
       └────────────┬───────────────────┘
                    │
       ┌────────────┴────────────┐
       │                         │
┌──────▼──────┐          ┌──────▼──────┐
│ PostgreSQL  │ :5432    │    Redis    │ :6379
└─────────────┘          └─────────────┘
```

## Service Details

### Frontend (Nginx)
- Serves static React build
- Reverse proxy for API requests
- WebSocket proxy for real-time features
- SSL termination (when configured)
- Ports: 80 (HTTP), 443 (HTTPS)

### Backend WSGI (Gunicorn)
- Handles REST API requests
- 4 workers by default (configurable)
- Port: 8000

### Backend ASGI (Daphne)
- Handles WebSocket connections
- Real-time chat and matchmaking
- Port: 8001

### PostgreSQL
- Primary database
- Connection pooling enabled
- Persistent volume for data
- Port: 5432

### Redis
- WebSocket channel layer
- Celery message broker
- Session cache
- Port: 6379

### Celery Worker
- Async task processing
- Email sending
- Media processing

### Celery Beat
- Scheduled tasks
- Periodic cleanup jobs

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

1. Install certbot:
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. Obtain certificates:
```bash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

3. Update nginx configuration to use certificates:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of configuration
}
```

4. Add certificate renewal to crontab:
```bash
0 0 * * * certbot renew --quiet
```

## Database Management

### Backup Database

```bash
# Create backup
docker exec ano_postgres pg_dump -U ano_user ano_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql
```

### Restore Database

```bash
# Stop backend services
docker-compose -f docker-compose.prod.yml stop backend backend_asgi celery_worker

# Restore from backup
gunzip -c backup_20240101_120000.sql.gz | docker exec -i ano_postgres psql -U ano_user ano_db

# Restart services
docker-compose -f docker-compose.prod.yml start backend backend_asgi celery_worker
```

### Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create migration
docker-compose -f docker-compose.prod.yml exec backend python manage.py makemigrations
```

## Monitoring and Logs

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Application Logs

Logs are stored in `backend/logs/`:
- `ano_platform.log`: General application logs
- `errors.log`: Error logs
- `security.log`: Security-related events

### Monitor Resources

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Service health
docker-compose -f docker-compose.prod.yml ps
```

## Scaling

### Horizontal Scaling

Increase worker processes:

```bash
# Edit .env.production
GUNICORN_WORKERS=8
GUNICORN_THREADS=4

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Add More Celery Workers

```bash
# Scale celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose -f docker-compose.prod.yml build

# Restart services with zero downtime
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend backend_asgi frontend

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove stopped containers
docker container prune
```

## Troubleshooting

### Backend Won't Start

1. Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs backend
```

2. Verify database connection:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

3. Check environment variables:
```bash
docker-compose -f docker-compose.prod.yml exec backend env
```

### WebSocket Connection Issues

1. Check Daphne logs:
```bash
docker-compose -f docker-compose.prod.yml logs backend_asgi
```

2. Verify Redis connection:
```bash
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

3. Test WebSocket endpoint:
```bash
wscat -c ws://localhost/ws/chat/test-room-uuid/
```

### Database Performance Issues

1. Check connection count:
```bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U ano_user -d ano_db -c "SELECT count(*) FROM pg_stat_activity;"
```

2. Analyze slow queries:
```bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U ano_user -d ano_db -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### High Memory Usage

1. Check container memory:
```bash
docker stats --no-stream
```

2. Adjust Redis memory limit in docker-compose.prod.yml:
```yaml
redis:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Configure SSL/TLS certificates
- [ ] Set strong SECRET_KEY
- [ ] Enable firewall (UFW/iptables)
- [ ] Configure fail2ban for SSH
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Monitor logs for suspicious activity
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] File upload limits set

## Performance Optimization

### Database Optimization

1. Enable query logging:
```python
# In settings.py
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['file'],
}
```

2. Add database indexes:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

### Redis Optimization

1. Monitor Redis memory:
```bash
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory
```

2. Adjust eviction policy if needed:
```yaml
redis:
  command: redis-server --maxmemory-policy allkeys-lfu
```

### Frontend Optimization

1. Enable Nginx caching:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;
```

2. Enable Gzip compression (already configured in nginx.conf)

## Support

For issues and questions:
- Check logs first
- Review this guide
- Contact system administrator
- Check Django/Docker documentation

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
