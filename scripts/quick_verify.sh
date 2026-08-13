#!/bin/bash
# Quick Trade Data Verification Script
# Fast check of current data status without updates

set -e

echo "=========================================="
echo "Quick Trade Data Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check container status
echo "1. Container Status"
if docker ps | grep -q trade-api; then
    print_success "trade-api container is running"
else
    print_error "trade-api container is not running"
    exit 1
fi

echo ""
echo "2. API Health Check"
HEALTH=$(curl -s http://localhost:9000/api/health)
STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
if [ "$STATUS" = "ok" ] || [ "$STATUS" = "warning" ]; then
    print_success "API is healthy (status: $STATUS)"
else
    print_error "API health check failed"
fi

echo ""
echo "3. Data Freshness Check"
echo "$HEALTH" | python3 -c "
import sys, json
data = json.load(sys.stdin)
warnings = data.get('warnings', [])
if warnings:
    for warning in warnings:
        print(f'⚠️  {warning}')
else:
    print('✅ No data freshness warnings')
"

echo ""
echo "4. Database Record Counts"
docker exec trade-api python -c "
from src.database import db
from sqlalchemy import text

session = db.get_session()
try:
    # Exchange rates
    result = session.execute(text('SELECT COUNT(*) FROM exchange_rates'))
    print(f'Exchange rates: {result.scalar():,} records')
    
    # Commodity prices
    result = session.execute(text('SELECT COUNT(*) FROM commodity_prices'))
    print(f'Commodity prices: {result.scalar():,} records')
    
    # Dollar index
    result = session.execute(text('SELECT COUNT(*) FROM dollar_index'))
    print(f'Dollar index: {result.scalar():,} records')
    
    # Latest dates
    result = session.execute(text('SELECT MAX(date) FROM exchange_rates'))
    print(f'Latest exchange rate: {result.scalar()}')
    
    result = session.execute(text('SELECT MAX(date) FROM commodity_prices'))
    print(f'Latest commodity price: {result.scalar()}')
    
    result = session.execute(text('SELECT MAX(date) FROM dollar_index'))
    print(f'Latest dollar index: {result.scalar()}')
finally:
    session.close()
"

echo ""
echo "5. Sample Data Verification"
echo "Testing API endpoints..."

# Test exchange rate
echo "Testing THB exchange rate..."
THB_DATA=$(curl -s "http://localhost:9000/api/exchange_rates/THB?limit=1")
if echo "$THB_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if data.get('count',0)>0 else 1)"; then
    LATEST_RATE=$(echo "$THB_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['data'][0]['rate'])")
    print_success "THB rate: $LATEST_RATE"
else
    print_warning "No THB data available"
fi

# Test commodity prices
echo "Testing WTI oil price..."
WTI_DATA=$(curl -s "http://localhost:9000/api/commodity_prices/OIL?limit=1")
if echo "$WTI_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if data.get('count',0)>0 else 1)"; then
    LATEST_WTI=$(echo "$WTI_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['data'][0]['price'])")
    print_success "WTI oil: \$$LATEST_WTI/barrel"
else
    print_warning "No oil data available"
fi

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "If data is stale, run: ./scripts/manual_update.sh"
