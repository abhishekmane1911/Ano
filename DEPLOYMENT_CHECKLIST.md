# Ano Platform - Production Deployment Checklist

Use this checklist to ensure a smooth production deployment.

## Pre-Deployment

### Server Setup
- [ ] Server provisioned (2GB+ RAM, 2+ CPU cores, 20GB+ storage)
- [ ] Ubuntu 20.04+ or similar Linux distribution installed
- [ ] SSH access configured with key-based authentication
- [ ] Firewall configured (UFW or iptables)
- [ ] fail2ban installed and configured
- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Git installed

### Domain & DNS
- [ ] Domain name registered
- [ ] DNS A record pointing to server IP
- [ ] DNS propagation verified (use `dig yourdomain.com`)
- [ ] SSL certificates obtained (Let's Encrypt or custom)

### External Services
- [ ] SMTP server credentials ready
- [ ] SMTP server tested and working
- [ ] Email templates reviewed
- [ ] (Optional) Monitoring service configured
- [ ] (Optional) CDN configured for media files

### Security Credentials
- [ ] Django SECRET_KEY generated (50+ characters)
- [ ] Strong database password created (16+ characters)
- [ ] Admin email and password prepared
- [ ] All default passwords changed
- [ ] Credentials stored securely (password manager)

## Configuration

### Environment Variables
- [ ] `.env.production` created from template
- [ ] `SECRET_KEY` set with generated value
- [ ] `DEBUG` set to `False`
- [ ] `ALLOWED_HOSTS` configured with domain names
- [ ] `CORS_ALLOWED_ORIGINS` configured with frontend URLs
- [ ] `DB_PASSWORD` set with strong password
- [ ] `EMAIL_HOST` configured
- [ ] `EMAIL_HOST_USER` configured
- [ ] `EMAIL_HOST_PASSWORD` configured
- [ ] `DJANGO_SUPERUSER_EMAIL` set
- [ ] `DJANGO_SUPERUSER_PASSWORD` set
- [ ] `FRONTEND_URL` configured
- [ ] All other variables reviewed and set

### Docker Configuration
- [ ] `docker-compose.prod.yml` reviewed
- [ ] Service resource limits appropriate for server
- [ ] Volume mounts configured correctly
- [ ] Network configuration reviewed
- [ ] Health checks configured

### Nginx Configuration
- [ ] `frontend/nginx.conf` reviewed
- [ ] SSL configuration prepared (if using SSL)
- [ ] Proxy settings verified
- [ ] Security headers configured
- [ ] Gzip compression enabled
- [ ] Client body size limit set appropriately

### Database Configuration
- [ ] `init-db.sql` reviewed
- [ ] Connection pooling settings appropriate
- [ ] PostgreSQL extensions enabled
- [ ] Backup strategy planned

## Deployment

### Initial Deployment
- [ ] Repository cloned to server
- [ ] `.env.production` file in place
- [ ] File permissions set correctly
- [ ] `deploy.sh` made executable (`chmod +x deploy.sh`)
- [ ] `monitor.sh` made executable (`chmod +x monitor.sh`)
- [ ] Docker images built (`./deploy.sh build`)
- [ ] Services started (`./deploy.sh start`)
- [ ] Logs checked for errors (`./deploy.sh logs`)
- [ ] Health checks passing (`./deploy.sh health`)

### Database Setup
- [ ] Migrations applied (`./deploy.sh migrate`)
- [ ] Superuser created (automatically or manually)
- [ ] Database accessible from backend
- [ ] Sample data loaded (if needed)

### SSL/TLS Setup (if applicable)
- [ ] Certificates obtained
- [ ] Certificates mounted in docker-compose
- [ ] Nginx SSL configuration applied
- [ ] HTTPS redirect working
- [ ] SSL certificate auto-renewal configured
- [ ] HSTS headers configured

### Service Verification
- [ ] Frontend accessible at domain
- [ ] Backend API responding at `/api/`
- [ ] WebSocket connections working at `/ws/`
- [ ] Static files serving correctly
- [ ] Media files serving correctly
- [ ] Admin panel accessible at `/admin/`
- [ ] Email sending working (test registration)
- [ ] Celery tasks processing
- [ ] Redis cache working

## Post-Deployment

### Testing
- [ ] User registration flow tested
- [ ] Email verification tested
- [ ] Login/logout tested
- [ ] Profile creation tested
- [ ] Chat functionality tested
- [ ] Matchmaking tested
- [ ] WebSocket real-time features tested
- [ ] File uploads tested
- [ ] Search functionality tested
- [ ] Admin dashboard tested
- [ ] Report/block functionality tested
- [ ] Mobile responsiveness tested
- [ ] Cross-browser compatibility tested

### Security Verification
- [ ] HTTPS enforced (if SSL configured)
- [ ] Security headers present (check with securityheaders.com)
- [ ] CORS configured correctly
- [ ] CSRF protection working
- [ ] Rate limiting active
- [ ] File upload validation working
- [ ] SQL injection protection verified
- [ ] XSS protection verified
- [ ] Authentication working correctly
- [ ] Authorization working correctly

### Performance Verification
- [ ] Page load times acceptable
- [ ] API response times acceptable
- [ ] WebSocket latency acceptable
- [ ] Database query performance acceptable
- [ ] Static files cached properly
- [ ] Gzip compression working
- [ ] No memory leaks detected
- [ ] CPU usage normal under load

### Monitoring Setup
- [ ] Health check endpoints accessible
- [ ] Monitoring script configured (`./monitor.sh`)
- [ ] Log rotation configured
- [ ] Disk space monitoring set up
- [ ] Memory monitoring set up
- [ ] CPU monitoring set up
- [ ] Database monitoring set up
- [ ] Alert notifications configured
- [ ] Uptime monitoring configured (optional)

### Backup Setup
- [ ] Backup script created
- [ ] Backup directory created
- [ ] Backup cron job configured
- [ ] Backup tested (create and restore)
- [ ] Backup retention policy set
- [ ] Off-site backup configured (optional)
- [ ] Backup monitoring set up

### Documentation
- [ ] Deployment documentation reviewed
- [ ] Admin credentials documented securely
- [ ] Runbook created for common operations
- [ ] Incident response plan documented
- [ ] Contact information updated
- [ ] Team trained on deployment procedures

## Ongoing Maintenance

### Daily
- [ ] Check service health (`./monitor.sh check`)
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Monitor memory usage

### Weekly
- [ ] Review application logs
- [ ] Check backup success
- [ ] Review security logs
- [ ] Monitor performance metrics
- [ ] Check for security updates

### Monthly
- [ ] Test backup restoration
- [ ] Review and rotate logs
- [ ] Update dependencies
- [ ] Review and update documentation
- [ ] Performance optimization review
- [ ] Security audit

### Quarterly
- [ ] Full security audit
- [ ] Disaster recovery test
- [ ] Capacity planning review
- [ ] Update SSL certificates (if not auto-renewed)
- [ ] Review and update monitoring

## Rollback Plan

### If Deployment Fails
- [ ] Stop new services: `./deploy.sh stop`
- [ ] Restore previous version from git
- [ ] Restore database from backup (if needed)
- [ ] Start services: `./deploy.sh start`
- [ ] Verify rollback successful
- [ ] Document issues encountered
- [ ] Plan fixes for next deployment

### Emergency Contacts
- [ ] System Administrator: _______________
- [ ] Technical Lead: _______________
- [ ] Database Administrator: _______________
- [ ] Security Team: _______________
- [ ] On-call Engineer: _______________

## Sign-off

### Deployment Team
- [ ] Developer: _____________ Date: _______
- [ ] DevOps: _____________ Date: _______
- [ ] QA: _____________ Date: _______
- [ ] Security: _____________ Date: _______
- [ ] Manager: _____________ Date: _______

### Production Approval
- [ ] All checklist items completed
- [ ] All tests passing
- [ ] All stakeholders notified
- [ ] Deployment window scheduled
- [ ] Rollback plan ready
- [ ] Team on standby for monitoring

**Deployment Date:** _____________

**Deployment Time:** _____________

**Deployed By:** _____________

**Approved By:** _____________

---

## Notes

Use this section to document any issues, deviations from the plan, or important observations during deployment:

```
[Add notes here]
```

---

## Post-Deployment Review

After 24-48 hours of production operation:

- [ ] No critical issues reported
- [ ] Performance metrics within acceptable range
- [ ] No security incidents
- [ ] User feedback collected
- [ ] Lessons learned documented
- [ ] Deployment process improvements identified

**Review Date:** _____________

**Reviewed By:** _____________

**Status:** [ ] Success [ ] Issues [ ] Rollback Required

**Comments:**
```
[Add comments here]
```
