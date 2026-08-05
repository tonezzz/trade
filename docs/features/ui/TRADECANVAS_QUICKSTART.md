
---

**Last Updated: 2026-08-04
# TradeCanvas Quick Start Guide

## Getting Started with the Enhanced TradeCanvas UI

### Prerequisites

- Trade API running at `http://tony-omen.local:8080/apps/trade/api`
- Modern web browser (Chrome, Firefox, Safari, Edge)
- USD/THB data imported into database (547 records from 1981-01-01 to 2026-07-01)

### Quick Start

1. **Open the Enhanced UI**:
   ```
   http://tony-omen.local:8080/apps/trade/tradecanvas-ui/index.html
   ```

2. **Default View**:
   - USD/THB is selected as default symbol
   - 1 Year timeframe is selected
   - Candlestick chart displays automatically
   - Connection status shows "Connected"

3. **Basic Navigation**:
   - **Change Symbol**: Use the symbol selector dropdown
   - **Change Timeframe**: Use the timeframe selector (1D, 1W, 1M, 3M, 6M, 1Y, 2Y)
   - **Refresh Data**: Click the Refresh button
   - **Zoom**: Use +, -, Reset buttons
   - **Pan**: Click and drag on the chart

### Using Technical Indicators

1. **Add Indicators**:
   - Click indicator buttons in the chart controls
   - Available: SMA, EMA, RSI, MACD, Bollinger Bands
   - Multiple indicators can be active simultaneously

2. **View Indicator Values**:
   - Check the "Indicator Values" panel in the side panel
   - Values update in real-time

3. **Remove Indicators**:
   - Click the indicator button again to toggle off

### Customizing Charts

1. **Open Settings**:
   - Click the Settings button in the header

2. **Customize Colors**:
   - Up Color: Color for bullish candles
   - Down Color: Color for bearish candles
   - Background Color: Chart background
   - Grid Color: Grid line color

3. **Toggle Features**:
   - Show Volume: Display volume histogram
   - Show Crosshair: Enable crosshair on hover

4. **Auto-Refresh**:
   - Set interval in seconds (5-300)
   - Default: 30 seconds

5. **Apply Changes**:
   - Click Apply to save changes
   - Click Cancel to discard

### Real-Time Updates

1. **WebSocket Connection**:
   - Connection status shows in header
   - Auto-reconnects on disconnect

2. **Price Updates**:
   - Real-time price updates via WebSocket
   - Chart updates automatically

3. **Trade Feed**:
   - Recent trades appear in side panel
   - Shows price, size, and time
   - Last 20 trades displayed

### Mobile Usage

1. **Responsive Design**:
   - UI adapts to screen size
   - Touch-friendly controls
   - Simplified layout on mobile

2. **Mobile Navigation**:
   - Swipe to pan chart
   - Tap to interact with controls
   - Portrait and landscape support

## USD/THB Data

### Data Source

- **Source**: Federal Reserve Economic Data (FRED)
- **Series**: EXTHUS (Thai Baht to U.S. Dollar Spot Exchange Rate)
- **Frequency**: Monthly (averages of daily figures)
- **Unit**: Thai Baht per U.S. Dollar

### Data Range

- **Start Date**: 1981-01-01
- **End Date**: 2026-07-01
- **Total Records**: 547
- **Data Points**: Monthly averages

### Data Format

```csv
date,quote_currency,rate,open_price,high_price,low_price,close_price,volume
1981-01-01,THB,20.6611,20.6611,20.7024,20.6198,20.6611,1333887
```

- **OHLC Data**: Synthetic (0.2% variation from close)
- **Volume**: Synthetic for visualization

## Available Symbols

### Currencies (28 available)

**Primary Currencies**:
- THB (Thai Baht) - DEFAULT
- EUR (Euro)
- GBP (British Pound)
- JPY (Japanese Yen)
- CHF (Swiss Franc)
- CAD (Canadian Dollar)
- AUD (Australian Dollar)
- NZD (New Zealand Dollar)

**Additional Currencies**:
- BRL (Brazilian Real)
- CNY (Chinese Yuan)
- CZK (Czech Koruna)
- DKK (Danish Krone)
- HKD (Hong Kong Dollar)
- HUF (Hungarian Forint)
- INR (Indian Rupee)
- KRW (South Korean Won)
- MXN (Mexican Peso)
- NOK (Norwegian Krone)
- PLN (Polish Zloty)
- SEK (Swedish Krona)
- SGD (Singapore Dollar)
- TRY (Turkish Lira)
- ZAR (South African Rand)
- MYR (Malaysian Ringgit)
- IDR (Indonesian Rupiah)
- PHP (Philippine Peso)
- VND (Vietnamese Dong)

### Indices

- DXY (Dollar Index)

### Commodities

- OIL (Crude Oil)

## Timeframes

### Available Timeframes

- **1D**: 1 Day
- **1W**: 1 Week
- **1M**: 1 Month
- **3M**: 3 Months (NEW)
- **6M**: 6 Months (NEW)
- **1Y**: 1 Year
- **2Y**: 2 Years (NEW)

### Timeframe Behavior

- **Shorter Timeframes**: More granular data, fewer data points
- **Longer Timeframes**: More data points, broader view
- **Auto-Adjust**: Chart automatically fits content

## Troubleshooting

### Connection Issues

1. **Check API Status**:
   ```bash
   curl http://tony-omen.local:8080/apps/trade/api/api/health
   ```

2. **Verify WebSocket**:
   - Check browser console for WebSocket errors
   - Verify connection status indicator

3. **Data Loading**:
   - Check browser console for API errors
   - Verify data exists in database

### Chart Issues

1. **Empty Chart**:
   - Verify symbol has data in database
   - Check timeframe selection
   - Try refreshing data

2. **Performance Issues**:
   - Reduce number of active indicators
   - Use shorter timeframes
   - Close other browser tabs

3. **Mobile Issues**:
   - Ensure modern browser
   - Clear browser cache
   - Try landscape mode

### Data Issues

1. **Missing THB Data**:
   ```bash
   # Check if THB data exists
   source venv/bin/activate
   python cli.py list currencies
   ```

2. **Re-import THB Data**:
   ```bash
   # Re-download and import
   python3 download_thb_data.py
   source venv/bin/activate
   python cli.py import exchange_rates data/imported/thb_formatted.csv --source FRED
   ```

## API Endpoints

### Exchange Rates
```
GET /api/exchange_rates/{currency}?period={period}&limit=1000
```

### Dollar Index
```
GET /api/dollar_index?period={period}&limit=1000
```

### Commodity Prices
```
GET /api/commodity_prices/{commodity}?period={period}&limit=1000
```

### WebSocket
```
WS /api/ws
```

## Keyboard Shortcuts

- **R**: Refresh data
- **Z**: Reset zoom
- **+**: Zoom in
- **-**: Zoom out
- **S**: Open settings
- **ESC**: Close modal

## Support

For issues or questions:
1. Check the main documentation: `docs/TRADECANVAS_INTEGRATION.md`
2. Review API documentation: `API_GUIDE.md`
3. Check troubleshooting: `TROUBLESHOOTING.md`
4. Review architecture: `ARCHITECTURE.md`
