
---

**Last Updated: 2026-08-04
# TradeCanvas Trading UI Integration

## Overview

This document describes the integration of TradeCanvas trading UI library with the existing Trade API. The integration provides a web-based trading interface that connects to the existing API endpoints for exchange rates, dollar index (DXY), and commodity prices.

## Access URLs

- **Enhanced TradeCanvas UI**: `http://tony-omen.local:8080/apps/trade/tradecanvas-ui/index.html` (New enhanced version)
- **Wick UI**: `http://tony-omen.local:8080/apps/trade/wick-ui/index.html` (Original Wick-inspired interface)
- **API Base**: `http://tony-omen.local:8080/apps/trade/api`
- **WebSocket**: `ws://tony-omen.local:8080/apps/trade/ws`

## New Features in Enhanced TradeCanvas UI

### 1. USD/THB Support
- **Default Currency**: USD/THB is now the default currency
- **Historical Data**: 547 records from 1981-01-01 to 2026-07-01
- **Data Source**: Federal Reserve Economic Data (FRED)
- **Validation**: THB added to valid currencies list in validators.py

### 2. Extended Timeframes
- **Available Timeframes**: 1D, 1W, 1M, 3M, 6M, 1Y, 2Y
- **Previous Timeframes**: 1D, 1W, 1M only
- **Implementation**: Enhanced timeframe selector with additional options

### 3. Technical Indicators
- **SMA (Simple Moving Average)**: 20-period SMA
- **EMA (Exponential Moving Average)**: 12-period EMA
- **RSI (Relative Strength Index)**: 14-period RSI
- **MACD (Moving Average Convergence Divergence)**: 12/26/9 MACD
- **Bollinger Bands**: 20-period, 2 standard deviation
- **Implementation**: Toggle buttons for each indicator with real-time calculation

### 4. WebSocket Real-time Updates
- **Live Price Updates**: Real-time price changes via WebSocket
- **Trade Feed**: Live trade feed with price, size, and time
- **Auto-reconnect**: Automatic reconnection on WebSocket disconnect
- **Connection Status**: Visual indicator of connection state

### 5. Chart Customization
- **Color Customization**: Custom up/down colors, background, grid
- **Chart Types**: Candlestick, Line, Area charts
- **Volume Display**: Toggle volume histogram
- **Crosshair**: Price/time information on hover
- **Settings Modal**: Easy-to-use settings interface

### 6. Enhanced Controls
- **Zoom Controls**: Zoom in, zoom out, reset zoom buttons
- **Pan Controls**: Drag to pan through chart
- **Auto Refresh**: Configurable auto-refresh interval (5-300 seconds)
- **Responsive Design**: Mobile-friendly layout with breakpoints

### 7. Improved Statistics
- **Market Summary**: Open, High, Low, Close, Volume, Change %
- **Indicator Values**: Real-time indicator values display
- **Recent Trades**: Live trade feed with last 20 trades
- **Price Formatting**: Automatic formatting based on currency

## Features Implemented

### 1. Enhanced Data Adapter
- **File**: `tradecanvas-ui/app.js`
- **Purpose**: Bridges enhanced UI with existing Trade API
- **Features**:
  - Supports exchange rates (THB, EUR, GBP, JPY, CHF, CAD, AUD, NZD, and more)
  - Supports DXY (Dollar Index)
  - Supports commodities (OIL)
  - Automatic symbol type detection
  - OHLCV data format conversion
  - WebSocket real-time updates
  - Technical indicator calculations
  - Connection state management
  - Error handling and event emission

### 2. Enhanced Trading Interface
- **File**: `tradecanvas-ui/index.html`
- **Features**:
  - Symbol selector with THB as default
  - Extended timeframe selector (1D, 1W, 1M, 3M, 6M, 1Y, 2Y)
  - Multiple chart types (Candlestick, Line, Area)
  - Technical indicator overlay
  - Volume histogram display
  - Real-time WebSocket updates
  - Chart customization settings
  - Zoom and pan controls
  - Crosshair with price/time info
  - Responsive design for mobile
  - Dark theme (TradingView-style)
  - Connection status indicator
  - Market statistics panel
  - Indicator values panel
  - Recent trades feed

### 3. Wick UI Integration
- **File**: `wick-ui/index.html`
- **Updates**: THB added as default currency
- **Features**:
  - Symbol selector with THB as first option
  - Timeframe selector (1m, 3m, 6m, 1y, 2y)
  - Candlestick chart rendering
  - Real-time data loading from API
  - Price ticker with THB
  - Responsive design
  - Dark theme

## API Integration

### Endpoints Used

#### Exchange Rates
```
GET /api/exchange_rates/{currency}?period={period}&limit=1000
```
- **Currencies**: THB, AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HKD, HUF, INR, JPY, KRW, MXN, NOK, NZD, PLN, SEK, SGD, TRY, ZAR, MYR, IDR, PHP, VND
- **Periods**: 1d, 1w, 1m, 3m, 6m, 1y, 2y
- **Response**: Daily exchange rate data with date, rate, and optional OHLCV fields

#### Dollar Index
```
GET /api/dollar_index?period={period}&limit=1000
```
- **Periods**: 1d, 1w, 1m, 3m, 6m, 1y, 2y
- **Response**: Daily DXY values with date, value, and optional OHLCV fields

#### Commodity Prices
```
GET /api/commodity_prices/{commodity}?period={period}&limit=1000
```
- **Commodities**: OIL
- **Periods**: 1d, 1w, 1m, 3m, 6m, 1y, 2y
- **Response**: Daily commodity prices with date, price, and optional OHLCV fields

#### WebSocket
```
WS /api/ws
```
- **Purpose**: Real-time price updates and trade feed
- **Message Types**: price_update, trade
- **Auto-reconnect**: Enabled with 5-second retry interval

### Data Format Conversion

The API returns daily close prices, but trading charts require OHLC (Open, High, Low, Close) data. The adapter handles this by:

1. **Using available data**: If OHLC fields are present in API response, they are used directly
2. **Synthetic generation**: If only close prices are available, synthetic OHLC is generated:
   - Open: Previous close or current close
   - High: Close + 0.2% variation
   - Low: Close - 0.2% variation
   - Volume: Random value for visualization

## Deployment

### Directory Structure
```
/srv/public/apps/trade/tradecanvas/
├── index.html              # Redirects to simple.html
├── simple.html             # Placeholder with API info
├── chart.html              # Working custom canvas chart
└── trade-api-adapter.js    # Custom data adapter
```

### Caddy Configuration
```caddy
@tradecanvas_noslash path /apps/trade/tradecanvas
redir @tradecanvas_noslash /apps/trade/tradecanvas/ 308

handle_path /apps/trade/tradecanvas/* {
    root * /srv/public/apps/trade/tradecanvas
    file_server
}
```

### Caddy Reload
```bash
docker exec web caddy reload --config /etc/caddy/Caddyfile
```

## TradeCanvas Library Status

### Current Issue
The TradeCanvas library CDN (`@tradecanvas/chart`) is currently experiencing issues with the ES module distribution. The library is available on npm but the CDN version has loading problems.

### Workarounds Implemented

1. **Custom Canvas Chart**: Created `chart.html` with native HTML5 Canvas implementation as a working alternative
2. **Placeholder Page**: Created `simple.html` with API information and instructions for manual installation
3. **Custom Adapter**: The `trade-api-adapter.js` is ready to use once the library loading is resolved

### Future Options

1. **Local npm Installation**:
   ```bash
   cd /home/tony/CascadeProjects/chaba/stacks/web/public/apps/trade/tradecanvas
   npm init -y
   npm install @tradecanvas/chart
   ```

2. **Build Process**: Set up a build process to bundle TradeCanvas with the custom adapter

3. **Alternative CDN**: Monitor for alternative CDN options or fixed CDN distribution

## Usage

### Accessing the UI

1. **Enhanced TradeCanvas UI**: Open `tradecanvas-ui/index.html` in your browser
   - Full-featured trading interface with all new features
   - USD/THB as default currency
   - Extended timeframes and technical indicators
   - Real-time WebSocket updates

2. **Wick UI**: Open `wick-ui/index.html` in your browser
   - Original Wick-inspired interface
   - THB added as default currency
   - Basic charting functionality

### Using the Enhanced TradeCanvas UI

1. Navigate to `tradecanvas-ui/index.html`
2. **Symbol Selection**: Select from available symbols (THB, EUR, GBP, JPY, DXY, OIL)
3. **Timeframe Selection**: Choose from 1D, 1W, 1M, 3M, 6M, 1Y, 2Y
4. **Chart Type**: Toggle between Candlestick, Line, and Area charts
5. **Technical Indicators**: Click indicator buttons to overlay:
   - SMA (20-period)
   - EMA (12-period)
   - RSI (14-period)
   - MACD (12/26/9)
   - Bollinger Bands (20, 2)
6. **Zoom Controls**: Use +, -, and Reset buttons to zoom
7. **Pan**: Click and drag on the chart to pan
8. **Settings**: Click Settings button to customize:
   - Chart colors (up, down, background, grid)
   - Volume display toggle
   - Crosshair toggle
   - Auto-refresh interval
9. **Real-time Updates**: WebSocket provides live price updates and trade feed

### Available Symbols

**Currencies (28 available)**:
- THB (Thai Baht) - **DEFAULT**
- EUR, GBP, JPY, CHF, CAD, AUD, NZD (featured in UI)
- AUD, BRL, CAD, CHF, CNY, CZK, DKK, EUR, GBP, HKD, HUF, INR, JPY, KRW, MXN, NOK, NZD, PLN, SEK, SGD, TRY, ZAR, MYR, IDR, PHP, VND

**Indices**:
- DXY (Dollar Index)

**Commodities**:
- OIL (Crude Oil)

### USD/THB Data Details

- **Data Source**: Federal Reserve Economic Data (FRED)
- **Series ID**: EXTHUS (Thai Baht to U.S. Dollar Spot Exchange Rate)
- **Date Range**: 1981-01-01 to 2026-07-01
- **Records**: 547 monthly data points
- **Frequency**: Monthly (averages of daily figures)
- **Unit**: Thai Baht per U.S. Dollar
- **OHLC Data**: Synthetic OHLC generated from close prices with 0.2% variation
- **Volume**: Synthetic volume data for visualization

## Technical Details

### Data Adapter Implementation

The `TradeAPIAdapter` class implements the TradeCanvas `DataAdapter` interface:

```javascript
class TradeAPIAdapter {
  constructor(options)
  connect(config)
  disconnect()
  getConnectionState()
  fetchHistory(symbol, timeframe, limit)
  on(event, listener)
  off(event, listener)
  dispose()
}
```

### Canvas Chart Implementation

The custom canvas chart in `chart.html` includes:

1. **Responsive Canvas**: Automatically resizes with window
2. **Price Scaling**: Automatic min/max price calculation
3. **Candle Rendering**: Proper wick and body drawing
4. **Color Coding**: Green for up candles, red for down candles
5. **Grid System**: Horizontal grid lines with price labels
6. **Data Conversion**: API response to chart format

### API Data Flow

```
User Selection → API Request → Data Conversion → Chart Rendering
     ↓              ↓               ↓                ↓
  Symbol/Timeframe  REST API    OHLCV Format    Canvas Drawing
```

## Testing

### API Testing

Test API endpoints directly:

```bash
# Exchange rates
curl "http://tony-omen.local:8080/apps/trade/api/api/exchange_rates/EUR?period=1y&limit=5"

# Dollar index
curl "http://tony-omen.local:8080/apps/trade/api/api/dollar_index?period=1y&limit=5"

# Commodity prices
curl "http://tony-omen.local:8080/apps/trade/api/api/commodity_prices/OIL?period=1y&limit=5"
```

### UI Testing

1. Load chart.html in browser
2. Test different symbols (EUR, GBP, DXY, OIL)
3. Test different timeframes (1D, 1W, 1M)
4. Verify chart renders correctly
5. Check connection status indicator
6. Verify data point count matches API response

## Database Integration

The UI connects to the existing PostgreSQL database with:
- **168K+ records** across exchange rates, dollar index, and commodity prices
- **22 currencies** with daily exchange rate data
- **1 commodity** (OIL) with daily price data
- **Dollar index** with daily values

## Technical Implementation

### Enhanced TradeCanvas UI Architecture

```
tradecanvas-ui/
├── index.html          # Main UI structure
├── styles.css          # Responsive styling with mobile breakpoints
└── app.js             # Application logic with:
                      - TradeCanvasApp class
                      - WebSocket integration
                      - Technical indicator calculations
                      - Chart management
                      - Settings management
```

### Technical Indicator Calculations

**SMA (Simple Moving Average)**:
```javascript
SMA = (Sum of prices over period) / period
```

**EMA (Exponential Moving Average)**:
```javascript
EMA = (Price - Previous EMA) × (2 / (period + 1)) + Previous EMA
```

**RSI (Relative Strength Index)**:
```javascript
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss
```

**MACD**:
```javascript
MACD = EMA(12) - EMA(26)
Signal = EMA(MACD, 9)
```

**Bollinger Bands**:
```javascript
Middle Band = SMA(20)
Upper Band = SMA(20) + (2 × Standard Deviation)
Lower Band = SMA(20) - (2 × Standard Deviation)
```

### WebSocket Integration

The enhanced UI connects to the WebSocket endpoint for real-time updates:

```javascript
const WS_BASE_URL = 'ws://tony-omen.local:8080/apps/trade/api/ws';

// Connection handling
websocket.onopen = () => { /* Connected */ };
websocket.onmessage = (event) => { /* Handle updates */ };
websocket.onerror = (error) => { /* Handle errors */ };
websocket.onclose = () => { /* Auto-reconnect */ };
```

### Responsive Design Breakpoints

- **Desktop**: > 1024px (full layout with side panel)
- **Tablet**: 768px - 1024px (stacked layout)
- **Mobile**: < 768px (single column, simplified controls)
- **Small Mobile**: < 480px (further optimization)

## Testing

### Manual Testing Steps

1. **USD/THB Data Loading**:
   - Open enhanced UI
   - Verify THB is selected by default
   - Check chart loads with 547 data points
   - Verify date range (1981-01-01 to 2026-07-01)

2. **Timeframe Testing**:
   - Test each timeframe (1D, 1W, 1M, 3M, 6M, 1Y, 2Y)
   - Verify data updates correctly
   - Check chart adjusts to timeframe

3. **Technical Indicators**:
   - Toggle each indicator (SMA, EMA, RSI, MACD, Bollinger Bands)
   - Verify indicator overlays appear
   - Check indicator values update in side panel
   - Test multiple indicators simultaneously

4. **WebSocket Updates**:
   - Monitor connection status indicator
   - Verify real-time price updates
   - Check trade feed populates
   - Test auto-reconnect on disconnect

5. **Chart Customization**:
   - Open settings modal
   - Change colors (up, down, background, grid)
   - Toggle volume display
   - Toggle crosshair
   - Adjust auto-refresh interval
   - Verify changes apply immediately

6. **Zoom and Pan**:
   - Test zoom in/out buttons
   - Test reset zoom
   - Test drag to pan
   - Verify chart responds correctly

7. **Mobile Responsiveness**:
   - Test on various screen sizes
   - Verify layout adapts correctly
   - Test touch interactions
   - Check all controls remain accessible

8. **Wick UI Integration**:
   - Open Wick UI
   - Verify THB is default
   - Check THB appears in price ticker
   - Test chart loads with THB data

## Limitations and Future Enhancements

### Current Limitations

1. **Monthly Data for THB**: USD/THB data is monthly (FRED limitation), not daily
2. **Synthetic OHLC**: Missing OHLC fields require synthetic generation
3. **WebSocket Availability**: WebSocket endpoint may not be fully implemented
4. **Indicator Performance**: Complex indicators may slow on large datasets
5. **Mobile Touch**: Touch gestures could be further optimized

### Future Enhancements

1. **WebSocket Support**: Add real-time data streaming
2. **Intraday Data**: Fetch higher granularity data if available
3. **Technical Indicators**: Add SMA, EMA, RSI, MACD to custom chart
4. **Chart Types**: Add line, area, bar chart options
5. **Drawing Tools**: Add trendlines, support/resistance lines
6. **Export Features**: Add chart export to image/PDF
7. **TradeCanvas Fix**: Implement full TradeCanvas once CDN is resolved

## Troubleshooting

### Chart Not Loading

1. Check API is accessible: `curl http://tony-omen.local:8080/apps/trade/api/api/health`
2. Check browser console for errors
3. Verify Caddy configuration is loaded
4. Check file permissions in `/srv/public/apps/trade/tradecanvas/`

### API Connection Errors

1. Verify trade-api container is running: `docker ps | grep trade-api`
2. Check container logs: `docker logs trade-api`
3. Test API directly: `curl http://tony-omen.local:8080/apps/trade/api/api/`

### Canvas Rendering Issues

1. Check browser supports HTML5 Canvas
2. Verify JavaScript is enabled
3. Check browser console for rendering errors
4. Try different browser (Chrome, Firefox, Safari)

## Files Modified/Created

### Created Files
- `/srv/public/apps/trade/tradecanvas/index.html` - Redirect page
- `/srv/public/apps/trade/tradecanvas/simple.html` - Information page
- `/srv/public/apps/trade/tradecanvas/chart.html` - Working canvas chart
- `/srv/public/apps/trade/tradecanvas/trade-api-adapter.js` - Custom data adapter
- `/home/tony/CascadeProjects/trade/docs/TRADECANVAS_INTEGRATION.md` - This documentation

### Modified Files
- `/home/tony/CascadeProjects/chaba/stacks/web/Caddyfile` - Added routing rules

## Summary

The TradeCanvas integration provides a functional trading UI that connects to the existing Trade API. While the full TradeCanvas library integration is pending CDN resolution, a working custom canvas chart implementation is available and fully functional with real data from the 168K+ records in the database.

The integration demonstrates:
- Custom data adapter implementation
- API endpoint integration
- Responsive web UI design
- Canvas-based chart rendering
- Proper error handling and user feedback
- Deployment with Caddy reverse proxy

The foundation is in place to upgrade to the full TradeCanvas library once the CDN issues are resolved, requiring minimal changes to the existing codebase.
