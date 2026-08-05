
---

**Last Updated: 2026-08-04
# Trading Terminal Quick Start Guide

## Quick Access

**URL**: `http://tony-omen.local:8080/apps/trade/terminal/`

## What You'll See

The Trading Terminal provides a modern dashboard for monitoring:

- **22 Currencies**: EUR, GBP, JPY, CHF, CAD, AUD, NZD, CNY, INR, MXN, BRL, KRW, SGD, HKD, NOK, SEK, DKK, PLN, TRY, ZAR, RON, HUF
- **Commodities**: OIL, GOLD, SILVER, COPPER
- **Dollar Index**: DXY

## Default Watchlist

The terminal loads with these assets by default:
- EUR (Euro)
- GBP (British Pound)
- JPY (Japanese Yen)
- GOLD (Gold)
- OIL (Crude Oil)
- DXY (Dollar Index)

## Basic Usage

### 1. View Market Data
- Open the URL in your browser
- See current prices and 24-hour changes
- View price charts for selected assets

### 2. Customize Watchlist
- **Add**: Click any asset in the "Available Assets" section
- **Remove**: Click the "×" next to any asset in your watchlist
- **Select**: Click an asset to view its detailed chart

### 3. Manage Portfolio
- Use the portfolio form to add holdings
- Enter asset symbol, quantity, and average cost
- View automatic P&L calculations

### 4. Refresh Data
- Click the "Refresh" button to update market data
- Data auto-refreshes every 60 seconds
- Last update time shown in header

## Data Source

The terminal connects to your existing trade API with:
- **168K+ historical records** in the database
- **Real-time data** from the Trade API
- **Automatic fallback** if data is temporarily unavailable

## Features

✅ **Market Dashboard** - Real-time prices and charts
✅ **Watchlist** - Customizable asset monitoring
✅ **Portfolio Tracker** - Holdings and performance tracking
✅ **Trading Signals** - Technical analysis signals (when sufficient data available)
✅ **Responsive Design** - Works on desktop and mobile
✅ **Auto-refresh** - Data updates every 60 seconds

## Troubleshooting

### Page Not Loading
```bash
# Check if container is running
docker ps | grep trading-terminal

# Restart if needed
cd /home/tony/CascadeProjects/chaba/stacks/web
docker compose restart trading-terminal
```

### No Data Showing
```bash
# Check API connectivity
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/health

# Check trade-api container
docker logs trade-api
```

### Management Commands
```bash
# Start terminal
cd /home/tony/CascadeProjects/chaba/stacks/web
docker compose up -d trading-terminal

# Stop terminal
docker compose stop trading-terminal

# View logs
docker logs -f trading-terminal

# Rebuild after changes
docker compose build --no-cache trading-terminal
docker compose up -d trading-terminal
```

## Next Steps

- Customize your watchlist with preferred assets
- Add your actual portfolio holdings
- Explore different assets from the available universe
- Check back for trading signals (requires 50+ data points per asset)

## Full Documentation

See [TRADING_TERMINAL_INTEGRATION.md](TRADING_TERMINAL_INTEGRATION.md) for complete technical documentation.
