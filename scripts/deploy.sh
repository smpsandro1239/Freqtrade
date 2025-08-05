#!/bin/bash
set -e

# Freqtrade Multi-Strategy Deploy Script
# Usage: ./scripts/deploy.sh [production|staging]

ENVIRONMENT=${1:-production}
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="deploy.log"

echo "🚀 Starting deployment for $ENVIRONMENT environment..."
echo "$(date): Deploy started" >> $LOG_FILE

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
    echo "$(date): $1" >> $LOG_FILE
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"
    echo "$(date): WARNING: $1" >> $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"
    echo "$(date): ERROR: $1" >> $LOG_FILE
    exit 1
}

# Pre-deployment checks
log "Running pre-deployment checks..."

if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
fi

if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    error "Docker Compose is not installed"
fi

if [ ! -f ".env" ]; then
    error ".env file not found. Copy from .env.example and configure"
fi

# Check if containers are running
if docker compose ps | grep -q "Up"; then
    log "Containers are currently running"
    CONTAINERS_RUNNING=true
else
    log "No containers currently running"
    CONTAINERS_RUNNING=false
fi

# Create backup directory
log "Creating backup directory: $BACKUP_DIR"
mkdir -p $BACKUP_DIR

# Backup database if exists
if [ -f "user_data/tradesv3.dryrun.sqlite" ]; then
    log "Backing up dry-run database..."
    cp user_data/tradesv3.dryrun.sqlite $BACKUP_DIR/
fi

if [ -f "user_data/tradesv3.sqlite" ]; then
    log "Backing up live database..."
    cp user_data/tradesv3.sqlite $BACKUP_DIR/
fi

# Backup current configs
log "Backing up configurations..."
cp -r user_data/configs $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/
cp .env $BACKUP_DIR/

# Git operations
log "Pulling latest changes from repository..."
git fetch origin
git pull origin main

# Check for config changes
if git diff HEAD~1 --name-only | grep -q "user_data/configs\|docker-compose.yml"; then
    warn "Configuration files have changed. Please review before continuing."
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Deployment cancelled by user"
    fi
fi

# Build new images
log "Building Docker images..."
docker compose build --no-cache

# Health check function
health_check() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    log "Checking health of $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose ps $service | grep -q "Up"; then
            log "$service is healthy"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $service not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    error "$service failed to start properly"
}

# Rolling deployment
if [ "$CONTAINERS_RUNNING" = true ]; then
    log "Performing rolling deployment..."
    
    # Stop telegram bot first (non-critical)
    log "Stopping Telegram bot..."
    docker compose stop telegram_bot
    
    # Update telegram bot
    log "Starting updated Telegram bot..."
    docker compose up -d telegram_bot
    health_check telegram_bot
    
    # Update strategies one by one
    for strategy in stratA stratB; do
        log "Updating $strategy..."
        docker compose stop $strategy
        docker compose up -d $strategy
        health_check $strategy
        sleep 5  # Brief pause between strategy updates
    done
    
else
    log "Starting all services..."
    docker compose up -d
    
    # Check all services
    for service in redis stratA stratB telegram_bot; do
        health_check $service
    done
fi

# Post-deployment verification
log "Running post-deployment verification..."

# Check if all containers are running
if ! docker compose ps | grep -q "Up.*Up.*Up.*Up"; then
    warn "Not all containers are running properly"
    docker compose ps
fi

# Test Telegram bot endpoint
if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
    log "Telegram bot health endpoint is responding"
else
    warn "Telegram bot health endpoint is not responding"
fi

# Clean up old images
log "Cleaning up old Docker images..."
docker image prune -f

# Send deployment notification
if [ -f "scripts/telegram_bot.py" ]; then
    log "Sending deployment notification..."
    docker compose exec telegram_bot python -c "
import asyncio
import os
from telegram import Bot

async def notify():
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
    await bot.send_message(
        chat_id=os.getenv('TELEGRAM_CHAT_ID'),
        text='🚀 <b>DEPLOY CONCLUÍDO</b>\n\n✅ Todas as estratégias atualizadas\n✅ Sistema funcionando normalmente\n\n📊 Ambiente: $ENVIRONMENT\n🕐 $(date)',
        parse_mode='HTML'
    )

asyncio.run(notify())
" 2>/dev/null || warn "Could not send deployment notification"
fi

log "✅ Deployment completed successfully!"
log "📊 Backup stored in: $BACKUP_DIR"
log "📋 Logs available in: $LOG_FILE"

# Show final status
echo
echo "=== FINAL STATUS ==="
docker compose ps
echo
echo "=== RECENT LOGS ==="
docker compose logs --tail=10