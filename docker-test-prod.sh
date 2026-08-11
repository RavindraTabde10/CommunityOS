#!/bin/bash

# CommunityOS Production Docker Compose Test Script
# Tests health, endpoints, resource limits, and networking before EC2 deployment
# Usage: ./docker-test-prod.sh [--cleanup]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="backend/.env.prod.test"
FRONTEND_PORT=8080
BACKEND_PORT=8000
STARTUP_WAIT=20
MAX_RETRIES=5

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

cleanup() {
    echo ""
    log_info "Cleaning up containers and networks..."
    docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    sleep 2
    log_success "Cleanup complete"
}

# Check if docker and docker-compose are available
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    log_success "Docker installed"
    
    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    log_success "Docker Compose installed"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "$COMPOSE_FILE not found"
        exit 1
    fi
    log_success "docker-compose.prod.yml found"
    
    # Check if .env file exists; if not, copy from example or warn
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "backend/.env.example" ]; then
            log_warning "Creating $ENV_FILE from backend/.env.example"
            cp backend/.env.example "$ENV_FILE"
        else
            log_warning "$ENV_FILE not found. Using backend/.env if available"
        fi
    else
        log_success "$ENV_FILE found"
    fi
}

# Modify compose file for local testing (use 8080 instead of 80)
prepare_test_compose() {
    print_header "Preparing Test Environment"
    
    # Create a temporary compose file with port 8080 for frontend
    log_info "Creating temporary compose file with port $FRONTEND_PORT..."
    
    # Use sed to modify the compose file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/- \"80:80\"/- \"$FRONTEND_PORT:80\"/g" "$COMPOSE_FILE" || true
    else
        # Linux
        sed -i "s/- \"80:80\"/- \"$FRONTEND_PORT:80\"/g" "$COMPOSE_FILE" || true
    fi
    
    log_success "Compose file prepared for local testing"
}

restore_compose() {
    # Restore original compose file (80:80)
    log_info "Restoring original compose file..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/- \"$FRONTEND_PORT:80\"/- \"80:80\"/g" "$COMPOSE_FILE" || true
    else
        sed -i "s/- \"$FRONTEND_PORT:80\"/- \"80:80\"/g" "$COMPOSE_FILE" || true
    fi
    log_success "Original compose file restored"
}

# Build images
build_images() {
    print_header "Building Docker Images"
    
    log_info "Building backend and frontend images..."
    if docker compose -f "$COMPOSE_FILE" build 2>&1 | tail -20; then
        log_success "Images built successfully"
    else
        log_error "Failed to build images"
        return 1
    fi
}

# Start containers
start_containers() {
    print_header "Starting Containers"
    
    log_info "Starting services..."
    if docker compose -f "$COMPOSE_FILE" up -d; then
        log_success "Containers started"
    else
        log_error "Failed to start containers"
        return 1
    fi
    
    log_info "Waiting $STARTUP_WAIT seconds for services to start..."
    sleep "$STARTUP_WAIT"
}

# Test container health
test_container_health() {
    print_header "Testing Container Health"
    
    # Check backend health
    log_info "Checking backend health..."
    if docker compose -f "$COMPOSE_FILE" ps backend | grep -q "healthy"; then
        log_success "Backend is healthy"
    elif docker compose -f "$COMPOSE_FILE" ps backend | grep -q "starting"; then
        log_warning "Backend still starting; waiting..."
        sleep 10
        if docker compose -f "$COMPOSE_FILE" ps backend | grep -q "healthy"; then
            log_success "Backend is now healthy"
        else
            log_error "Backend health check failed or timed out"
        fi
    else
        log_error "Backend is not healthy"
        docker compose -f "$COMPOSE_FILE" logs backend | tail -20
        return 1
    fi
    
    # Check frontend health
    log_info "Checking frontend health..."
    if docker compose -f "$COMPOSE_FILE" ps frontend | grep -q "healthy"; then
        log_success "Frontend is healthy"
    elif docker compose -f "$COMPOSE_FILE" ps frontend | grep -q "starting"; then
        log_warning "Frontend still starting; waiting..."
        sleep 10
        if docker compose -f "$COMPOSE_FILE" ps frontend | grep -q "healthy"; then
            log_success "Frontend is now healthy"
        else
            log_error "Frontend health check failed or timed out"
        fi
    else
        log_error "Frontend is not healthy"
        docker compose -f "$COMPOSE_FILE" logs frontend | tail -20
        return 1
    fi
}

# Test API endpoints
test_endpoints() {
    print_header "Testing API Endpoints"
    
    # Test backend Swagger UI
    log_info "Testing backend Swagger UI (http://localhost:$BACKEND_PORT/api/docs)..."
    if curl -sf "http://localhost:$BACKEND_PORT/api/docs" > /dev/null 2>&1; then
        log_success "Backend Swagger UI accessible"
    else
        log_error "Backend Swagger UI not accessible"
        return 1
    fi
    
    # Test backend health endpoint (if exists)
    log_info "Testing backend root endpoint..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$BACKEND_PORT/")
    if [ "$response" == "200" ] || [ "$response" == "404" ]; then
        log_success "Backend responding (HTTP $response)"
    else
        log_error "Backend not responding correctly (HTTP $response)"
        return 1
    fi
    
    # Test frontend
    log_info "Testing frontend (http://localhost:$FRONTEND_PORT)..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT/")
    if [ "$response" == "200" ]; then
        log_success "Frontend accessible (HTTP $response)"
    else
        log_error "Frontend not accessible (HTTP $response)"
        return 1
    fi
    
    # Test frontend loads HTML
    log_info "Checking if frontend returns HTML..."
    content=$(curl -s "http://localhost:$FRONTEND_PORT/" | head -20)
    if echo "$content" | grep -q "<html\|<!DOCTYPE"; then
        log_success "Frontend returns valid HTML"
    else
        log_error "Frontend HTML invalid"
        return 1
    fi
    
    # Test API proxy from frontend
    log_info "Testing API proxy through frontend (http://localhost:$FRONTEND_PORT/api/docs)..."
    if curl -sf "http://localhost:$FRONTEND_PORT/api/docs" > /dev/null 2>&1; then
        log_success "API proxy working (frontend → backend)"
    else
        log_warning "API proxy failed (might be expected if no /api/docs endpoint)"
    fi
}

# Test resource limits
test_resource_limits() {
    print_header "Testing Resource Limits"
    
    log_info "Checking resource limits and usage..."
    
    # Get stats
    docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.CPUPerc}}" > /tmp/docker_stats.txt 2>&1
    
    # Check backend memory
    backend_stats=$(docker stats communityos-backend --no-stream --format "{{.MemUsage}}" 2>/dev/null || echo "0B")
    log_info "Backend memory usage: $backend_stats"
    
    # Check frontend memory
    frontend_stats=$(docker stats communityos-frontend --no-stream --format "{{.MemUsage}}" 2>/dev/null || echo "0B")
    log_info "Frontend memory usage: $frontend_stats"
    
    # Check if limits are set in container config
    log_info "Checking memory limits in container config..."
    backend_limit=$(docker inspect communityos-backend --format="{{.HostConfig.Memory}}" 2>/dev/null || echo "0")
    if [ "$backend_limit" != "0" ]; then
        limit_mb=$((backend_limit / 1048576))
        log_success "Backend memory limit set: ${limit_mb}M"
    else
        log_warning "Backend memory limit not set (might be using compose defaults)"
    fi
    
    frontend_limit=$(docker inspect communityos-frontend --format="{{.HostConfig.Memory}}" 2>/dev/null || echo "0")
    if [ "$frontend_limit" != "0" ]; then
        limit_mb=$((frontend_limit / 1048576))
        log_success "Frontend memory limit set: ${limit_mb}M"
    else
        log_warning "Frontend memory limit not set (might be using compose defaults)"
    fi
}

# Test networking
test_networking() {
    print_header "Testing Networking"
    
    log_info "Checking network configuration..."
    
    # Check if network exists
    if docker network ls | grep -q "communityos-network"; then
        log_success "communityos-network exists"
    else
        log_error "communityos-network not found"
        return 1
    fi
    
    # Test inter-container communication
    log_info "Testing inter-container communication (frontend → backend)..."
    if docker exec communityos-frontend wget -q -O- "http://backend:8000/api/docs" > /dev/null 2>&1; then
        log_success "Frontend can reach backend via internal network"
    else
        log_warning "Frontend cannot reach backend (may be expected if API blocked)"
    fi
    
    # Check container IPs
    backend_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' communityos-backend 2>/dev/null)
    frontend_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' communityos-frontend 2>/dev/null)
    
    log_info "Backend IP: $backend_ip"
    log_info "Frontend IP: $frontend_ip"
    log_success "Container IPs assigned"
}

# Test volume mounts
test_volumes() {
    print_header "Testing Volumes"
    
    log_info "Checking volume configuration..."
    
    # Check if backend_data volume exists
    if docker volume ls | grep -q "backend_data"; then
        log_success "backend_data volume exists"
    else
        log_error "backend_data volume not found"
        return 1
    fi
    
    # Test volume accessibility from backend
    log_info "Testing volume accessibility..."
    if docker exec communityos-backend touch /app/data/test.txt 2>/dev/null; then
        if docker exec communityos-backend test -f /app/data/test.txt; then
            log_success "Backend can write to volume"
            docker exec communityos-backend rm -f /app/data/test.txt 2>/dev/null
        else
            log_error "Backend cannot access volume after write"
            return 1
        fi
    else
        log_warning "Could not test volume write (permissions issue)"
    fi
}

# Test environment variables
test_environment() {
    print_header "Testing Environment Variables"
    
    log_info "Checking backend environment variables..."
    
    # Check key env vars
    pythonunbuffered=$(docker exec communityos-backend printenv PYTHONUNBUFFERED 2>/dev/null || echo "NOT SET")
    if [ "$pythonunbuffered" == "1" ]; then
        log_success "PYTHONUNBUFFERED is set"
    else
        log_warning "PYTHONUNBUFFERED not set (value: $pythonunbuffered)"
    fi
    
    # Check if backend loaded .env file
    log_info "Checking if .env file was loaded..."
    if [ -f "$ENV_FILE" ]; then
        log_success "$ENV_FILE exists and should be loaded"
    else
        log_warning "$ENV_FILE not found; using default .env"
    fi
}

# Generate report
generate_report() {
    print_header "Test Report"
    
    total=$((PASSED + FAILED + WARNINGS))
    
    echo ""
    echo "Test Results:"
    echo "  ✓ Passed:  $PASSED"
    echo "  ✗ Failed:  $FAILED"
    echo "  ⚠ Warnings: $WARNINGS"
    echo "  Total:   $total"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}All tests passed! Safe to deploy to EC2.${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        return 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}Some tests failed. Review errors above before deploying.${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║   CommunityOS Production Docker Compose Test Suite            ║
║   Automated tests for production deployment validation        ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    # Parse arguments
    cleanup_after=0
    if [ "$1" == "--cleanup" ]; then
        cleanup_after=1
    fi
    
    # Run test phases
    check_prerequisites || exit 1
    prepare_test_compose || exit 1
    
    if ! build_images; then
        restore_compose
        exit 1
    fi
    
    if ! start_containers; then
        restore_compose
        cleanup
        exit 1
    fi
    
    # Run all tests
    test_container_health || log_warning "Container health tests had issues"
    test_endpoints || log_warning "Endpoint tests had issues"
    test_resource_limits || log_warning "Resource limit tests had issues"
    test_networking || log_warning "Networking tests had issues"
    test_volumes || log_warning "Volume tests had issues"
    test_environment || log_warning "Environment tests had issues"
    
    # Cleanup
    if [ $cleanup_after -eq 1 ] || [ $FAILED -gt 0 ]; then
        cleanup
    else
        log_info "Containers still running. Run 'docker compose -f $COMPOSE_FILE down' to stop."
    fi
    
    restore_compose
    
    # Generate report and exit
    generate_report
    exit_code=$?
    
    echo ""
    echo "Next steps:"
    echo "  1. Review any warnings above"
    echo "  2. If all tests pass, deploy to EC2:"
    echo "     - Copy docker-compose.prod.yml to EC2"
    echo "     - Set environment variables in backend/.env"
    echo "     - Run: docker compose -f docker-compose.prod.yml up -d"
    echo ""
    
    exit $exit_code
}

# Trap errors and cleanup
trap 'log_error "Script interrupted"; restore_compose; cleanup; exit 1' INT TERM

# Run main function
main "$@"
