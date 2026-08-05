
---

**Last Updated: 2026-08-04
# Trading Signal System Documentation

## Overview

The Trading Signal System is a comprehensive technical analysis and signal generation framework designed to provide actionable trading signals for currencies, commodities, and the Dollar Index (DXY). The system uses multiple technical indicators to generate buy/sell/hold signals with confidence scores and strength ratings.

## Features

- **Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, Support/Resistance, ADX, Volume indicators
- **Signal Generation**: Multi-factor signal generation with confidence scoring
- **Multiple Timeframes**: Support for daily, weekly, and monthly analysis
- **Backtesting**: Historical performance testing of signals
- **Alert System**: Configurable alerts for signal triggers
- **Signal History**: Track and analyze historical signals
- **API Endpoints**: RESTful API for signal access
- **Data Validation**: Quality checks for input data

## Architecture

### Core Components

1. **TechnicalIndicators Class**: Calculates all technical indicators
2. **SignalGenerator Class**: Generates trading signals from indicators
3. **SignalHistory Class**: Manages signal history in database
4. **Backtester Class**: Performs historical backtesting
5. **SignalAlertSystem Class**: Handles alert generation
6. **Database Models**: SignalHistory and SignalPerformance tables

## Technical Indicators

### Moving Averages

#### Simple Moving Average (SMA)
- **Short Period**: 20 days
- **Long Period**: 50 days
- **Very Long Period**: 200 days
- **Usage**: Trend identification and crossover signals

#### Exponential Moving Average (EMA)
- **Short Period**: 12 days
- **Long Period**: 26 days
- **Very Long Period**: 50 days
- **Usage**: Faster response to price changes

### Relative Strength Index (RSI)
- **Period**: 14 days
- **Oversold Threshold**: 30
- **Overbought Threshold**: 70
- **Extreme Oversold**: 20
- **Extreme Overbought**: 80
- **Usage**: Momentum and reversal signals

### MACD (Moving Average Convergence Divergence)
- **Fast Period**: 12 days
- **Slow Period**: 26 days
- **Signal Period**: 9 days
- **Components**: MACD line, Signal line, Histogram
- **Usage**: Trend following and momentum

### Bollinger Bands
- **Period**: 20 days
- **Standard Deviation**: 2.0
- **Components**: Upper band, Middle band (SMA), Lower band
- **Usage**: Volatility and overbought/oversold conditions

### ADX (Average Directional Index)
- **Period**: 14 days
- **Trend Threshold**: 25
- **Strong Trend**: 40+
- **Weak Trend**: <20
- **Components**: ADX, +DI, -DI
- **Usage**: Trend strength measurement

### Volume Indicators
- **Volume SMA**: 20-day average volume
- **Volume Ratio**: Current volume / Average volume
- **On Balance Volume (OBV)**: Cumulative volume flow
- **Usage**: Volume confirmation of price moves

### Support/Resistance Levels
- **Window**: 20 days
- **Levels**: 3 support and 3 resistance levels
- **Method**: Local extrema detection
- **Usage**: Key price levels for trading

## Signal Generation

### Signal Types

- **BUY**: Indicates potential upward price movement
- **SELL**: Indicates potential downward price movement
- **HOLD**: No clear directional signal

### Signal Strength

- **WEAK**: Confidence 0.60 - 0.74
- **MODERATE**: Confidence 0.75 - 0.84
- **STRONG**: Confidence 0.85 - 1.00

### Signal Scoring

Signals are generated based on a weighted scoring system:

| Indicator | Weight | Conditions |
|-----------|--------|------------|
| RSI | 2.0 | Oversold/Overbought |
| MACD | 2.0 | Crossover, Histogram |
| Moving Averages | 1.5 | Price position, Crossovers |
| Bollinger Bands | 1.0 | Price outside bands |
| ADX | 1.0 | Trend strength |
| Volume | 1.0 | Volume confirmation |
| Support/Resistance | 0.5 | Key levels |

### Minimum Confidence Threshold

Default minimum confidence: 0.60 (60%)

Signals below this threshold are converted to HOLD.

## Configuration

### Configuration File: `config/signals.yml`

```yaml
# Technical Indicator Parameters
indicators:
  sma:
    short_period: 20
    long_period: 50
  rsi:
    period: 14
    oversold: 30
    overbought: 70
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9
  # ... more indicators

# Signal Generation Rules
signal_rules:
  min_confidence: 0.6
  strength_thresholds:
    weak: 0.6
    moderate: 0.75
    strong: 0.85

# Timeframes
timeframes:
  - "1d"
  - "1w"
  - "1m"
```

### Asset-Specific Settings

Override default settings for specific assets:

```yaml
asset_settings:
  currencies:
    EUR:
      adx_threshold: 20
  commodities:
    GOLD:
      bollinger_std_dev: 2.5
```

## API Endpoints

### Get Currency Signal

**Endpoint**: `GET /api/signals/{currency}`

**Parameters**:
- `currency`: Currency code (e.g., EUR, GBP, JPY)
- `timeframe`: Timeframe (1d, 1w, 1m) - default: 1d

**Response**:
```json
{
  "signal_type": "buy",
  "strength": "moderate",
  "confidence": 0.78,
  "timestamp": "2024-01-15T10:30:00",
  "price": 1.0850,
  "indicators": {
    "rsi": 45.2,
    "macd": 0.0012,
    "adx": 28.5,
    ...
  },
  "reasons": [
    "RSI neutral",
    "MACD bullish crossover"
  ],
  "timeframe": "1d",
  "validation": {
    "is_valid": true,
    "warnings": [],
    "errors": []
  }
}
```

### Get Dollar Index Signal

**Endpoint**: `GET /api/signals/dollar_index`

**Parameters**:
- `timeframe`: Timeframe (1d, 1w, 1m) - default: 1d

**Response**: Same structure as currency signal

### Get Commodity Signal

**Endpoint**: `GET /api/signals/commodity/{commodity}`

**Parameters**:
- `commodity`: Commodity name or symbol (e.g., GOLD, XAU, OIL)
- `timeframe`: Timeframe (1d, 1w, 1m) - default: 1d

**Response**: Same structure as currency signal

### Get Signal History

**Endpoint**: `GET /api/signals/history`

**Parameters**:
- `asset_type`: Filter by asset type (currency, commodity, dollar_index)
- `asset_symbol`: Filter by asset symbol
- `limit`: Maximum number of signals (1-1000) - default: 100

**Response**: Array of historical signals

### Run Signal Backtest

**Endpoint**: `POST /api/signals/backtest`

**Request Body**:
```json
{
  "asset_type": "currency",
  "asset_symbol": "EUR",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000.0,
  "commission": 0.001,
  "timeframe": "1d"
}
```

**Response**:
```json
{
  "initial_capital": 10000.0,
  "final_capital": 10500.0,
  "total_return": 5.0,
  "max_drawdown": 2.5,
  "total_trades": 15,
  "win_rate": 60.0,
  "equity_curve": [...],
  "trades": [...]
}
```

### Get Signal Performance

**Endpoint**: `GET /api/signals/performance`

**Parameters**:
- `asset_type`: Filter by asset type
- `asset_symbol`: Filter by asset symbol
- `limit`: Maximum number of results (1-500) - default: 50

**Response**: Array of performance metrics

### Get Technical Indicators

**Endpoint**: `GET /api/signals/indicators/{currency}`

**Parameters**:
- `currency`: Currency code

**Response**:
```json
{
  "currency": "EUR",
  "timestamp": "2024-01-15T10:30:00",
  "indicators": {
    "sma_short": 1.0845,
    "sma_long": 1.0820,
    "rsi": 45.2,
    "macd": 0.0012,
    ...
  }
}
```

## Usage Examples

### Python API Usage

```python
from src.signals import SignalGenerator, Backtester, SignalAlertSystem
from src.queries import PriceQueries
from src.database import get_db
import pandas as pd

# Initialize signal generator
generator = SignalGenerator()

# Get historical data
db = next(get_db())
queries = PriceQueries(db)
df = queries.get_exchange_rates('EUR')

# Prepare data
df = df.set_index('date')
df['close'] = df['rate']
df['high'] = df['rate'] * 1.01
df['low'] = df['rate'] * 0.99
df['volume'] = 1000

# Generate signal
signal = generator.generate_signal(df)
print(f"Signal: {signal.signal_type.value}")
print(f"Confidence: {signal.confidence:.2f}")
print(f"Reasons: {signal.reasons}")

# Run backtest
backtester = Backtester(generator)
results = backtester.run_backtest(df)
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")

# Check alerts
alert_system = SignalAlertSystem()
alerts = alert_system.check_alert_conditions(signal)
for alert in alerts:
    print(f"Alert: {alert['message']}")
```

### CLI Usage

```bash
# Get signal for EUR
curl http://localhost:8000/api/signals/EUR

# Get DXY signal
curl http://localhost:8000/api/signals/dollar_index

# Get GOLD signal with weekly timeframe
curl http://localhost:8000/api/signals/commodity/GOLD?timeframe=1w

# Run backtest
curl -X POST http://localhost:8000/api/signals/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "currency",
    "asset_symbol": "EUR",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'
```

## Data Requirements

### Minimum Data Points
- **Signal Generation**: 50 data points
- **Recommended**: 200+ data points
- **Backtesting**: 500+ data points

### Required Columns
- `close` or `rate` or `price`: Close price
- `high`: High price (optional, will use close if missing)
- `low`: Low price (optional, will use close if missing)
- `volume`: Volume (optional, will use 1.0 if missing)

### Data Quality Checks

The system validates input data for:
- Null values
- Duplicate dates
- Negative prices
- Outliers (>3 standard deviations)
- Insufficient data points

## Signal Validation

### Validation Checks

1. **Confidence Threshold**: Signals below minimum confidence are converted to HOLD
2. **Conflicting Indicators**: Warnings for contradictory signals (e.g., BUY with overbought RSI)
3. **Trend Strength**: Warnings for low ADX (<20) indicating weak trends
4. **Volume Confirmation**: Checks for volume support of price moves

### Validation Response

```json
{
  "is_valid": true,
  "warnings": [
    "Low confidence: 0.55",
    "Weak trend (ADX < 20)"
  ],
  "errors": []
}
```

## Alert System

### Alert Types

1. **Strong Signal**: Signal strength is STRONG
2. **High Confidence**: Confidence >= 0.90
3. **Extreme RSI**: RSI < 20 or > 80
4. **Strong Trend**: ADX > 40
5. **Volume Spike**: Volume ratio > 2.0
6. **Bollinger Squeeze**: Bandwidth < 0.1

### Alert Configuration

```yaml
alerts:
  enabled: true
  conditions:
    strong_signal:
      enabled: true
      strength: "strong"
    high_confidence:
      enabled: true
      threshold: 0.9
```

## Backtesting

### Backtest Parameters

- **Initial Capital**: Default $10,000
- **Commission**: Default 0.1% per trade
- **Slippage**: Default 0.01% per trade

### Performance Metrics

- **Total Return**: Percentage gain/loss
- **Max Drawdown**: Maximum peak-to-trough decline
- **Win Rate**: Percentage of winning trades
- **Sharpe Ratio**: Risk-adjusted return
- **Profit Factor**: Gross profit / Gross loss
- **Average Win/Loss**: Average winning/losing trade

### Backtest Strategy

The backtester uses a sliding window approach:
1. Uses 50-period window for signal generation
2. Executes trades based on signals
3. Applies commission and slippage
4. Tracks equity curve
5. Calculates performance metrics

## Database Schema

### SignalHistory Table

```sql
CREATE TABLE signal_history (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(50) NOT NULL,
    asset_symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    strength VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price FLOAT NOT NULL,
    indicators JSON,
    reasons JSON,
    timeframe VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### SignalPerformance Table

```sql
CREATE TABLE signal_performance (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(50) NOT NULL,
    asset_symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    test_start_date DATE NOT NULL,
    test_end_date DATE NOT NULL,
    initial_capital FLOAT NOT NULL,
    final_capital FLOAT NOT NULL,
    total_return FLOAT NOT NULL,
    max_drawdown FLOAT NOT NULL,
    total_trades INTEGER NOT NULL,
    win_rate FLOAT NOT NULL,
    avg_win FLOAT,
    avg_loss FLOAT,
    profit_factor FLOAT,
    sharpe_ratio FLOAT,
    parameters JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Run Tests

```bash
# Run all signal tests
pytest tests/test_signals.py -v

# Run specific test class
pytest tests/test_signals.py::TestTechnicalIndicators -v

# Run with coverage
pytest tests/test_signals.py --cov=src.signals
```

### Test Coverage

Current test coverage: ~79% for signals module

Test categories:
- Technical indicator calculations
- Signal generation
- Signal validation
- Alert system
- Data quality validation
- Backtesting

## Best Practices

### Signal Interpretation

1. **Always check confidence**: Higher confidence = more reliable signals
2. **Consider multiple timeframes**: Confirm signals across timeframes
3. **Use volume confirmation**: Volume supports price moves
4. **Check trend strength**: ADX indicates trend reliability
5. **Review validation warnings**: Address any validation issues

### Risk Management

1. **Never rely solely on signals**: Use as part of broader analysis
2. **Set stop-losses**: Always define exit points
3. **Position sizing**: Risk only 1-2% per trade
4. **Diversify**: Don't concentrate on one asset
5. **Monitor performance**: Track signal accuracy over time

### Configuration Tips

1. **Adjust for asset class**: Different assets have different characteristics
2. **Optimize parameters**: Backtest to find optimal settings
3. **Monitor market conditions**: Adjust for volatility regimes
4. **Regular validation**: Ensure data quality is maintained
5. **Review alerts**: Fine-tune alert thresholds

## Troubleshooting

### Common Issues

**Issue**: "Insufficient data for signal generation"
- **Solution**: Ensure at least 50 data points are available

**Issue**: Low confidence signals
- **Solution**: Check if indicators are conflicting or trend is weak

**Issue**: Signal doesn't match market conditions
- **Solution**: Review configuration parameters for the specific asset

**Issue**: Backtest shows poor performance
- **Solution**: Adjust signal generation rules or parameters

## Performance Considerations

- **Caching**: Indicator calculations can be cached (configurable)
- **Batch Processing**: Process multiple signals in batches
- **Database Indexing**: Ensure proper indexes on signal_history table
- **Data Limits**: Use pagination for large history queries

## Future Enhancements

Planned features:
- Machine learning signal enhancement
- Multi-asset portfolio signals
- Real-time streaming signals
- Custom indicator support
- Advanced backtesting strategies
- Signal performance attribution
- Integration with trading platforms

## Support

For issues or questions:
1. Check the documentation
2. Review test examples
3. Check configuration file
4. Review validation warnings
5. Examine signal history for patterns

## License

This signal system is part of the trading infrastructure project.

## Version History

- **v1.0.0**: Initial release with core indicators and signal generation
  - SMA, EMA, RSI, MACD, Bollinger Bands
  - Support/Resistance, ADX, Volume indicators
  - Signal generation and validation
  - Backtesting capability
  - Alert system
  - API endpoints
  - Database models
