"""
Tests for backtesting engine.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from src.backtesting import (
    BacktestEngine, BacktestConfig, Trade, Position,
    MovingAverageCrossover, RSIStrategy, MACDStrategy,
    BollingerBandsStrategy, BuyAndHold,
    get_strategy, list_strategies,
    ParameterOptimizer, WalkForwardAnalysis, StrategyComparator,
    PerformanceReport, STRATEGY_REGISTRY
)


@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    np.random.seed(42)
    n = 500
    dates = [date.today() - timedelta(days=n-i) for i in range(n)]

    # Generate random walk price data
    price = 100.0
    prices = []
    for _ in range(n):
        change = np.random.normal(0, 0.02)
        price = price * (1 + change)
        prices.append(price)

    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, n)
    })

    return data


@pytest.fixture
def backtest_config():
    """Create backtest configuration for testing."""
    return BacktestConfig(
        initial_capital=10000.0,
        commission_rate=0.001,
        slippage_rate=0.0001,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )


class TestBacktestConfig:
    """Tests for BacktestConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = BacktestConfig()
        assert config.initial_capital == 100000.0
        assert config.commission_rate == 0.001
        assert config.slippage_rate == 0.0001

    def test_custom_config(self):
        """Test custom configuration."""
        config = BacktestConfig(
            initial_capital=50000.0,
            commission_rate=0.002
        )
        assert config.initial_capital == 50000.0
        assert config.commission_rate == 0.002


class TestTrade:
    """Tests for Trade class."""

    def test_trade_creation(self):
        """Test creating a trade."""
        trade = Trade(
            entry_date=date.today(),
            entry_price=100.0,
            quantity=10.0,
            direction='long'
        )
        assert trade.entry_price == 100.0
        assert trade.quantity == 10.0
        assert trade.entry_value == 1000.0
        assert trade.direction == 'long'

    def test_trade_close_long(self):
        """Test closing a long trade."""
        trade = Trade(
            entry_date=date.today(),
            entry_price=100.0,
            quantity=10.0,
            direction='long',
            commission=5.0
        )
        trade.close(110.0, date.today() + timedelta(days=5), 'signal')

        assert trade.exit_price == 110.0
        assert trade.exit_value == 1100.0
        assert trade.pnl == 95.0  # (110-100)*10 - 5
        assert trade.exit_reason == 'signal'

    def test_trade_close_short(self):
        """Test closing a short trade."""
        trade = Trade(
            entry_date=date.today(),
            entry_price=100.0,
            quantity=10.0,
            direction='short',
            commission=5.0
        )
        trade.close(90.0, date.today() + timedelta(days=5), 'signal')

        assert trade.exit_price == 90.0
        assert trade.exit_value == 900.0
        assert trade.pnl == 95.0  # (100-90)*10 - 5


class TestPosition:
    """Tests for Position class."""

    def test_position_creation(self):
        """Test creating a position."""
        position = Position(
            symbol='TEST',
            quantity=100.0,
            entry_price=50.0,
            direction='long'
        )
        assert position.symbol == 'TEST'
        assert position.quantity == 100.0
        assert position.is_open == True
        assert position.value == 5000.0

    def test_closed_position(self):
        """Test closed position."""
        position = Position(symbol='TEST', quantity=0.0)
        assert position.is_open == False


class TestBacktestEngine:
    """Tests for BacktestEngine."""

    def test_engine_initialization(self, backtest_config):
        """Test engine initialization."""
        engine = BacktestEngine(backtest_config)
        assert engine.cash == backtest_config.initial_capital
        assert engine.equity == backtest_config.initial_capital
        assert len(engine.trades) == 0
        assert len(engine.equity_curve) == 0

    def test_set_data(self, backtest_config, sample_data):
        """Test setting data."""
        engine = BacktestEngine(backtest_config)
        engine.set_data(sample_data)
        assert engine.data is not None
        assert len(engine.data) == len(sample_data)

    def test_set_data_missing_columns(self, backtest_config):
        """Test setting data with missing columns."""
        engine = BacktestEngine(backtest_config)
        bad_data = pd.DataFrame({'date': [date.today()], 'close': [100.0]})
        with pytest.raises(ValueError, match="Missing required column"):
            engine.set_data(bad_data)

    def test_set_strategy(self, backtest_config):
        """Test setting strategy."""
        engine = BacktestEngine(backtest_config)
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        engine.set_strategy(strategy)
        assert engine.strategy == strategy

    def test_run_backtest(self, backtest_config, sample_data):
        """Test running a backtest."""
        engine = BacktestEngine(backtest_config)
        engine.set_data(sample_data)
        strategy = BuyAndHold()
        engine.set_strategy(strategy)

        result = engine.run()

        assert 'backtest_id' in result
        assert 'strategy_name' in result
        assert 'metrics' in result
        assert 'equity_curve' in result
        assert 'trades' in result
        assert result['initial_capital'] == backtest_config.initial_capital
        assert len(result['equity_curve']) > 0

    def test_run_without_data(self, backtest_config):
        """Test running without data raises error."""
        engine = BacktestEngine(backtest_config)
        strategy = BuyAndHold()
        engine.set_strategy(strategy)

        with pytest.raises(ValueError, match="No data set"):
            engine.run()

    def test_run_without_strategy(self, backtest_config, sample_data):
        """Test running without strategy raises error."""
        engine = BacktestEngine(backtest_config)
        engine.set_data(sample_data)

        with pytest.raises(ValueError, match="No strategy set"):
            engine.run()

    def test_calculate_metrics(self, backtest_config, sample_data):
        """Test metrics calculation."""
        engine = BacktestEngine(backtest_config)
        engine.set_data(sample_data)
        strategy = BuyAndHold()
        engine.set_strategy(strategy)

        result = engine.run()
        metrics = result['metrics']

        assert 'total_return' in metrics
        assert 'total_return_pct' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
        assert 'win_rate' in metrics
        assert 'total_trades' in metrics


class TestStrategies:
    """Tests for trading strategies."""

    def test_moving_average_crossover(self, sample_data):
        """Test Moving Average Crossover strategy."""
        strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
        data = strategy.calculate_indicators(sample_data)
        signals = strategy.generate_signals(data)

        assert 'fast_ma' in data.columns
        assert 'slow_ma' in data.columns
        assert len(signals) == len(data)
        assert signals.isin([0, 1, -1]).all()

    def test_rsi_strategy(self, sample_data):
        """Test RSI strategy."""
        strategy = RSIStrategy(period=14, oversold=30, overbought=70)
        data = strategy.calculate_indicators(sample_data)
        signals = strategy.generate_signals(data)

        assert 'rsi' in data.columns
        assert len(signals) == len(data)
        assert signals.isin([0, 1, -1]).all()

    def test_macd_strategy(self, sample_data):
        """Test MACD strategy."""
        strategy = MACDStrategy(fast_period=12, slow_period=26, signal_period=9)
        data = strategy.calculate_indicators(sample_data)
        signals = strategy.generate_signals(data)

        assert 'macd' in data.columns
        assert 'macd_signal' in data.columns
        assert 'macd_hist' in data.columns
        assert len(signals) == len(data)

    def test_bollinger_bands_strategy(self, sample_data):
        """Test Bollinger Bands strategy."""
        strategy = BollingerBandsStrategy(period=20, std_dev=2.0)
        data = strategy.calculate_indicators(sample_data)
        signals = strategy.generate_signals(data)

        assert 'bb_middle' in data.columns
        assert 'bb_upper' in data.columns
        assert 'bb_lower' in data.columns
        assert len(signals) == len(data)

    def test_buy_and_hold(self, sample_data):
        """Test Buy and Hold strategy."""
        strategy = BuyAndHold()
        data = strategy.calculate_indicators(sample_data)
        signals = strategy.generate_signals(data)

        assert len(signals) == len(data)
        assert signals.iloc[0] == 1  # Buy on first day


class TestStrategyRegistry:
    """Tests for strategy registry."""

    def test_get_strategy(self):
        """Test getting strategy from registry."""
        strategy = get_strategy('moving_average_crossover')
        assert isinstance(strategy, MovingAverageCrossover)

        strategy = get_strategy('rsi')
        assert isinstance(strategy, RSIStrategy)

    def test_get_strategy_with_parameters(self):
        """Test getting strategy with custom parameters."""
        strategy = get_strategy('moving_average_crossover', {'fast_period': 5, 'slow_period': 15})
        assert strategy.parameters['fast_period'] == 5
        assert strategy.parameters['slow_period'] == 15

    def test_get_strategy_invalid(self):
        """Test getting invalid strategy raises error."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            get_strategy('invalid_strategy')

    def test_list_strategies(self):
        """Test listing strategies."""
        strategies = list_strategies()
        assert len(strategies) > 0
        assert all('name' in s for s in strategies)
        assert all('display_name' in s for s in strategies)
        assert all('parameters' in s for s in strategies)


class TestParameterOptimizer:
    """Tests for parameter optimizer."""

    def test_grid_search(self, sample_data):
        """Test grid search optimization."""
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        optimizer = ParameterOptimizer(engine, sample_data)

        param_grid = {
            'fast_period': [5, 10],
            'slow_period': [20, 30]
        }

        result = optimizer.grid_search('moving_average_crossover', param_grid)

        assert 'best_parameters' in result
        assert 'best_metrics' in result
        assert 'all_results' in result
        assert len(result['all_results']) == 4  # 2 * 2 combinations

    def test_random_search(self, sample_data):
        """Test random search optimization."""
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        optimizer = ParameterOptimizer(engine, sample_data)

        param_ranges = {
            'fast_period': (5, 15),
            'slow_period': (20, 40)
        }

        result = optimizer.random_search('moving_average_crossover', param_ranges, n_iterations=5)

        assert 'best_parameters' in result
        assert 'best_metrics' in result
        assert 'all_results' in result
        assert len(result['all_results']) <= 5


class TestWalkForwardAnalysis:
    """Tests for walk-forward analysis."""

    def test_walk_forward_analysis(self, sample_data):
        """Test walk-forward analysis."""
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        wfa = WalkForwardAnalysis(engine, sample_data)

        result = wfa.run(
            'moving_average_crossover',
            {'fast_period': 10, 'slow_period': 30},
            train_size=0.5,
            test_size=0.2,
            step_size=0.1
        )

        assert 'results' in result
        assert 'aggregate_metrics' in result
        assert len(result['results']) > 0


class TestStrategyComparator:
    """Tests for strategy comparator."""

    def test_compare_strategies(self, sample_data):
        """Test comparing multiple strategies."""
        config = BacktestConfig(initial_capital=10000.0)
        comparator = StrategyComparator(config)

        strategies = [
            {'name': 'buy_and_hold'},
            {'name': 'moving_average_crossover', 'parameters': {'fast_period': 10, 'slow_period': 30}}
        ]

        result = comparator.compare(sample_data, strategies)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'strategy_name' in result.columns
        assert 'total_return_pct' in result.columns
        assert 'sharpe_ratio' in result.columns


class TestPerformanceReport:
    """Tests for performance report generation."""

    def test_text_report(self, sample_data):
        """Test text report generation."""
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        engine.set_data(sample_data)
        strategy = BuyAndHold()
        engine.set_strategy(strategy)

        result = engine.run()
        report = PerformanceReport(result)
        text_report = report.generate_text_report()

        assert 'BACKTEST PERFORMANCE REPORT' in text_report
        assert 'Strategy:' in text_report
        assert 'PERFORMANCE METRICS' in text_report
        assert 'TRADE STATISTICS' in text_report

    def test_json_report(self, sample_data):
        """Test JSON report generation."""
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        engine.set_data(sample_data)
        strategy = BuyAndHold()
        engine.set_strategy(strategy)

        result = engine.run()
        report = PerformanceReport(result)
        json_report = report.generate_json_report()

        import json
        parsed = json.loads(json_report)
        assert 'backtest_id' in parsed
        assert 'metrics' in parsed
        assert 'equity_curve' in parsed


class TestIntegration:
    """Integration tests for complete backtesting workflow."""

    def test_complete_backtest_workflow(self, sample_data):
        """Test complete backtest from data to report."""
        # Setup
        config = BacktestConfig(initial_capital=50000.0)
        engine = BacktestEngine(config)
        engine.set_data(sample_data)

        # Use strategy
        strategy = MovingAverageCrossover(fast_period=10, slow_period=30)
        engine.set_strategy(strategy)

        # Run backtest
        result = engine.run()

        # Verify results
        assert result['initial_capital'] == 50000.0
        assert result['final_capital'] > 0
        assert len(result['equity_curve']) > 0

        # Generate report
        report = PerformanceReport(result)
        text_report = report.generate_text_report()
        assert len(text_report) > 0

    def test_optimization_workflow(self, sample_data):
        """Test optimization workflow."""
        config = BacktestConfig(initial_capital=10000.0)
        engine = BacktestEngine(config)
        optimizer = ParameterOptimizer(engine, sample_data)

        # Optimize
        param_ranges = {
            'fast_period': (5, 20),
            'slow_period': (20, 50)
        }
        result = optimizer.random_search('moving_average_crossover', param_ranges, n_iterations=10)

        # Use best parameters
        best_params = result['best_parameters']
        engine2 = BacktestEngine(config)
        engine2.set_data(sample_data)
        strategy = get_strategy('moving_average_crossover', best_params)
        engine2.set_strategy(strategy)

        final_result = engine2.run()
        assert final_result['metrics']['total_trades'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
