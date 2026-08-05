#!/bin/bash
# Trade API Deployment Script
# This script manages the trade-api Docker container deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_STACK_DIR="/home/tony/CascadeProjects/chaba/stacks/web"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if container is running
is_running() {
    docker ps --format '{{.Names}}' | grep -q "^trade-api$"
}

# Function to start the service
start_service() {
    print_status "Starting trade-api service..."
    cd "$WEB_STACK_DIR"
    docker compose up -d trade-api
    print_status "Trade API service started successfully"
    print_status "API available at: http://tony-omen.local:8080/apps/trade/api"
    print_status "Swagger UI at: http://tony-omen.local:8080/apps/trade/api/docs"
}

# Function to stop the service
stop_service() {
    print_status "Stopping trade-api service..."
    cd "$WEB_STACK_DIR"
    docker compose stop trade-api
    print_status "Trade API service stopped"
}

# Function to restart the service
restart_service() {
    print_status "Restarting trade-api service..."
    stop_service
    sleep 2
    start_service
}

# Function to rebuild the service
rebuild_service() {
    print_status "Rebuilding trade-api service..."
    cd "$WEB_STACK_DIR"
    docker compose build --no-cache trade-api
    docker compose up -d trade-api
    print_status "Trade API service rebuilt and started"
}

# Function to view logs
view_logs() {
    print_status "Showing trade-api logs (Ctrl+C to exit)..."
    docker logs -f trade-api
}

# Function to check status
check_status() {
    if is_running; then
        print_status "Trade API is RUNNING"
        echo ""
        docker ps --filter name=trade-api --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        print_status "Health check:"
        curl -s http://tony-omen.local:8080/apps/trade/api/api/health | jq '.' 2>/dev/null || curl -s http://tony-omen.local:8080/apps/trade/api/api/health
    else
        print_warning "Trade API is NOT running"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 {start|stop|restart|rebuild|logs|status}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the trade-api service"
    echo "  stop     - Stop the trade-api service"
    echo "  restart  - Restart the trade-api service"
    echo "  rebuild  - Rebuild and start the trade-api service"
    echo "  logs     - View trade-api logs"
    echo "  status   - Check service status"
    echo ""
    echo "API Endpoints:"
    echo "  API Root:     http://tony-omen.local:8080/apps/trade/api"
    echo "  Health:       http://tony-omen.local:8080/apps/trade/api/api/health"
    echo "  Swagger UI:   http://tony-omen.local:8080/apps/trade/api/docs"
    echo "  ReDoc:        http://tony-omen.local:8080/apps/trade/api/redoc"
}

# Main script logic
case "${1:-}" in
    start)
        if is_running; then
            print_warning "Trade API is already running"
            exit 0
        fi
        start_service
        ;;
    stop)
        if ! is_running; then
            print_warning "Trade API is not running"
            exit 0
        fi
        stop_service
        ;;
    restart)
        restart_service
        ;;
    rebuild)
        rebuild_service
        ;;
    logs)
        if ! is_running; then
            print_error "Trade API is not running"
            exit 1
        fi
        view_logs
        ;;
    status)
        check_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
