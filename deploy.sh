#!/bin/bash

# Ano Platform Deployment Script
# This script helps with common deployment tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_requirements() {
    print_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found"
        print_info "Creating from template..."
        cp .env.production.example "$ENV_FILE"
        print_warning "Please edit $ENV_FILE with your configuration"
        exit 1
    fi
    print_success "Environment file exists"
}

build_containers() {
    print_info "Building containers..."
    docker-compose -f "$COMPOSE_FILE" build
    print_success "Containers built successfully"
}

start_services() {
    print_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    print_success "Services started"
}

stop_services() {
    print_info "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" stop
    print_success "Services stopped"
}

restart_services() {
    print_info "Restarting services..."
    docker-compose -f "$COMPOSE_FILE" restart
    print_success "Services restarted"
}

view_logs() {
    SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f
    else
        docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
    fi
}

check_health() {
    print_info "Checking service health..."
    
    # Check if containers are running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_error "Some services are not running"
        docker-compose -f "$COMPOSE_FILE" ps
        exit 1
    fi
    print_success "All containers are running"
    
    # Check backend health
    print_info "Checking backend health endpoint..."
    sleep 5
    if curl -f http://localhost:8000/api/health/ &> /dev/null; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
    fi
    
    # Check frontend health
    print_info "Checking frontend health endpoint..."
    if curl -f http://localhost/health &> /dev/null; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend health check failed"
    fi
}

run_migrations() {
    print_info "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" exec backend python manage.py migrate
    print_success "Migrations completed"
}

create_superuser() {
    print_info "Creating superuser..."
    docker-compose -f "$COMPOSE_FILE" exec backend python manage.py createsuperuser
}

backup_database() {
    BACKUP_DIR="backups"
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    print_info "Backing up database to $BACKUP_FILE..."
    docker exec ano_postgres pg_dump -U ano_user ano_db > "$BACKUP_FILE"
    gzip "$BACKUP_FILE"
    print_success "Database backed up to $BACKUP_FILE.gz"
}

restore_database() {
    BACKUP_FILE=$1
    
    if [ -z "$BACKUP_FILE" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_warning "This will restore the database from $BACKUP_FILE"
    read -p "Are you sure? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Restore cancelled"
        exit 0
    fi
    
    print_info "Stopping backend services..."
    docker-compose -f "$COMPOSE_FILE" stop backend backend_asgi celery_worker
    
    print_info "Restoring database..."
    if [[ $BACKUP_FILE == *.gz ]]; then
        gunzip -c "$BACKUP_FILE" | docker exec -i ano_postgres psql -U ano_user ano_db
    else
        cat "$BACKUP_FILE" | docker exec -i ano_postgres psql -U ano_user ano_db
    fi
    
    print_info "Starting backend services..."
    docker-compose -f "$COMPOSE_FILE" start backend backend_asgi celery_worker
    
    print_success "Database restored successfully"
}

update_application() {
    print_info "Updating application..."
    
    # Pull latest code
    print_info "Pulling latest code..."
    git pull origin main
    
    # Rebuild containers
    print_info "Rebuilding containers..."
    docker-compose -f "$COMPOSE_FILE" build
    
    # Restart services
    print_info "Restarting services..."
    docker-compose -f "$COMPOSE_FILE" up -d --no-deps --build backend backend_asgi frontend
    
    # Run migrations
    run_migrations
    
    print_success "Application updated successfully"
}

show_status() {
    print_info "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    print_info "Container Stats:"
    docker stats --no-stream
}

cleanup() {
    print_warning "This will remove unused Docker resources"
    read -p "Continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Cleanup cancelled"
        exit 0
    fi
    
    print_info "Cleaning up..."
    docker image prune -a -f
    docker volume prune -f
    docker container prune -f
    print_success "Cleanup completed"
}

show_help() {
    cat << EOF
Ano Platform Deployment Script

Usage: ./deploy.sh [command]

Commands:
    setup           - Initial setup (check requirements, build, start)
    build           - Build Docker containers
    start           - Start all services
    stop            - Stop all services
    restart         - Restart all services
    logs [service]  - View logs (optionally for specific service)
    health          - Check service health
    migrate         - Run database migrations
    superuser       - Create Django superuser
    backup          - Backup database
    restore <file>  - Restore database from backup
    update          - Update application (pull, build, restart, migrate)
    status          - Show service status and stats
    cleanup         - Remove unused Docker resources
    help            - Show this help message

Examples:
    ./deploy.sh setup
    ./deploy.sh logs backend
    ./deploy.sh backup
    ./deploy.sh restore backups/db_backup_20240101.sql.gz
    ./deploy.sh update

EOF
}

# Main script
case "${1:-}" in
    setup)
        check_requirements
        build_containers
        start_services
        sleep 10
        check_health
        print_success "Setup completed! Access the application at http://localhost"
        ;;
    build)
        build_containers
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        view_logs "${2:-}"
        ;;
    health)
        check_health
        ;;
    migrate)
        run_migrations
        ;;
    superuser)
        create_superuser
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$2"
        ;;
    update)
        update_application
        ;;
    status)
        show_status
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
