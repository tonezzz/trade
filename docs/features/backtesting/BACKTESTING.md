
---

**Last Updated:** 2026-08-05
# Backtesting System Documentation

## Overview

The backtesting system provides a comprehensive framework for testing trading strategies on historical data. It includes a strategy framework, backtesting engine, performance metrics calculation, parameter optimization, and walk-forward analysis capabilities.

## Features

- **Strategy Framework**: Abstract base class for defining custom trading strategies
- **Backtesting Engine**: Run strategies on historical data with realistic execution simulation
- **Performance Metrics**: Calculate Sharpe ratio, Sortino ratio, max drawdown, win rate, and more
- **Trade Execution**: Simulate trades with commission, slippage, and position management
- **Risk Management**: Built-in stop-loss, take-profit, and position sizing
- **Parameter Optimization**: Grid search and random search for finding optimal parameters
- **Walk-Forward Analysis**: Validate strategies using rolling window analysis
- **Strategy Comparison**: Compare multiple strategies side-by-side
- **Performance Reports**: Generate detailed text and JSON reports

## Architecture

### Core Components

1. **BacktestEngine**: Main engine that runs backtests
2. **Strategy**: Abstract base class for trading strategies
3. **BacktestConfig**: Configuration for backtesting parameters
4. **Trade/Position**: Data structures for trades and positions
5. **ParameterOptimizer**: Optimize strategy parameters
6. **WalkForwardAnalysis**: Perform walk-forward validation
7. **StrategyComparator**: Compare multiple strategies
8. **PerformanceReport**: Generate performance reports

### Database Models

- **BacktestResult**: Stores backtest execution results
- **BacktestTrade**: Stores individual trades from backtests
- **BacktestEquity**: Stores equity curve data points

## Configuration

The backtesting system is configured via `config/backtesting.yml`:

```yaml
# Initial capital settings
initial_capital:
  default: 100000.0
  min: 1000.0
  max: 10000000.0

# Commission and fee settings
commission:
  enabled: true
  type: "percentage"
  value: 0.001  # 0.1% per trade

# Slippage settings
slippage:
  enabled: true
  type: "percentage"
  value: 0.0001  # 0.01% slippage

# Risk management parameters
risk_management:
  max_position_size: 0.2  # 20% of capital per position
  max_total_exposure: 1.0  # 100% total exposure
  max_drawdown_limit: 0.5  # Stop at 50% drawdown

# Default stop-loss and take-profit
default_stops:
  stop_loss:
    enabled: true
    value: 0.05  # 5% stop loss
  take_profit:
    enabled: true
    value: 0.10  # 10% take profit
```

## Available Strategies

### 1. Moving Average Crossover

**Description**: Generates buy/sell signals when fast moving average crosses slow moving average.

**Parameters**:
- `fast_period`: Period for fast MA (default: 10)
- `slow_period`: Period for slow MA (default: 30)

**Example**:
```python
from src.backtesting import MovingAverageCrossover

strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
```

### 2. RSI Strategy

**Description**: Uses Relative Strength Index to identify overbought/oversold conditions.

**Parameters**:
- `period`: RSI calculation period (default: 14)
- `oversold`: Oversold threshold (default: 30)
- `overbought`: Overbought threshold (default: 70)

**Example**:
```python
from src.backtesting import RSIStrategy

strategy = RSIStrategy(period=14, oversold=30, overbought=70)
```

### 3. MACD Strategy

**Description**: Uses MACD histogram crossovers for signals.

**Parameters**:
- `fast_period`: Fast EMA period (default: 12)
- `slow_period`: Slow EMA period (default: 26)
- `signal_period`: Signal line period (default: 9)

**Example**:
```python
from src.backtesting import MACDStrategy

strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
```

### 4. Bollinger Bands Strategy

**Description**: Trades based on price interactions with Bollinger Bands.

**Parameters**:
- `period`: Period for bands calculation (default: 20)
- `std_dev`: Standard deviation for bands (default: 2.0)

**Example**:
```python
from src.backtesting import BollingerBandsStrategy

strategy = BollingerBandsStrategy(period=20, std_dev=2.0)
```

### 5. Buy and Hold

**Description**: Benchmark strategy that buys on first day and holds.

**Parameters**: None

**Example**:
```python
from src.backtesting import BuyAndHold

strategy = BuyAndHold()
```

## Usage Examples

### Basic Backtest

```python
from src.backtesting import BacktestEngine, BacktestConfig, MovingAverageCrossover
from src.queries import PriceQueries
from src.database import get_db
import pandas as pd

# Get database session
db = next(get_db())
queries = PriceQueries(db)

# Get historical data
data = queries.get_exchange_rates('EUR', start_date='2023-01-01', end_date='2023-12-31')
data = data.rename(columns={'rate': 'close'})
data['open'] = data['close']
data['high'] = data['close']
data['low'] = data['close']

# Create backtest configuration
config = BacktestConfig(
    initial_capital=100000.0,
    commission_rate=0.001,
    slippage_rate=0.0001
)

# Create engine and set data
engine = BacktestEngine(config)
engine.set_data(data)

# Set strategy
strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
engine.set_strategy(strategy)

# Run backtest
result = engine.run()

# Print results
print(f"Total Return: {result['metrics']['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {result['metrics']['max_drawdown_pct']:.2f}%")
print(f"Win Rate: {result['metrics']['win_rate']:.2f}%")
```

### Parameter Optimization

```python
from src.backtesting import BacktestEngine, BacktestConfig, ParameterOptimizer

# Setup
config = BacktestConfig(initial_capital=100000.0)
engine = BacktestEngine(config)
optimizer = ParameterOptimizer(engine, data)

# Define parameter ranges
param_ranges = {
    'fast_period': (5, 20),
    'slow_period': (20, 50)
}

# Run random search optimization
result = optimizer.random_search(
    'moving_average_crossover',
    param_ranges,
    n_iterations=50,
    metric='sharpe_ratio'
)

print(f"Best Parameters: {result['best_parameters']}")
print(f"Best Sharpe Ratio: {result['best_metrics']['sharpe_ratio']:.2f}")
```

### Walk-Forward Analysis

```python
from src.backtesting import BacktestEngine, WalkForwardAnalysis

# Setup
config = BacktestConfig(initial_capital=100000.0)
engine = BacktestEngine(config)
wfa = WalkForwardAnalysis(engine, data)

# Run walk-forward analysis
result = wfa.run(
    'moving_average_crossover',
    {'fast_period': 10, 'slow_period': 30},
    train_size=0.6,
    test_size=0.2,
    step_size=0.1
)

print(f"Number of folds: {len(result['results'])}")
print(f"Average Sharpe Ratio: {result['aggregate_metrics']['avg_sharpe_ratio']:.2f}")
```

### Strategy Comparison

```python
from src.backtesting import StrategyComparator, BacktestConfig

# Setup
config = BacktestConfig(initial_capital=100000.0)
comparator = StrategyComparator(config)

# Define strategies to compare
strategies = [
    {'name': 'buy_and_hold'},
    {'name': 'moving_average_crossover', 'parameters': {'fast_period': 10, 'slow_period': 30}},
    {'name': 'rsi', 'parameters': {'period': 14, 'oversold': 30, 'overbought': 70}}
]

# Run comparison
results = comparator.compare(data, strategies)
print(results[['strategy_name', 'total_return_pct', 'sharpe_ratio', 'max_drawdown_pct']])
```

### Performance Report Generation

```python
from src.backtesting import PerformanceReport

# Generate report
report = PerformanceReport(result)

# Text report
print(report.generate_text_report())

# JSON report
json_report = report.generate_json_report()

# Save to files
saved_files = report.save_report(output_dir='backtest_results')
print(f"Saved files: {saved_files}")
```

## Creating Custom Strategies

To create a custom strategy, inherit from the `Strategy` base class:

```python
from src.backtesting import Strategy
import pandas as pd
import talib

class MyCustomStrategy(Strategy):
    """Custom trading strategy."""

    def __init__(self, param1: int = 10, param2: float = 0.5):
        parameters = {
            'param1': param1,
            'param2': param2
        }
        super().__init__('My Custom Strategy', parameters)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate custom indicators."""
        df = data.copy()
        # Add your indicators here
        df['custom_indicator'] = talib.SMA(df['close'], timeperiod=self.parameters['param1'])
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals."""
        signals = pd.Series(0, index=data.index)

        # Add your signal logic here
        # signals[condition] = 1  # Buy
        # signals[condition] = -1  # Sell

        return signals
```

## API Endpoints

### POST /api/backtest/run

Run a backtest for a trading strategy.

**Request Body**:
```json
{
  "strategy_name": "moving_average_crossover",
  "symbol": "EUR",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000.0,
  "parameters": {
    "fast_period": 10,
    "slow_period": 30
  },
  "commission_rate": 0.001,
  "slippage_rate": 0.0001,
  "stop_loss_pct": 0.05,
  "take_profit_pct": 0.10
}
```

**Response**: Backtest results with performance metrics

### GET /api/backtest/results/{id}

Get backtest results by ID.

**Response**: Backtest results including equity curve and trades

### GET /api/backtest/strategies

List available backtesting strategies.

**Response**:
```json
{
  "strategies": [
    {
      "name": "moving_average_crossover",
      "display_name": "Moving Average Crossover",
      "parameters": {"fast_period": 10, "slow_period": 30}
    }
  ],
  "count": 5
}
```

### POST /api/backtest/optimize

Optimize strategy parameters.

**Request Body**:
```json
{
  "strategy_name": "moving_average_crossover",
  "symbol": "EUR",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "optimization_method": "random",
  "n_iterations": 100,
  "metric": "sharpe_ratio"
}
```

**Response**: Optimization results with best parameters

### POST /api/backtest/compare

Compare multiple strategies on the same data.

**Request Body**:
```json
{
  "strategies": [
    {"name": "buy_and_hold"},
    {"name": "moving_average_crossover", "parameters": {"fast_period": 10, "slow_period": 30}}
  ],
  "symbol": "EUR",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000.0
}
```

**Response**: Comparison results

## Performance Metrics

The backtesting engine calculates the following metrics:

### Return Metrics
- **Total Return**: Absolute return in currency
- **Total Return %**: Percentage return
- **Final Capital**: Ending capital after backtest

### Risk-Adjusted Metrics
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Sortino Ratio**: Downside risk-adjusted return
- **Max Drawdown**: Maximum peak-to-trough decline
- **Max Drawdown %**: Maximum drawdown as percentage

### Trade Statistics
- **Total Trades**: Number of trades executed
- **Winning Trades**: Number of profitable trades
- **Losing Trades**: Number of unprofitable trades
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Average Win**: Average profit from winning trades
- **Average Loss**: Average loss from losing trades
- **Largest Win**: Maximum profit from a single trade
- **Largest Loss**: Maximum loss from a single trade
- **Average Trade Duration**: Average holding period in days

## Risk Management

### Position Sizing
The system supports multiple position sizing methods:
- **Fixed**: Fixed position size
- **Percentage**: Percentage of capital per trade
- **Risk-Based**: Based on risk per trade
- **Kelly Criterion**: Optimal growth rate
- **Volatility-Based**: Based on volatility

### Stop-Loss and Take-Profit
- **Stop-Loss**: Automatically exit losing positions at specified level
- **Take-Profit**: Automatically exit winning positions at target
- **Trailing Stops**: Dynamic stop-loss that follows price

### Risk Limits
- **Max Position Size**: Limit position size as percentage of capital
- **Max Total Exposure**: Limit total market exposure
- **Max Drawdown Limit**: Stop trading if drawdown exceeds threshold
- **Max Daily Loss**: Stop trading if daily loss exceeds limit
- **Max Consecutive Losses**: Stop trading after consecutive losses

## Best Practices

1. **Use Sufficient Data**: Use at least 1-2 years of historical data for reliable results
2. **Avoid Overfitting**: Use walk-forward analysis to validate strategies
3. **Consider Transaction Costs**: Include realistic commission and slippage
4. **Test Multiple Markets**: Validate strategies across different instruments
5. **Monitor Drawdowns**: Pay attention to maximum drawdown, not just returns
6. **Use Risk Management**: Always implement stop-loss and position sizing
7. **Compare to Benchmark**: Compare strategy performance to buy-and-hold
8. **Validate Out-of-Sample**: Always test on unseen data before live trading

## Limitations

- **Historical Data**: Past performance does not guarantee future results
- **Market Conditions**: Strategies may not work in all market conditions
- **Execution Assumptions**: Real execution may differ from simulation
- **Liquidity**: Large orders may impact prices in reality
- **Slippage**: Actual slippage may vary from assumptions
- **Gaps**: Price gaps may trigger stops at worse prices

## Troubleshooting

### Common Issues

**Issue**: No signals generated
- **Solution**: Check that indicators are calculated correctly and signal logic is sound

**Issue**: Poor performance
- **Solution**: Try different parameters, check for overfitting, verify data quality

**Issue**: Too many trades
- **Solution**: Add filters, increase signal thresholds, add cooldown periods

**Issue**: High drawdown
- **Solution**: Implement tighter stop-loss, reduce position size, add risk limits

## Testing

Run the test suite:

```bash
source venv/bin/activate
python -m pytest tests/test_backtesting.py -v
```

## Future Enhancements

Potential improvements for the backtesting system:

- [ ] Multi-asset portfolio backtesting
- [ ] Machine learning strategy integration
- [ ] Real-time paper trading
- [ ] Advanced order types (limit, stop-limit)
- [ ] Monte Carlo simulation
- [ ] Market regime detection
- [ ] Dynamic parameter adjustment
- [ ] Strategy ensemble methods
- [ ] Advanced visualization
- [ ] Cloud-based optimization

## Support

For issues or questions:
1. Check the documentation
2. Review the test cases for examples
3. Examine the API endpoints
4. Check the configuration file

## License

This backtesting system is part of the trading infrastructure project.
