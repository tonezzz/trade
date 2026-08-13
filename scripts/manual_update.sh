#!/bin/bash
# Manual Trade Data Update Script
# Use this when the host comes back online to fetch and verify trade data

set -e

echo "=========================================="
echo "Manual Trade Data Update"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if trade-api container is running
echo "Checking trade-api container status..."
if docker ps | grep -q trade-api; then
    print_success "trade-api container is running"
else
    print_error "trade-api container is not running"
    echo "Starting trade-api container..."
    cd /home/tony/CascadeProjects/trade
    docker compose up -d trade-api
    sleep 10
fi

echo ""
echo "=========================================="
echo "Step 1: Download Exchange Rates"
echo "=========================================="
echo "Fetching current exchange rates from open.er-api.com..."
docker exec trade-api python -c "
import requests
import json
from datetime import datetime

try:
    response = requests.get('https://open.er-api.com/v6/latest/USD')
    data = response.json()
    
    with open('/app/data/archive/usd/exchange_rates_latest.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f'✅ Downloaded exchange rates for {len(data[\"rates\"])} currencies')
    print(f'📅 Date: {data[\"date\"]}')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Exchange rates downloaded"
else
    print_error "Failed to download exchange rates"
fi

echo ""
echo "=========================================="
echo "Step 2: Format and Import Exchange Rates"
echo "=========================================="
docker exec trade-api python -c "
import sys
sys.path.insert(0, '/app')
from src.database import db
from src.models import ExchangeRate
import json
from datetime import datetime

try:
    with open('/app/data/archive/usd/exchange_rates_latest.json', 'r') as f:
        data = json.load(f)
    
    session = db.get_session()
    count = 0
    
    base = data.get('base', 'USD')
    date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    rates = data.get('rates', {})
    
    for currency, rate in rates.items():
        # Check if record already exists
        existing = session.query(ExchangeRate).filter_by(
            base_currency=base,
            quote_currency=currency,
            date=date
        ).first()
        
        if not existing:
            record = ExchangeRate(
                date=date,
                base_currency=base,
                quote_currency=currency,
                rate=rate,
                close_price=rate
            )
            session.add(record)
            count += 1
    
    session.commit()
    session.close()
    print(f'✅ Imported {count} new exchange rate records')
except Exception as e:
    session.rollback()
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Exchange rates imported"
else
    print_error "Failed to import exchange rates"
fi

echo ""
echo "=========================================="
echo "Step 3: Download WTI/Brent Oil Data"
echo "=========================================="
echo "Downloading historical oil price data..."
cd /home/tony/CascadeProjects/trade
python3 download_data.py

if [ $? -eq 0 ]; then
    print_success "Oil data downloaded and formatted"
else
    print_error "Failed to download oil data"
fi

echo ""
echo "=========================================="
echo "Step 4: Import Oil Data"
echo "=========================================="
docker exec trade-api python scripts/import_wti_brent.py

if [ $? -eq 0 ]; then
    print_success "Oil data imported"
else
    print_error "Failed to import oil data"
fi

echo ""
echo "=========================================="
echo "Step 5: Run Data Quality Verification"
echo "=========================================="
docker exec trade-api python scripts/data_quality_agent.py

echo ""
echo "=========================================="
echo "Step 6: System Health Check"
echo "=========================================="
HEALTH_RESPONSE=$(curl -s http://localhost:9000/api/health)
echo "$HEALTH_RESPONSE" | python3 -m json.tool

echo ""
echo "=========================================="
echo "Manual Update Complete"
echo "=========================================="
echo ""
print_success "All manual update steps completed"
echo ""
echo "Next steps:"
echo "1. Review the data quality validation results above"
echo "2. Check the API health status"
echo "3. Test the endpoints to verify data is accessible"
echo ""
echo "Useful commands:"
echo "  - Check exchange rates: curl 'http://localhost:9000/api/exchange_rates/THB'"
echo "  - Check oil data: curl 'http://localhost:9000/api/commodity_prices/OIL?period=1w'"
echo "  - System health: curl 'http://localhost:9000/api/health'"
