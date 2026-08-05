
---

**Last Updated: 2026-08-04
# Trading Signal System - Quick Start Guide

## Installation

The signal system is included in the main trading infrastructure. Ensure you have:

```bash
# Install dependencies
pip install pandas numpy pyyaml sqlalchemy fastapi

# Run database migrations
python -m src.database init_db
```

## Quick Start

### 1. Generate Your First Signal

```python
from src.signals import SignalGenerator
from src.queries import PriceQueries
from src.database import get_db

# Initialize
generator = SignalGenerator()
db = next(get_db())
queries = PriceQueries(db)

# Get data
df = queries.get_exchange_rates('EUR')
df = df.set_index('date')
df['close'] = df['rate']
df['high'] = df['rate'] * 1.01
df['low'] = df['rate'] * 0.99
df['volume'] = 1000

# Generate signal
signal = generator.generate_signal(df)
print(f"Signal: {signal.signal_type.value}")
print(f"Strength: {signal.strength.value}")
print(f"Confidence: {signal.confidence:.2f}")
```

### 2. Run a Backtest

```python
from src.signals import Backtester

backtester = Backtester(generator)
results = backtester.run_backtest(df, initial_capital=10000)

print(f"Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Trades: {results['total_trades']}")
```

### 3. Check Alerts

```python
from src.signals import SignalAlertSystem

alert_system = SignalAlertSystem()
alerts = alert_system.check_alert_conditions(signal)

for alert in alerts:
    print(f"ALERT: {alert['message']}")
```

## API Quick Start

### Start the API Server

```bash
python -m src.api
```

### Get a Signal via API

```bash
# Currency signal
curl http://localhost:8000/api/signals/EUR

# Dollar Index signal
curl http://localhost:8000/api/signals/dollar_index

# Commodity signal
curl http://localhost:8000/api/signals/commodity/GOLD
```

### Run Backtest via API

```bash
curl -X POST http://localhost:8000/api/signals/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "currency",
    "asset_symbol": "EUR",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'
```

## Configuration

Edit `config/signals.yml` to customize:

```yaml
indicators:
  rsi:
    period: 14
    oversold: 30
    overbought: 70

signal_rules:
  min_confidence: 0.6
  strength_thresholds:
    weak: 0.6
    moderate: 0.75
    strong: 0.85
```

## Common Use Cases

### Monitor Multiple Currencies

```python
currencies = ['EUR', 'GBP', 'JPY', 'CHF']
for currency in currencies:
    df = queries.get_exchange_rates(currency)
    # Prepare data...
    signal = generator.generate_signal(df)
    print(f"{currency}: {signal.signal_type.value} ({signal.confidence:.2f})")
```

### Compare Timeframes

```python
timeframes = ['1d', '1w', '1m']
for tf in timeframes:
    signal = generator.generate_signal(df, timeframe=tf)
    print(f"{tf}: {signal.signal_type.value}")
```

### Track Signal History

```python
from src.signals import SignalHistory

history = SignalHistory(db)
history.save_signal(signal, 'currency', 'EUR')

# Retrieve recent signals
recent = history.get_recent_signals(asset_symbol='EUR', limit=10)
```

## Next Steps

1. Read the full [SIGNALS.md](SIGNALS.md) documentation
2. Explore configuration options in `config/signals.yml`
3. Run tests: `pytest tests/test_signals.py -v`
4. Check API documentation at http://localhost:8000/docs
5. Review signal history in the database

## Tips

- Always validate signals before acting on them
- Use multiple timeframes for confirmation
- Monitor signal performance over time
- Adjust parameters based on backtesting results
- Keep data quality high for reliable signals
