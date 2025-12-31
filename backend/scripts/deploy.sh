#!/bin/bash
# Deployment script for AI-Powered Todo Chatbot
# Usage: ./scripts/deploy.sh [staging|production]

set -e  # Exit on error

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   AI Todo Chatbot - Deployment Script                    ║"
echo "║   Environment: $ENVIRONMENT                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is required but not installed."
        exit 1
    fi
}

# Step 1: Pre-deployment checks
log_info "Step 1/7: Running pre-deployment checks..."

check_command python3
check_command pip
check_command alembic

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    log_error ".env file not found! Copy from .env.example and configure."
    exit 1
fi

# Validate required environment variables
required_vars=("DATABASE_URL" "BETTER_AUTH_SECRET" "OPENAI_API_KEY" "OPENAI_AGENT_MODEL")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" "$PROJECT_ROOT/.env"; then
        log_error "Required environment variable ${var} not found in .env"
        exit 1
    fi
done

log_info "✓ Pre-deployment checks passed"
echo ""

# Step 2: Install dependencies
log_info "Step 2/7: Installing dependencies..."
cd "$PROJECT_ROOT"
pip install -q --upgrade pip
pip install -q -e .
log_info "✓ Dependencies installed"
echo ""

# Step 3: Run database migrations
log_info "Step 3/7: Running database migrations..."
alembic upgrade head

# Verify migrations
log_info "Verifying database tables..."
python3 -c "
from src.db import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
required_tables = ['users', 'tasks', 'conversations', 'messages']
for table in required_tables:
    if table in tables:
        print(f'  ✓ Table {table} exists')
    else:
        print(f'  ✗ Table {table} missing')
        exit(1)
"
log_info "✓ Database migrations complete"
echo ""

# Step 4: Health check
log_info "Step 4/7: Running health checks..."
python3 -c "
from src.config import settings
print(f'  ✓ Database URL configured')
print(f'  ✓ OpenAI API Key: {settings.openai_api_key[:8]}...')
print(f'  ✓ Model: {settings.openai_agent_model}')
print(f'  ✓ Pool size: {settings.db_pool_size}')
print(f'  ✓ Max overflow: {settings.db_max_overflow}')
"
log_info "✓ Health checks passed"
echo ""

# Step 5: Run tests (optional for staging, required for production)
if [ "$ENVIRONMENT" = "production" ]; then
    log_info "Step 5/7: Running test suite..."
    pytest tests/ -v --tb=short
    log_info "✓ All tests passed"
else
    log_warn "Step 5/7: Skipping tests (staging environment)"
fi
echo ""

# Step 6: Security checks
log_info "Step 6/7: Running security checks..."

# Check debug mode is disabled for production
if [ "$ENVIRONMENT" = "production" ]; then
    if grep -q "^DEBUG=true" "$PROJECT_ROOT/.env"; then
        log_error "DEBUG mode is enabled in production! Set DEBUG=false"
        exit 1
    fi
    log_info "✓ Debug mode disabled"
fi

# Check secret length
SECRET_LENGTH=$(grep "^BETTER_AUTH_SECRET=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d '"' | wc -c)
if [ $SECRET_LENGTH -lt 32 ]; then
    log_error "BETTER_AUTH_SECRET is too short (< 32 chars)"
    exit 1
fi
log_info "✓ Security checks passed"
echo ""

# Step 7: Start application (or report success)
log_info "Step 7/7: Deployment complete!"
echo ""
echo "════════════════════════════════════════════════════════════"
echo " Deployment Summary - $ENVIRONMENT"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ Dependencies installed"
echo "✅ Database migrations applied"
echo "✅ Health checks passed"
echo "✅ Security validated"
echo ""
echo "Next Steps:"
echo "  1. Start the server:"
echo "     uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "  2. Verify health endpoint:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  3. Run smoke tests:"
echo "     python tests/smoke_tests.py"
echo ""
echo "  4. Monitor logs:"
echo "     tail -f logs/app.log (if configured)"
echo ""
echo "════════════════════════════════════════════════════════════"
