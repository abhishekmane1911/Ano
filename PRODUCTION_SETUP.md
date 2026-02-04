# Production Setup Quick Reference

## Pre-deployment Checklist

### 1. Server Requirements
- [ ] Ubuntu 20.04+ or similar Linux distribution
- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Domain name configured with DNS A records
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] Minimum 2GB RAM, 2 CPU cores, 20GB storage

### 2. Required Credentials
- [ ] Django SECRET_KEY generated
- [ ] Strong database password
- [ ] SMTP server credentials
- [ ] Admin email and password
- [ ] SSL certificates (or Let's Encrypt setup)

### 3. Configuration Files
- [ ] `.env.production` created and filled
- [ ] SSL certificates in place (if using)
- [ ] Nginx configuration reviewed

## Quick Setup Commands

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd ano-platform

# 2. Create production environment file
cp .env.production.example .env.production
nano .env.production  # Fill in all values

# 3. Generate Django secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Build containers
docker-compose -f docker-compose.prod.yml build

# 5. Start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Check status
docker-compose -f docker-compose.prod.yml ps

# 7. View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/api/health/

# Check frontend health
curl http://localhost/health

# Check database
docker-compose -f docker-compose.prod.yml exec postgres psql -U ano_user -d ano_db -c "SELECT version();"

# Check Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## Common Operations

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Restart Services
```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Stop/Start Services
```bash
# Stop all
docker-compose -f docker-compose.prod.yml stop

# Start all
docker-compose -f docker-compose.prod.yml start

# Stop specific service
docker-compose -f docker-compose.prod.yml stop backend
```

### Database Operations
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Backup database
docker exec ano_postgres pg_dump -U ano_user ano_db > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20240101.sql | docker exec -i ano_postgres psql -U ano_user ano_db
```

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## Environment Variables Reference

### Critical Variables (Must Set)
```bash
SECRET_KEY=                    # Django secret key
DB_PASSWORD=                   # Database password
ALLOWED_HOSTS=                 # Your domain(s)
CORS_ALLOWED_ORIGINS=          # Frontend URL(s)
EMAIL_HOST=                    # SMTP server
EMAIL_HOST_USER=               # SMTP username
EMAIL_HOST_PASSWORD=           # SMTP password
DJANGO_SUPERUSER_EMAIL=        # Admin email
DJANGO_SUPERUSER_PASSWORD=     # Admin password
```

### Optional Variables (Have Defaults)
```bash
DB_NAME=ano_db
DB_USER=ano_user
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## SSL/TLS Setup with Let's Encrypt

### Install Certbot
```bash
sudo apt-get update
sudo apt-get install certbot
```

### Obtain Certificates
```bash
# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop frontend

# Get certificates
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos

# Certificates will be in /etc/letsencrypt/live/yourdomain.com/
```

### Configure Nginx for SSL
```bash
# Copy SSL nginx config
cp frontend/nginx-ssl.conf frontend/nginx.conf

# Update docker-compose.prod.yml to mount certificates
# Add under frontend service volumes:
#   - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/ssl:ro

# Restart frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Auto-renewal
```bash
# Add to crontab
sudo crontab -e

# Add this line:
0 0 * * * certbot renew --quiet && docker-compose -f /path/to/ano-platform/docker-compose.prod.yml restart frontend
```

## Monitoring

### Check Service Health
```bash
# Container stats
docker stats

# Service status
docker-compose -f docker-compose.prod.yml ps

# Disk usage
docker system df
```

### Application Logs Location
```
backend/logs/ano_platform.log  # General logs
backend/logs/errors.log        # Error logs
backend/logs/security.log      # Security logs
```

### Database Monitoring
```bash
# Connection count
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U ano_user -d ano_db -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U ano_user -d ano_db -c "SELECT pg_size_pretty(pg_database_size('ano_db'));"
```

### Redis Monitoring
```bash
# Memory usage
docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory

# Connected clients
docker-compose -f docker-compose.prod.yml exec redis redis-cli info clients
```

## Troubleshooting

### Backend Won't Start
1. Check logs: `docker-compose -f docker-compose.prod.yml logs backend`
2. Verify environment variables: `docker-compose -f docker-compose.prod.yml exec backend env`
3. Check database connection: `docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell`

### Database Connection Issues
1. Check PostgreSQL is running: `docker-compose -f docker-compose.prod.yml ps postgres`
2. Test connection: `docker-compose -f docker-compose.prod.yml exec postgres psql -U ano_user -d ano_db`
3. Check credentials in `.env.production`

### WebSocket Not Working
1. Check Daphne logs: `docker-compose -f docker-compose.prod.yml logs backend_asgi`
2. Verify Redis: `docker-compose -f docker-compose.prod.yml exec redis redis-cli ping`
3. Check nginx WebSocket proxy configuration

### Email Not Sending
1. Check Celery worker logs: `docker-compose -f docker-compose.prod.yml logs celery_worker`
2. Verify SMTP credentials in `.env.production`
3. Test email manually: `docker-compose -f docker-compose.prod.yml exec backend python manage.py shell`

### High Memory Usage
1. Check container stats: `docker stats`
2. Reduce Gunicorn workers: Edit `GUNICORN_WORKERS` in `.env.production`
3. Adjust Redis memory limit in `docker-compose.prod.yml`

## Security Hardening

### Firewall Setup (UFW)
```bash
# Install UFW
sudo apt-get install ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Fail2ban Setup
```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure for SSH
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Regular Updates
```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Backup Strategy

### Automated Daily Backups
```bash
# Create backup script
cat > /usr/local/bin/backup-ano.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/ano"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker exec ano_postgres pg_dump -U ano_user ano_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /path/to/ano-platform/backend media

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/backup-ano.sh

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ano.sh
```

## Performance Tuning

### Increase Gunicorn Workers
```bash
# Edit .env.production
GUNICORN_WORKERS=8
GUNICORN_THREADS=4

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Scale Celery Workers
```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

### PostgreSQL Tuning
Already configured in `init-db.sql` with optimized settings for:
- Connection pooling
- Memory allocation
- Query optimization
- Write-ahead logging

## Support Contacts

- System Administrator: [admin@yourdomain.com]
- Technical Support: [support@yourdomain.com]
- Emergency Contact: [emergency@yourdomain.com]

## Additional Documentation

- Full Deployment Guide: `DEPLOYMENT_GUIDE.md`
- Application README: `README.md`
- API Documentation: Available at `/api/docs/` when running
