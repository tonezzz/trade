
---

**Last Updated:** 2026-08-05
# Trading Terminal Integration Documentation

## Overview

The Trading Terminal dashboard has been successfully integrated with the existing trade API, providing a modern web-based interface for monitoring currencies, commodities, and dollar index data. The terminal connects to the existing PostgreSQL database containing 168K+ records and provides real-time market data visualization, portfolio tracking, and watchlist management.

## Access URL

**Trading Terminal**: `http://tony-omen.local:8080/apps/trade/terminal/`

## Architecture

### Components

1. **Trading Terminal UI** (React + TypeScript + Vite)
   - Location: `/home/tony/CascadeProjects/trading-terminal`
   - Container: `trading-terminal`
   - Technology: React 19, Recharts for visualization, Tailwind CSS for styling
   - Serves static assets via nginx

2. **Trade API** (FastAPI + Python)
   - Location: `/home/tony/CascadeProjects/trade`
   - Container: `trade-api`
   - Provides REST endpoints for market data and trading signals

3. **Reverse Proxy** (Caddy)
   - Routes `/apps/trade/terminal/` to the Trading Terminal UI
   - Routes `/apps/trade/terminal/api/trade/*` to the Trade API
   - Provides SSL termination and load balancing capabilities

4. **Database** (PostgreSQL)
   - Contains 168K+ historical records
   - 22 currencies, 1 commodity (OIL), dollar index data
   - Accessed by the Trade API

## Configuration

### API Endpoints Used

The Trading Terminal connects to the following Trade API endpoints:

#### Market Data Endpoints
- `GET /api/exchange_rates/{currency}?period=1d&limit=2` - Recent exchange rate data
- `GET /api/exchange_rates/{currency}/latest` - Latest exchange rate (fallback)
- `GET /api/commodity_prices/{commodity}?period=1d&limit=2` - Recent commodity prices
- `GET /api/commodity_prices/{commodity}/latest` - Latest commodity price (fallback)
- `GET /api/dollar_index?period=1d&limit=2` - Recent dollar index data
- `GET /api/dollar_index/latest` - Latest dollar index (fallback)
- `GET /api/available/currencies` - List of available currencies
- `GET /api/available/commodities` - List of available commodities

#### Trading Signals Endpoints
- `GET /api/signals/{currency}` - Trading signals for currencies
- `GET /api/signals/commodity/{commodity}` - Trading signals for commodities
- `GET /api/signals/dollar_index` - Trading signals for dollar index

### Asset Universe

The Trading Terminal is configured with the following asset categories:

#### Currencies (22 available)
EUR, GBP, JPY, CHF, CAD, AUD, NZD, CNY, INR, MXN, BRL, KRW, SGD, HKD, NOK, SEK, DKK, PLN, TRY, ZAR, RON, HUF

#### Commodities
OIL (Crude Oil), GOLD (Gold), SILVER (Silver), COPPER (Copper)

#### Dollar Index
DXY (Dollar Index)

### Default Watchlist
EUR, GBP, JPY, GOLD, OIL, DXY

## Features Implemented

### 1. Market Dashboard
- Real-time price display for selected assets
- 24-hour price change calculations
- Automatic data refresh every 60 seconds
- Price history charts using Recharts
- Responsive design for desktop and mobile

### 2. Watchlist Management
- Customizable watchlist with add/remove functionality
- Persistent storage using localStorage
- Quick asset selection from available universe
- Real-time updates for all watchlist items

### 3. Portfolio Tracker
- Portfolio holdings management
- Automatic value calculation based on current prices
- Performance tracking (unrealized P&L)
- Asset allocation visualization
- Default portfolio: EUR (1000 units), GBP (500 units), GOLD (10 units)

### 4. API Integration
- Custom adapter for Trade API endpoints
- Automatic fallback to latest data endpoints
- Error handling with fallback sample data
- CORS handling through Vite proxy (development) and Caddy (production)

### 5. Trading Signals
- Integration with signal generation system
- Support for currency, commodity, and dollar index signals
- Technical indicator analysis
- Signal strength and confidence metrics
- Graceful handling when insufficient data is available

## Deployment

### Docker Configuration

#### Trading Terminal Container
```yaml
trading-terminal:
  container_name: trading-terminal
  build:
    context: /home/tony/CascadeProjects/trading-terminal
    dockerfile: Dockerfile
  restart: unless-stopped
  networks:
    - default
```

#### Caddy Routing
```caddy
@terminal_noslash path /apps/trade/terminal
redir @terminal_noslash /apps/trade/terminal/ 308

handle_path /apps/trade/terminal/api/trade/* {
    uri strip_prefix /apps/trade/terminal/api/trade
    reverse_proxy trade-api:8000
}

handle_path /apps/trade/terminal/* {
    reverse_proxy trading-terminal:80
}
```

### Build Process

1. **Development Build** (with Vite proxy):
   ```bash
   cd /home/tony/CascadeProjects/trading-terminal
   npm install
   npm run dev
   ```

2. **Production Build**:
   ```bash
   cd /home/tony/CascadeProjects/trading-terminal
   npm run build
   ```

3. **Docker Build**:
   ```bash
   cd /home/tony/CascadeProjects/chaba/stacks/web
   docker compose build trading-terminal
   docker compose up -d trading-terminal
   ```

### Management Commands

```bash
# Start the service
cd /home/tony/CascadeProjects/chaba/stacks/web
docker compose up -d trading-terminal

# Stop the service
docker compose stop trading-terminal

# Restart the service
docker compose restart trading-terminal

# Rebuild the service (after code changes)
docker compose build --no-cache trading-terminal
docker compose up -d trading-terminal

# View logs
docker logs -f trading-terminal

# Check container status
docker ps | grep trading-terminal
```

## Usage

### Accessing the Terminal

1. Open your web browser
2. Navigate to: `http://tony-omen.local:8080/apps/trade/terminal/`
3. The terminal will load with the default watchlist

### Managing Watchlist

1. **Add Asset**: Click on an asset in the available assets list
2. **Remove Asset**: Click the "×" button next to an asset in the watchlist
3. **Select Asset**: Click on an asset to view its detailed chart and information

### Managing Portfolio

1. **Add Holding**: Use the portfolio form to add new holdings
2. **Edit Holding**: Select an existing holding to modify quantity or cost
3. **View Performance**: Portfolio value and P&L are automatically calculated

### Refreshing Data

- Click the "Refresh" button in the header to manually update market data
- Data automatically refreshes every 60 seconds
- Last update time is displayed in the header

## Technical Details

### Custom API Adapter

The Trading Terminal uses a custom API adapter (`src/lib/tradeApiAdapter.ts`) that:

1. Maps the existing Trade API endpoints to the expected data structure
2. Handles different asset categories (currencies, commodities, dollar index)
3. Implements fallback logic when recent data is unavailable
4. Calculates 24-hour price changes from historical data
5. Integrates with the trading signals system

### Data Flow

```
User Browser → Caddy → Trading Terminal (nginx) → React App
                                     ↓
                             API Requests
                                     ↓
                             Caddy → Trade API → PostgreSQL
```

### Error Handling

- **API Unavailable**: Falls back to sample data with warning message
- **Insufficient Data**: Gracefully handles missing data points
- **Network Errors**: Shows error message and maintains last known state
- **Signal Generation**: Returns null when insufficient historical data exists

## Testing

### API Testing

```bash
# Test health endpoint
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/health

# Test available currencies
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/available/currencies

# Test exchange rate data
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/exchange_rates/EUR/latest

# Test commodity data
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/commodity_prices/OIL/latest

# Test dollar index
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/dollar_index/latest
```

### UI Testing

1. Navigate to `http://tony-omen.local:8080/apps/trade/terminal/`
2. Verify the page loads without errors
3. Check that market data is displayed
4. Test watchlist add/remove functionality
5. Test portfolio management
6. Verify data refresh functionality

## Troubleshooting

### Terminal Not Loading

**Check container status:**
```bash
docker ps | grep trading-terminal
```

**Check container logs:**
```bash
docker logs trading-terminal
```

**Check Caddy configuration:**
```bash
docker exec web caddy validate --config /etc/caddy/Caddyfile
```

### API Not Responding

**Check Trade API container:**
```bash
docker ps | grep trade-api
docker logs trade-api
```

**Test API directly:**
```bash
curl http://tony-omen.local:8080/apps/trade/api/api/health
```

### Data Not Updating

**Check network connectivity:**
```bash
docker exec trading-terminal ping trade-api
```

**Check API proxy configuration:**
```bash
curl http://tony-omen.local:8080/apps/trade/terminal/api/trade/api/health
```

### Build Errors

**Clear Docker cache:**
```bash
docker compose build --no-cache trading-terminal
```

**Check Node.js version:**
```bash
node --version  # Should be 20.x
```

## Future Enhancements

### Planned Features

1. **Enhanced Signal Display**
   - Visual signal indicators (buy/sell/hold)
   - Signal strength visualization
   - Historical signal performance tracking

2. **Advanced Charting**
   - Multiple timeframe support
   - Technical indicator overlays
   - Drawing tools and annotations

3. **Alert System**
   - Price alerts via email/webhook
   - Signal notifications
   - Custom threshold alerts

4. **Backtesting Integration**
   - Strategy backtesting interface
   - Performance comparison
   - Parameter optimization

5. **Data Export**
   - CSV export for historical data
   - Portfolio performance reports
   - Signal history export

6. **Authentication**
   - User authentication and authorization
   - Portfolio isolation per user
   - Custom watchlist persistence

### Technical Improvements

1. **Performance Optimization**
   - Implement data caching
   - Optimize bundle size (currently 584KB)
   - Add service worker for offline support

2. **Testing**
   - Add unit tests for API adapter
   - Add integration tests for UI components
   - Add E2E tests with Playwright

3. **Monitoring**
   - Add error tracking (Sentry)
   - Add performance monitoring
   - Add usage analytics

## Related Documentation

- [Trade API Guide](API_GUIDE.md) - Complete API reference
- [Deployment Documentation](DEPLOYMENT.md) - Trade API deployment details
- [Architecture Documentation](ARCHITECTURE.md) - System architecture overview
- [Trading Terminal Repository](https://github.com/Kalz99/trading-terminal) - Upstream project

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review container logs: `docker logs trading-terminal`
3. Check API logs: `docker logs trade-api`
4. Verify network connectivity between containers
5. Review Caddy configuration and routing

## Summary

The Trading Terminal integration provides a modern, responsive web interface for the existing trade API, enabling users to:
- Monitor 22+ currencies, commodities, and dollar index in real-time
- Manage custom watchlists with persistent storage
- Track portfolio performance with automatic P&L calculation
- Access trading signals based on technical analysis
- Visualize market data with interactive charts

The integration successfully leverages the existing 168K+ record database while providing a user-friendly interface for market analysis and portfolio management.
