
---

**Last Updated: 2026-08-04
# Quick Start Guide

Get the trade system up and running in minutes.

---

## Prerequisites

- Python 3.14+
- PostgreSQL database
- Docker (for containerized deployment)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd trade
```

### 2. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Create PostgreSQL database
createdb trade

# Run database migrations
python scripts/migrate_database.py
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

---

## First Steps

### Download Sample Data

```bash
python3 download_data.py
```

This downloads historical data for:
- USD exchange rates (EUR, GBP, JPY, THB)
- Dollar Index (DXY)
- Commodity prices (GOLD, OIL)

### Import Data

```bash
# Import commodity prices
python cli.py import commodity_prices data/imported/wti_formatted.csv
python cli.py import commodity_prices data/imported/brent_formatted.csv

# Import exchange rates
python cli.py import exchange_rates data/imported/thb_formatted.csv
```

### Query Data

```bash
# Query commodity prices
python cli.py query commodity_prices --commodity OIL

# Query exchange rates
python cli.py query exchange_rates --currency THB
```

---

## Start the API

### Development

```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`

---

## Verify Installation

### Check API Health

```bash
curl http://localhost:8000/api/health
```

### Check Available Currencies

```bash
curl http://localhost:8000/api/available/currencies
```

### Query THB Data

```bash
curl http://localhost:8000/api/exchange_rates/THB?period=1y&limit=1000
```

---

## Next Steps

- [Architecture](../core/ARCHITECTURE.md) - Learn about system architecture
- [API Guide](../core/API_GUIDE.md) - Complete API reference
- [Signals](../features/signals/SIGNALS_QUICKSTART.md) - Set up trading signals
- [Visualization](../core/VISUALIZATION_GUIDE.md) - Create interactive charts
- [Deployment](../core/DEPLOYMENT.md) - Production deployment guide

---

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify database exists
psql -l | grep trade
```

### Import Error

```bash
# Check CSV file format
head data/imported/thb_formatted.csv

# Verify column headers match expected format
```

### API Not Starting

```bash
# Check port is not in use
lsof -i :8000

# Check environment variables
cat .env
```

---

**Last Updated:** 2026-08-04  
**Version:** 1.0  
**Related:** [Main README](../../README.md)