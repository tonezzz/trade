"""
Example script demonstrating the backtesting system.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.backtesting import (
    BacktestEngine, BacktestConfig,
    MovingAverageCrossover, RSIStrategy, MACDStrategy,
    BollingerBandsStrategy, BuyAndHold,
    get_strategy, list_strategies,
    ParameterOptimizer, WalkForwardAnalysis, StrategyComparator,
    PerformanceReport
)
from src.queries import PriceQueries
from src.database import get_db
import pandas as pd


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def example_list_strategies():
    """Example: List available strategies."""
    print_section("Available Strategies")

    strategies = list_strategies()
    for strategy in strategies:
        print(f"\n{strategy['display_name']}")
        print(f"  Name: {strategy['name']}")
        print(f"  Parameters: {strategy['parameters']}")


def example_basic_backtest():
    """Example: Run a basic backtest."""
    print_section("Basic Backtest Example")

    # Get database session
    db = next(get_db())
    queries = PriceQueries(db)

    # Get historical data for EUR
    print("Fetching historical data for EUR...")
    data = queries.get_exchange_rates('EUR', start_date='2023-01-01', end_date='2023-12-31')

    if data.empty:
        print("No data found. Please import data first.")
        return

    # Prepare data
    data = data.rename(columns={'rate': 'close'})
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']

    print(f"Data points: {len(data)}")

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
    print("Running backtest...")
    result = engine.run()

    # Print results
    metrics = result['metrics']
    print(f"\nResults:")
    print(f"  Initial Capital: ${result['initial_capital']:,.2f}")
    print(f"  Final Capital: ${result['final_capital']:,.2f}")
    print(f"  Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print(f"  Win Rate: {metrics['win_rate']:.2f}%")
    print(f"  Total Trades: {metrics['total_trades']}")

    db.close()


def example_strategy_comparison():
    """Example: Compare multiple strategies."""
    print_section("Strategy Comparison Example")

    # Get database session
    db = next(get_db())
    queries = PriceQueries(db)

    # Get historical data
    print("Fetching historical data for EUR...")
    data = queries.get_exchange_rates('EUR', start_date='2023-01-01', end_date='2023-12-31')

    if data.empty:
        print("No data found. Please import data first.")
        return

    # Prepare data
    data = data.rename(columns={'rate': 'close'})
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']

    # Create comparator
    config = BacktestConfig(initial_capital=100000.0)
    comparator = StrategyComparator(config)

    # Define strategies to compare
    strategies = [
        {'name': 'buy_and_hold'},
        {'name': 'moving_average_crossover', 'parameters': {'fast_period': 10, 'slow_period': 30}},
        {'name': 'rsi', 'parameters': {'period': 14, 'oversold': 30, 'overbought': 70}}
    ]

    print("Comparing strategies...")
    results = comparator.compare(data, strategies)

    print("\nComparison Results:")
    print(results[['strategy_name', 'total_return_pct', 'sharpe_ratio', 'max_drawdown_pct', 'win_rate']])

    db.close()


def example_parameter_optimization():
    """Example: Optimize strategy parameters."""
    print_section("Parameter Optimization Example")

    # Get database session
    db = next(get_db())
    queries = PriceQueries(db)

    # Get historical data
    print("Fetching historical data for EUR...")
    data = queries.get_exchange_rates('EUR', start_date='2023-01-01', end_date='2023-12-31')

    if data.empty:
        print("No data found. Please import data first.")
        return

    # Prepare data
    data = data.rename(columns={'rate': 'close'})
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']

    # Create optimizer
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    optimizer = ParameterOptimizer(engine, data)

    # Define parameter ranges
    param_ranges = {
        'fast_period': (5, 20),
        'slow_period': (20, 50)
    }

    print("Running optimization (10 iterations)...")
    result = optimizer.random_search(
        'moving_average_crossover',
        param_ranges,
        n_iterations=10,
        metric='sharpe_ratio'
    )

    print(f"\nBest Parameters: {result['best_parameters']}")
    print(f"Best Sharpe Ratio: {result['best_metrics']['sharpe_ratio']:.2f}")
    print(f"Best Total Return: {result['best_metrics']['total_return_pct']:.2f}%")

    db.close()


def example_performance_report():
    """Example: Generate performance report."""
    print_section("Performance Report Example")

    # Get database session
    db = next(get_db())
    queries = PriceQueries(db)

    # Get historical data
    print("Fetching historical data for EUR...")
    data = queries.get_exchange_rates('EUR', start_date='2023-01-01', end_date='2023-12-31')

    if data.empty:
        print("No data found. Please import data first.")
        return

    # Prepare data
    data = data.rename(columns={'rate': 'close'})
    data['open'] = data['close']
    data['high'] = data['close']
    data['low'] = data['close']

    # Run backtest
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    engine.set_data(data)
    strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
    engine.set_strategy(strategy)

    result = engine.run()

    # Generate report
    report = PerformanceReport(result)
    print(report.generate_text_report())

    db.close()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  BACKTESTING SYSTEM EXAMPLES")
    print("=" * 60)

    # List strategies
    example_list_strategies()

    # Basic backtest
    example_basic_backtest()

    # Strategy comparison
    example_strategy_comparison()

    # Parameter optimization
    example_parameter_optimization()

    # Performance report
    example_performance_report()

    print("\n" + "=" * 60)
    print("  Examples completed!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
