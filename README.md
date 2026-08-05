
---

**Last Updated:** 2026-08-04
# Dollar Price Database

A Python-based system for tracking historical dollar price data including USD exchange rates, Dollar Index (DXY), and commodity prices.

## Documentation

**[Documentation Portal](docs/PORTAL.md)** - Unified documentation hub with guided navigation  
**[Documentation Index](docs/INDEX.md)** - Complete documentation navigation

### Core Documentation
- **[Architecture](docs/core/ARCHITECTURE.md)** - System architecture, components, and technical design
- **[API Guide](docs/core/API_GUIDE.md)** - Complete API reference and examples
- **[Deployment](docs/core/DEPLOYMENT.md)** - Deployment and configuration
- **[Troubleshooting](docs/core/TROUBLESHOOTING.md)** - Common issues, solutions, and FAQ
- **[Decision Log](docs/core/DECISION_LOG.md)** - Technical decisions and rationale

### Feature Documentation
- **[Signals](docs/features/signals/SIGNALS.md)** - Trading signals system
- **[Backtesting](docs/features/backtesting/BACKTESTING.md)** - Backtesting system guide
- **[WebSocket](docs/features/websocket/WEBSOCKET.md)** - WebSocket implementation
- **[User Interfaces](docs/features/ui/)** - TradeCanvas, Wick UI, Trading Terminal
- **[Automation](docs/features/automation/AUTOMATION_QUICK_START.md)** - Automation quick start

### Data & Reference
- **[Data Sources](docs/data/DATA_SOURCES.md)** - Historical data source documentation
- **[Project Plan](docs/reference/PROJECT_PLAN.md)** - Project vision, phases, timeline
- **[Visualization Guide](docs/core/VISUALIZATION_GUIDE.md)** - Interactive charting system

## �🚀 Quick Start

### Current Status
- ✅ Database tables created and optimized
- ✅ Sample data imported (EUR, GBP, DXY, GOLD, OIL)
- ✅ Historical data sources identified and documented
- ✅ Download tools implemented
- ✅ CLI tool ready for use
- ✅ Interactive visualization system with Plotly
- ✅ Automated data download and import scheduling system
- ✅ Database setup automation wizard
- ✅ Additional currency pairs (JPY, CAD, CHF, AUD, NZD)
- ✅ Additional commodities (Silver, Copper, Natural Gas, Agricultural)

### Immediate Actions
```bash
# 1. Run database setup wizard (first-time setup)
python3 cli.py setup

# 2. Download sample historical data
python3 download_data.py

# 3. Download additional currency pairs
python3 download_additional_currencies.py

# 4. Download additional commodities
python3 download_additional_commodities.py

# 5. Import downloaded data
python cli.py import commodity_prices data/imported/wti_formatted.csv
python cli.py import commodity_prices data/imported/brent_formatted.csv
python cli.py import exchange_rates data/imported/jpy_formatted.csv
python cli.py import commodity_prices data/imported/xag_formatted.csv

# 6. Query the data
python cli.py query commodity_prices --commodity OIL
python cli.py query exchange_rates --currency JPY
```

## Features

- **Multi-type Data Support**: Track exchange rates, Dollar Index, and commodity prices
- **PostgreSQL Database**: Robust relational database with optimized indexes
- **Database Setup Wizard**: Automated database initialization and configuration
- **Manual CSV Import**: Easy data import from CSV files
- **Query & Analysis**: Built-in functions for data retrieval and performance analysis
- **Flexible Schema**: Supports OHLCV (Open, High, Low, Close, Volume) data
- **Historical Data Sources**: Access to decades of free financial data
- **Interactive Visualization**: Plotly-based charts for price history and analysis
- **Automated Scheduling**: Hands-off automated data download and import system
- **Extended Currency Coverage**: JPY, CAD, CHF, AUD, NZD in addition to EUR, GBP
- **Extended Commodity Coverage**: Silver, Copper, Natural Gas, Wheat, Corn, Soy

## Project Structure

```
trade/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database connection and configuration
│   ├── importer.py          # CSV import functionality
│   ├── queries.py           # Query and analysis functions
│   ├── visualization.py     # Interactive charting with Plotly
│   ├── scheduler.py         # Job scheduling and automation
│   ├── notifications.py     # Error notifications and status logging
│   └── logging_config.py    # Logging configuration
├── scripts/
│   ├── auto_update.py       # Main automation script
│   ├── setup_database.py    # Database setup wizard
│   ├── deploy-mcp-config.sh # Deploy MCP server configuration
│   ├── generate-mcp-configs.py # Generate Devin CLI MCP configs
│   ├── validate-configs.sh  # Validate configuration consistency
│   ├── update-changelog.sh  # Quick changelog updates
│   ├── changelog-manager.py # Advanced changelog management
│   └── README.md            # Scripts documentation
├── config/
│   ├── data_sources.yml     # Data source and schedule configuration
│   ├── signals.yml          # Trading signals configuration
│   ├── backtesting.yml      # Backtesting system configuration
│   ├── api.yml              # API server configuration
│   └── infrastructure.yml   # Infrastructure SSOT configuration
├── docs/
│   ├── INDEX.md             # Documentation index and navigation
│   ├── PORTAL.md            # Unified documentation portal
│   ├── ARCHIVE_RETENTION_POLICY.md # Archive management guidelines
│   ├── core/                # Core system documentation
│   │   ├── ARCHITECTURE.md  # System architecture and design
│   │   ├── API_GUIDE.md     # Complete API reference
│   │   ├── DEPLOYMENT.md    # Deployment and configuration
│   │   ├── TROUBLESHOOTING.md # Common issues and solutions
│   │   ├── DECISION_LOG.md  # Technical decisions and rationale
│   │   └── VISUALIZATION_GUIDE.md # Interactive charting system
│   ├── features/            # Feature-specific documentation
│   │   ├── signals/         # Trading signals system
│   │   ├── backtesting/     # Backtesting system
│   │   ├── websocket/       # WebSocket implementation
│   │   ├── ui/              # User interfaces (TradeCanvas, Wick, Terminal)
│   │   └── automation/      # Automation system
│   ├── data/                # Data documentation
│   │   └── DATA_SOURCES.md  # Historical data source documentation
│   ├── getting-started/     # Getting started guides
│   │   └── quickstart.md    # Quick start guide
│   ├── knowledge/           # Knowledge base and insights
│   │   ├── architecture/    # Architecture knowledge
│   │   ├── operations/     # Operations knowledge
│   │   ├── troubleshooting/ # Troubleshooting knowledge
│   │   └── best-practices/  # Best practices
│   ├── workflows/           # Workflow procedures
│   └── reference/           # Reference documentation
│       └── PROJECT_PLAN.md  # Project vision, phases, timeline
├── docs-archive/            # Archived historical documentation
│   ├── DEV_FEEDBACK_LOOP_ANALYSIS.md
│   ├── DOCUMENTATION_STRATEGY.md
│   ├── FEEDBACK_LOOP_IMPLEMENTATION.md
│   ├── HANDS_OFF_DEV_STRATEGY.md
│   └── PROJECT_COMPLETION_SUMMARY.md
├── data/
│   ├── templates/           # CSV template files
│   ├── archive/             # Temporary download area (gitignore)
│   └── imported/            # Successfully imported data (gitignore)
├── tests/                   # Test suite
│   └── __pycache__/         # Test cache (gitignore)
├── .github/
│   └── workflows/           # GitHub Actions workflows
├── .devin/
│   ├── skills/              # Devin AI skills
│   │   ├── browser-helper/  # Browser automation helper
│   │   ├── config-helper/   # Configuration management
│   │   ├── remote-access/   # Remote access management
│   │   └── trade-verify/    # System verification
│   ├── mcp-remote-exec-wrapper.py # MCP wrapper script
│   └── remote-exec-wrapper.sh # Remote execution wrapper
├── examples/                # Example scripts and configurations
├── logs/                    # Automation and status logs (gitignore)
├── cli.py                   # Command-line interface
├── download_data.py         # Historical data downloader
├── download_thb_data.py     # THB data downloader
├── download_additional_currencies.py # Additional currency data downloader
├── download_additional_commodities.py # Additional commodity data downloader
├── setup.sh                 # Setup script
├── deploy.sh                # Deployment script
├── requirements.txt         # Python dependencies
├── CONFIGURATION_MANAGEMENT.md # Configuration management guide
├── CHANGELOG.md             # Project changelog
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker container configuration
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### 2. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb dollar_prices

# Or using psql
psql -U postgres
CREATE DATABASE dollar_prices;
\q
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Initialize Database
```bash
python -c "from src.database import db; db.init_db()"
```

## Usage

### Command-Line Interface

```bash
# Import data
python cli.py import exchange_rates data/exchange_rates.csv
python cli.py import dollar_index data/dxy_data.csv
python cli.py import commodity_prices data/commodities.csv

# Query data
python cli.py query exchange_rates --currency EUR
python cli.py query dollar_index
python cli.py query commodity_prices --commodity GOLD

# Analyze performance
python cli.py analyze currency --currency EUR --start-date 2024-01-01 --end-date 2024-12-31
python cli.py analyze dxy --start-date 2024-01-01 --end-date 2024-12-31

# List available data
python cli.py list currencies
python cli.py list commodities

# Generate charts
python cli.py chart currency --currency EUR --output charts/eur_usd.html
python cli.py chart dxy --output charts/dxy.html
python cli.py chart commodity --commodity GOLD --output charts/gold.html
```

### Automated Data Updates

The system includes a hands-off automation system for scheduled data downloads and imports:

```bash
# Test automation (dry run)
python scripts/auto_update.py --run-once --dry-run

# Check automation status
python scripts/auto_update.py --status

# Run all jobs once
python scripts/auto_update.py --run-once

# Start continuous scheduler
python scripts/auto_update.py --scheduled
```

**Key Features:**
- Configurable data sources and schedules in `config/data_sources.yml`
- Automatic retry logic with exponential backoff
- Error notifications via email
- Comprehensive status logging
- Pre-configured for WTI Oil, Brent Oil, ECB Exchange Rates, DXY, and Gold

For detailed setup and configuration, see [docs/AUTOMATION_GUIDE.md](docs/AUTOMATION_GUIDE.md) or [docs/AUTOMATION_QUICK_START.md](docs/AUTOMATION_QUICK_START.md).
python cli.py chart exchange_rates --currency EUR --period 1y
python cli.py chart commodity_prices --commodity GOLD --period 6m
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m
python cli.py chart dollar_index --period 1y
```

### Python API

```python
from src.queries import get_queries, get_analysis
from datetime import date

# Get query instance
queries = get_queries()

# Get exchange rates for EUR
df = queries.get_exchange_rates('EUR')

# Get latest exchange rate
latest = queries.get_latest_exchange_rate('EUR')

# Get Dollar Index data
dxy_df = queries.get_dollar_index()

# Get commodity prices
gold_df = queries.get_commodity_prices(commodity='GOLD')

# Analysis
analysis = get_analysis()
performance = analysis.calculate_currency_performance('EUR', date(2024,1,1), date(2024,12,31))
currencies = analysis.get_available_currencies()
commodities = analysis.get_available_commodities()
```

### Visualization

Generate interactive charts for price history and analysis:

```bash
# Exchange rate charts
python cli.py chart exchange_rates --currency EUR --period 1y
python cli.py chart exchange_rates --currency GBP --period 6m --chart-type candlestick
python cli.py chart exchange_rates --currency JPY --period 3m --volume

# Commodity price charts
python cli.py chart commodity_prices --commodity GOLD --period 1y
python cli.py chart commodity_prices --commodity OIL --period 6m --chart-type candlestick

# Currency comparison
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m
python cli.py chart comparison --currencies EUR,GBP,JPY --period 3m --performance

# Dollar Index
python cli.py chart dollar_index --period 1y

# Save chart to HTML
python cli.py chart exchange_rates --currency EUR --period 1y --output chart.html
```

For detailed visualization documentation, see **VISUALIZATION_GUIDE.md**.

### Direct SQL Queries
```python
# Using PostgreSQL MCP server
mcp_call_tool("postgres", "query", {"sql": "SELECT * FROM exchange_rates WHERE quote_currency = 'EUR' ORDER BY date DESC LIMIT 10"})
```

## Historical Data Sources

### Quick Overview
- **Exchange Rates**: ECB (40+ currencies), FRED (major pairs), HistData.com (66 pairs with OHLCV)
- **Dollar Index**: MarketWatch (OHLCV), Investing.com, Kaggle (2001-2022)
- **Gold Prices**: Free Gold API (768 years! 1258-2025), Kaggle (2004-present)
- **Oil Prices**: DataHub.io (WTI since 1986, Brent since 1987), FRED

### Download Data
```bash
# Download sample historical data (WTI & Brent oil)
python3 download_data.py

# Data will be downloaded to data/archive/, formatted, and moved to data/imported/
# Raw files are automatically cleaned up after formatting

# For comprehensive source information, see:
# docs/DATA_SOURCES.md
```

### Data Sources Summary
| Data Type | Best Free Source | History | Format |
|-----------|-----------------|---------|--------|
| Exchange Rates | ECB | 1999-present | CSV |
| DXY | MarketWatch | Several decades | CSV (OHLCV) |
| Gold | Free Gold API | 1258-2025 | CSV |
| Oil (WTI/Brent) | DataHub.io | 1986/1987-present | CSV |

## CSV File Formats

### Exchange Rates
```csv
date,quote_currency,rate,open_price,high_price,low_price,close_price,volume
2024-01-01,EUR,0.9150,0.9145,0.9160,0.9130,0.9155,1000000
```

### Dollar Index
```csv
date,value,open_price,high_price,low_price,close_price,volume
2024-01-01,101.5,101.3,101.8,101.2,101.6,50000000
```

### Commodity Prices
```csv
date,commodity,symbol,price,unit,open_price,high_price,low_price,close_price,volume
2024-01-01,GOLD,XAUUSD,2050.50,oz,2048.00,2055.00,2045.00,2052.00,150000
```

Templates are available in `data/templates/`

## Database Schema

### Tables
- **exchange_rates**: USD exchange rates to other currencies (indexed by date/currency)
- **dollar_index**: USD Dollar Index (DXY) values (unique date constraint)
- **commodity_prices**: Commodity prices in USD (indexed by date/symbol)

All tables support OHLCV data structure for detailed analysis.

## Data Management

### Download Workflow
```bash
# 1. Download data to archive/
python3 download_data.py

# 2. Format and validate (automatic in download script)
# Raw files are automatically cleaned up after formatting

# 3. Import to database
python cli.py import commodity_prices data/imported/wti_formatted.csv

# 4. Clean up imported files (optional)
rm data/imported/wti_formatted.csv
```

### Data Lifecycle
1. **Download** → `data/archive/` (temporary)
2. **Format** → Match templates in `data/templates/`
3. **Import** → Database via CLI or Python API
4. **Cleanup** → Delete from `data/archive/` after successful import
5. **Archive** → Keep only templates in git, ignore data files

## Current Database Status

- **Tables**: 3 (exchange_rates, dollar_index, commodity_prices)
- **Indexes**: 5 (optimized for common queries)
- **Sample Data**: EUR/USD, GBP/USD, DXY, GOLD, OIL
- **Historical Data**: WTI (10K+ records), Brent (9K+ records) downloaded

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running
- Check database credentials in `.env` file
- Verify database exists: `psql -l`

### Import Errors
- Validate CSV format matches templates
- Check date format is YYYY-MM-DD
- Ensure required columns are present

### Performance
- Database indexes are automatically created
- For large datasets, consider batch imports
- Use date ranges in queries to limit data

## License

MIT License - feel free to use and modify.

## Additional Documentation

- **VISUALIZATION_GUIDE.md** - Complete guide to interactive charting system
- **docs/DATA_SOURCES.md** - Comprehensive historical data source guide
- **data/templates/** - CSV format templates for each data type
