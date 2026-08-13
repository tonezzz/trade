# Manual Trade Data Workflow

## Overview
This workflow is designed for hosts that are offline frequently. All data fetching and verification is done manually when the host comes back online.

## Quick Start

### 1. Check Current Status
```bash
cd /home/tony/CascadeProjects/trade
./scripts/quick_verify.sh
```

This will show:
- Container status
- API health
- Data freshness
- Record counts
- Sample data verification

### 2. Update Data (when stale)
```bash
cd /home/tony/CascadeProjects/trade
./scripts/manual_update.sh
```

This will:
- Download fresh exchange rates
- Download WTI/Brent oil data
- Import all data into database
- Run data quality verification
- Show system health status

## Manual Workflow Steps

### Step 1: Start Trade API (if not running)
```bash
cd /home/tony/CascadeProjects/trade
docker compose up -d trade-api
```

### Step 2: Download Exchange Rates
```bash
# Download current rates from open.er-api.com
docker exec trade-api python -c "
import requests, json
response = requests.get('https://open.er-api.com/v6/latest/USD')
data = response.json()
with open('/app/data/archive/usd/exchange_rates_latest.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f'Downloaded {len(data[\"rates\"])} currency rates')
"
```

### Step 3: Import Exchange Rates
```bash
docker exec trade-api python -c "
import sys, json
sys.path.insert(0, '/app')
from src.database import db
from src.models import ExchangeRate
from datetime import datetime

with open('/app/data/archive/usd/exchange_rates_latest.json', 'r') as f:
    data = json.load(f)

session = db.get_session()
date = datetime.strptime(data['date'], '%Y-%m-%d').date()
count = 0

for currency, rate in data['rates'].items():
    existing = session.query(ExchangeRate).filter_by(
        base_currency='USD', quote_currency=currency, date=date
    ).first()
    if not existing:
        record = ExchangeRate(date=date, base_currency='USD', 
                           quote_currency=currency, rate=rate, close_price=rate)
        session.add(record)
        count += 1

session.commit()
print(f'Imported {count} new exchange rates')
session.close()
"
```

### Step 4: Download Oil Data
```bash
cd /home/tony/CascadeProjects/trade
python3 download_data.py
```

### Step 5: Import Oil Data
```bash
docker exec trade-api python scripts/import_wti_brent.py
```

### Step 6: Verify Data Quality
```bash
docker exec trade-api python scripts/data_quality_agent.py
```

### Step 7: Check API Health
```bash
curl http://localhost:9000/api/health | python3 -m json.tool
```

## Available Data Sources

### Exchange Rates
- **Source**: open.er-api.com
- **Currencies**: 23 major currencies (AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HKD, HUF, INR, JPY, KRW, MXN, NOK, NZD, PLN, SEK, SGD, THB, TRY, ZAR)
- **Frequency**: Daily updates recommended

### Commodity Prices
- **Source**: GitHub datasets (oil-prices)
- **Commodities**: WTI crude oil, Brent crude oil
- **Frequency**: Weekly updates sufficient

### Dollar Index
- **Source**: FRED API (currently broken)
- **Status**: Manual updates not currently available
- **Alternative**: Consider manual entry or different data source

## API Endpoints

### Health Check
```bash
curl http://localhost:9000/api/health
```

### Exchange Rates
```bash
# Latest THB rate
curl "http://localhost:9000/api/exchange_rates/THB?limit=1"

# EUR rates for last month
curl "http://localhost:9000/api/exchange_rates/EUR?period=1m"
```

### Commodity Prices
```bash
# Latest oil prices (both WTI and BRENT)
curl "http://localhost:9000/api/commodity_prices/OIL?limit=2"

# WTI specific (use commodity name)
curl "http://localhost:9000/api/commodity_prices/OIL?period=1w"
```

### Available Data
```bash
# List available currencies
curl http://localhost:9000/api/available/currencies

# List available commodities
curl http://localhost:9000/api/available/commodities
```

## Troubleshooting

### Container Not Running
```bash
# Check status
docker ps | grep trade-api

# Start if needed
cd /home/tony/CascadeProjects/trade
docker compose up -d trade-api
```

### API Not Responding
```bash
# Check container logs
docker logs trade-api

# Restart container
docker restart trade-api
```

### Data Import Fails
```bash
# Check database connection
docker exec trade-api python -c "from src.database import db; print('DB OK')"

# Check data files
docker exec trade-api ls -la /app/data/imported/
```

### Data Quality Issues
```bash
# Run detailed validation
docker exec trade-api python scripts/data_quality_agent.py

# Check validation results
cat /home/tony/CascadeProjects/trade/data/quality/validation_*.json
```

## Automation Status

**DISABLED**: The automatic trade-automation container has been disabled to prevent issues when the host is offline.

**Manual Only**: All data updates must be performed manually using the scripts in this workflow.

## Best Practices

1. **Check Status First**: Always run `quick_verify.sh` before updates
2. **Update Regularly**: Update exchange rates daily when host is online
3. **Verify After Updates**: Run data quality validation after each update
4. **Monitor API Health**: Check API health status regularly
5. **Keep Records**: Note when updates were performed for tracking

## Recovery After Extended Offline

If the host has been offline for an extended period:

1. Run `quick_verify.sh` to assess data staleness
2. Run `manual_update.sh` to refresh all data
3. Consider running multiple manual updates if data is very old
4. Verify all endpoints are returning current data
5. Check data quality validation results

## Notes

- The trade-api container should remain running (restart: unless-stopped)
- Only the trade-automation container has been disabled
- Data persists in SQLite database even when host is offline
- API endpoints will return stale data if not updated regularly
- Manual workflow provides full control over when updates occur
