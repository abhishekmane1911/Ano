#!/bin/bash

# Ano Platform Monitoring Script
# Checks health of all services and sends alerts if needed

set -e

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
LOG_FILE="monitoring.log"
ALERT_EMAIL="${ALERT_EMAIL:-admin@example.com}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if service is running
check_container() {
    local container=$1
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        return 0
    else
        return 1
    fi
}

# Check container health
check_container_health() {
    local container=$1
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
    
    if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
        return 0
    else
        return 1
    fi
}

# Check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local name=$2
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        log_success "$name endpoint is responding"
        return 0
    else
        log_error "$name endpoint is not responding"
        return 1
    fi
}

# Check database connection
check_database() {
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U ano_user -d ano_db -c "SELECT 1;" &> /dev/null; then
        log_success "Database is accessible"
        return 0
    else
        log_error "Database is not accessible"
        return 1
    fi
}

# Check Redis connection
check_redis() {
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q "PONG"; then
        log_success "Redis is responding"
        return 0
    else
        log_error "Redis is not responding"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 90 ]; then
        log_error "Disk usage is critical: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log_warning "Disk usage is high: ${usage}%"
        return 0
    else
        log_success "Disk usage is normal: ${usage}%"
        return 0
    fi
}

# Check memory usage
check_memory() {
    local usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    
    if [ "$usage" -gt 90 ]; then
        log_error "Memory usage is critical: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log_warning "Memory usage is high: ${usage}%"
        return 0
    else
        log_success "Memory usage is normal: ${usage}%"
        return 0
    fi
}

# Check container logs for errors
check_logs_for_errors() {
    local container=$1
    local error_count=$(docker logs --since 5m "$container" 2>&1 | grep -i "error\|exception\|critical" | wc -l)
    
    if [ "$error_count" -gt 10 ]; then
        log_error "$container has $error_count errors in the last 5 minutes"
        return 1
    elif [ "$error_count" -gt 0 ]; then
        log_warning "$container has $error_count errors in the last 5 minutes"
        return 0
    else
        log_success "$container has no recent errors"
        return 0
    fi
}

# Send alert email
send_alert() {
    local subject=$1
    local message=$2
    
    # Only send if mail command is available
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
        log "Alert sent to $ALERT_EMAIL"
    else
        log_warning "Mail command not available, cannot send alert"
    fi
}

# Main monitoring function
run_monitoring() {
    log "=== Starting monitoring check ==="
    
    local errors=0
    local warnings=0
    
    # Check containers
    for container in ano_postgres ano_redis ano_backend ano_backend_asgi ano_frontend ano_celery_worker; do
        if check_container "$container"; then
            log_success "$container is running"
            
            # Check container health
            if ! check_container_health "$container"; then
                log_error "$container is unhealthy"
                ((errors++))
            fi
            
            # Check logs for errors
            if ! check_logs_for_errors "$container"; then
                ((warnings++))
            fi
        else
            log_error "$container is not running"
            ((errors++))
        fi
    done
    
    # Check endpoints
    if ! check_http_endpoint "http://localhost:8000/api/health/" "Backend"; then
        ((errors++))
    fi
    
    if ! check_http_endpoint "http://localhost/health" "Frontend"; then
        ((errors++))
    fi
    
    # Check database
    if ! check_database; then
        ((errors++))
    fi
    
    # Check Redis
    if ! check_redis; then
        ((errors++))
    fi
    
    # Check system resources
    if ! check_disk_space; then
        ((errors++))
    fi
    
    if ! check_memory; then
        ((warnings++))
    fi
    
    # Summary
    log "=== Monitoring check complete ==="
    log "Errors: $errors, Warnings: $warnings"
    
    # Send alert if there are errors
    if [ "$errors" -gt 0 ]; then
        send_alert "Ano Platform Alert: $errors errors detected" "$(tail -n 50 $LOG_FILE)"
        return 1
    fi
    
    return 0
}

# Show current status
show_status() {
    echo "=== Ano Platform Status ==="
    echo ""
    
    echo "Container Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    
    echo "Resource Usage:"
    docker stats --no-stream
    echo ""
    
    echo "Disk Usage:"
    df -h /
    echo ""
    
    echo "Memory Usage:"
    free -h
    echo ""
    
    echo "Recent Logs (last 20 lines):"
    tail -n 20 "$LOG_FILE"
}

# Show help
show_help() {
    cat << EOF
Ano Platform Monitoring Script

Usage: ./monitor.sh [command]

Commands:
    check   - Run monitoring checks
    status  - Show current status
    watch   - Continuously monitor (every 60 seconds)
    help    - Show this help message

Examples:
    ./monitor.sh check
    ./monitor.sh status
    ./monitor.sh watch

Environment Variables:
    ALERT_EMAIL - Email address for alerts (default: admin@example.com)

EOF
}

# Main
case "${1:-check}" in
    check)
        run_monitoring
        ;;
    status)
        show_status
        ;;
    watch)
        log "Starting continuous monitoring (Ctrl+C to stop)"
        while true; do
            run_monitoring
            sleep 60
        done
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
