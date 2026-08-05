
---

**Last Updated:** 2026-08-05
# Trading Data API Guide

## Overview

The Trading Data API provides REST endpoints for accessing dollar price data including exchange rates, dollar index (DXY), and commodity prices. The API is built with FastAPI and includes comprehensive documentation via Swagger UI.

**Base URL:** `http://tony-omen.local:8080/apps/trade/api` (when mounted)
**Direct URL:** `http://localhost:8000` (when running standalone)

## Quick Start

### Starting the Server

**Development Mode (with auto-reload):**
```bash
python scripts/run_api.py --mode development
```

**Production Mode:**
```bash
python scripts/run_api.py --mode production
```

**Custom host/port:**
```bash
python scripts/run_api.py --host 0.0.0.0 --port 8000
```

**Using custom config:**
```bash
python scripts/run_api.py --config /path/to/config.yml
```

### Accessing Documentation

Once the server is running:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## API Endpoints

### 1. Health Check

Check system health and database status.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "checks": {
    "database_connection": true,
    "database_tables": true,
    "data_freshness": true,
    "data_volume": true,
    "data_quality": true,
    "system_resources": true
  },
  "issues": [],
  "warnings": []
}
```

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

### 2. Data Quality Report

Get comprehensive data quality metrics.

**Endpoint:** `GET /api/data_quality`

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "summary": {
    "total_records": 15000,
    "tables_with_data": 3
  },
  "tables": {
    "exchange_rates": { ... },
    "dollar_index": { ... },
    "commodity_prices": { ... }
  },
  "issues": [],
  "warnings": [],
  "recommendations": []
}
```

**Example:**
```bash
curl http://localhost:8000/api/data_quality
```

---

### 3. Available Currencies

List all available currencies in the database.

**Endpoint:** `GET /api/available/currencies`

**Response:**
```json
{
  "items": ["EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"],
  "count": 7
}
```

**Example:**
```bash
curl http://localhost:8000/api/available/currencies
```

---

### 4. Available Commodities

List all available commodities in the database.

**Endpoint:** `GET /api/available/commodities`

**Response:**
```json
{
  "items": ["GOLD", "SILVER", "OIL", "COPPER"],
  "count": 4
}
```

**Example:**
```bash
curl http://localhost:8000/api/available/commodities
```

---

### 5. Exchange Rates

Get exchange rate data for a specific currency.

**Endpoint:** `GET /api/exchange_rates/{currency}`

**Path Parameters:**
- `currency` (required): Currency code (e.g., EUR, GBP, JPY)

**Query Parameters:**
- `period` (optional): Time period - `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of records (1-10000)
- `offset` (optional): Number of records to skip (default: 0)

**Note:** Cannot specify both `period` and `start_date`/`end_date`.

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "base_currency": "USD",
      "quote_currency": "EUR",
      "rate": 0.92,
      "open": 0.918,
      "high": 0.925,
      "low": 0.915,
      "close": 0.92,
      "volume": null
    }
  ],
  "count": 100,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

**Examples:**

Get last week of EUR data:
```bash
curl "http://localhost:8000/api/exchange_rates/EUR?period=1w"
```

Get data for a specific date range:
```bash
curl "http://localhost:8000/api/exchange_rates/GBP?start_date=2024-01-01&end_date=2024-01-15"
```

Get with pagination:
```bash
curl "http://localhost:8000/api/exchange_rates/JPY?limit=50&offset=0"
```

---

### 6. Latest Exchange Rate

Get the most recent exchange rate for a currency.

**Endpoint:** `GET /api/exchange_rates/{currency}/latest`

**Path Parameters:**
- `currency` (required): Currency code (e.g., EUR, GBP, JPY)

**Response:**
```json
{
  "date": "2024-01-15",
  "base_currency": "USD",
  "quote_currency": "EUR",
  "rate": 0.92,
  "open": 0.918,
  "high": 0.925,
  "low": 0.915,
  "close": 0.92,
  "volume": null
}
```

**Example:**
```bash
curl http://localhost:8000/api/exchange_rates/EUR/latest
```

---

### 7. Dollar Index (DXY)

Get Dollar Index data.

**Endpoint:** `GET /api/dollar_index`

**Query Parameters:**
- `period` (optional): Time period - `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of records (1-10000)
- `offset` (optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "value": 102.5,
      "open": 102.3,
      "high": 102.8,
      "low": 102.1,
      "close": 102.5,
      "volume": null
    }
  ],
  "count": 365,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

**Examples:**

Get last month of DXY data:
```bash
curl "http://localhost:8000/api/dollar_index?period=1m"
```

Get data for a specific date range:
```bash
curl "http://localhost:8000/api/dollar_index?start_date=2024-01-01&end_date=2024-01-15"
```

---

### 8. Latest Dollar Index

Get the most recent Dollar Index value.

**Endpoint:** `GET /api/dollar_index/latest`

**Response:**
```json
{
  "date": "2024-01-15",
  "value": 102.5,
  "open": 102.3,
  "high": 102.8,
  "low": 102.1,
  "close": 102.5,
  "volume": null
}
```

**Example:**
```bash
curl http://localhost:8000/api/dollar_index/latest
```

---

### 9. Commodity Prices

Get commodity price data.

**Endpoint:** `GET /api/commodity_prices/{commodity}`

**Path Parameters:**
- `commodity` (required): Commodity name (e.g., GOLD, SILVER, OIL)

**Query Parameters:**
- `period` (optional): Time period - `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of records (1-10000)
- `offset` (optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "commodity": "GOLD",
      "symbol": "XAUUSD",
      "price": 2050.50,
      "unit": "oz",
      "open": 2045.00,
      "high": 2055.00,
      "low": 2040.00,
      "close": 2050.50,
      "volume": null
    }
  ],
  "count": 365,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

**Examples:**

Get last week of gold prices:
```bash
curl "http://localhost:8000/api/commodity_prices/GOLD?period=1w"
```

Get oil prices for a specific date range:
```bash
curl "http://localhost:8000/api/commodity_prices/OIL?start_date=2024-01-01&end_date=2024-01-15"
```

---

### 10. Latest Commodity Price

Get the most recent commodity price.

**Endpoint:** `GET /api/commodity_prices/{commodity}/latest`

**Path Parameters:**
- `commodity` (required): Commodity name (e.g., GOLD, SILVER, OIL)

**Response:**
```json
{
  "date": "2024-01-15",
  "commodity": "GOLD",
  "symbol": "XAUUSD",
  "price": 2050.50,
  "unit": "oz",
  "open": 2045.00,
  "high": 2055.00,
  "low": 2040.00,
  "close": 2050.50,
  "volume": null
}
```

**Example:**
```bash
curl http://localhost:8000/api/commodity_prices/GOLD/latest
```

---

### 11. Performance Analysis

Get performance analysis for a currency over a time period.

**Endpoint:** `GET /api/performance/{currency}`

**Path Parameters:**
- `currency` (required): Currency code (e.g., EUR, GBP, JPY)

**Query Parameters:**
- `period` (optional): Time period - `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`
- `start_date` (optional): Start date in YYYY-MM-DD format (required if not using period)
- `end_date` (optional): End date in YYYY-MM-DD format (required if not using period)

**Response:**
```json
{
  "currency": "EUR",
  "start_date": "2024-01-01",
  "end_date": "2024-01-15",
  "start_rate": 0.91,
  "end_rate": 0.92,
  "change": 0.01,
  "change_percent": 1.0989,
  "high": 0.925,
  "low": 0.905,
  "range": 0.02
}
```

**Examples:**

Get performance over the last month:
```bash
curl "http://localhost:8000/api/performance/EUR?period=1m"
```

Get performance for a specific date range:
```bash
curl "http://localhost:8000/api/performance/GBP?start_date=2024-01-01&end_date=2024-01-15"
```

---

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters or validation error
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "error": "Error message",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Example Error:**
```json
{
  "error": "Invalid currency code: XYZ",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Configuration

### Environment Variables

The API can be configured using environment variables:

- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `API_WORKERS`: Number of workers (default: 1)
- `API_LOG_LEVEL`: Log level (default: info)

### Configuration File

The API can be configured via `config/api.yml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 1
  reload: false
  log_level: "info"

cors:
  enabled: true
  allow_origins:
    - "http://localhost:8080"
    - "http://tony-omen.local:8080"
  allow_credentials: true
  allow_methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  allow_headers:
    - "Content-Type"
    - "Authorization"
    - "X-Requested-With"
```

---

## Integration with Trading UI

### Mounting the API

To mount the API at `/apps/trade/api` in your existing trading infrastructure:

```python
from fastapi import FastAPI
from src.api import app as trading_api

main_app = FastAPI()
main_app.mount("/apps/trade/api", trading_api)
```

### CORS Configuration

The API is configured to allow CORS from the trading UI. Update the `config/api.yml` to add your UI domain:

```yaml
cors:
  allow_origins:
    - "http://tony-omen.local:8080"
    - "http://your-ui-domain.com"
```

### Example JavaScript Integration

```javascript
// Fetch latest EUR exchange rate
async function getLatestEUR() {
  const response = await fetch('http://localhost:8000/api/exchange_rates/EUR/latest');
  const data = await response.json();
  console.log(data);
  return data;
}

// Fetch DXY data for the last month
async function getDXYData() {
  const response = await fetch('http://localhost:8000/api/dollar_index?period=1m');
  const data = await response.json();
  console.log(data);
  return data;
}

// Fetch gold prices with pagination
async function getGoldPrices() {
  const response = await fetch('http://localhost:8000/api/commodity_prices/GOLD?limit=100&offset=0');
  const data = await response.json();
  console.log(data);
  return data;
}
```

### Example Python Integration

```python
import requests

# Get latest exchange rate
response = requests.get('http://localhost:8000/api/exchange_rates/EUR/latest')
data = response.json()
print(data)

# Get DXY data for a date range
params = {
    'start_date': '2024-01-01',
    'end_date': '2024-01-15'
}
response = requests.get('http://localhost:8000/api/dollar_index', params=params)
data = response.json()
print(data)

# Get performance analysis
response = requests.get('http://localhost:8000/api/performance/GBP?period=1m')
data = response.json()
print(data)
```

---

## Authentication

Currently, the API does not require authentication. If you need to add authentication:

1. Update the API to include authentication middleware
2. Configure your authentication provider (OAuth2, JWT, etc.)
3. Update the CORS configuration to allow authentication headers

---

## Rate Limiting

Rate limiting can be enabled in `config/api.yml`:

```yaml
rate_limiting:
  enabled: true
  requests_per_minute: 60
  requests_per_hour: 1000
```

---

## Testing

### Test with curl

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test exchange rates
curl http://localhost:8000/api/exchange_rates/EUR/latest

# Test dollar index
curl http://localhost:8000/api/dollar_index?period=1w

# Test commodity prices
curl http://localhost:8000/api/commodity_prices/GOLD/latest
```

### Test with Python

```python
import requests

base_url = "http://localhost:8000"

# Test health
response = requests.get(f"{base_url}/api/health")
print(response.json())

# Test available currencies
response = requests.get(f"{base_url}/api/available/currencies")
print(response.json())

# Test exchange rates
response = requests.get(f"{base_url}/api/exchange_rates/EUR?period=1w")
print(response.json())
```

---

## Troubleshooting

### Server won't start

1. Check if port 8000 is already in use
2. Verify database connection settings in `.env`
3. Check logs for error messages

### CORS errors

1. Verify CORS configuration in `config/api.yml`
2. Ensure your UI domain is in `allow_origins`
3. Check that credentials are allowed if needed

### Database connection errors

1. Verify database is running
2. Check connection string in `.env` file
3. Ensure database tables exist

### No data returned

1. Check if data exists in the database
2. Verify date ranges are correct
3. Check currency/commodity codes are valid

---

## Support

For issues or questions:
1. Check the Swagger UI at `/docs` for interactive testing
2. Review logs for error messages
3. Verify configuration settings

---

**Last Updated:** 2026-08-05
**Version:** 1.0  
**Related:** [Architecture](ARCHITECTURE.md)
4. Check database connectivity
