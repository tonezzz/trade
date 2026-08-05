"""
Backtesting engine for trading strategies.
Provides framework for defining strategies, running backtests, and analyzing performance.
"""
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
import yaml
import json
from pathlib import Path

# Technical indicators
try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    print("Warning: TA-Lib not installed. Some backtesting features will be limited.")


@dataclass
class Trade:
    """Represents a single trade."""
    entry_date: date
    exit_date: Optional[date] = None
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: float = 0.0
    direction: str = 'long'  # 'long' or 'short'
    entry_value: float = 0.0
    exit_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    commission: float = 0.0
    slippage: float = 0.0
    exit_reason: Optional[str] = None

    def __post_init__(self):
        self.entry_value = self.entry_price * self.quantity

    def close(self, exit_price: float, exit_date: date, exit_reason: str = 'signal'):
        """Close the trade."""
        self.exit_price = exit_price
        self.exit_date = exit_date
        self.exit_value = exit_price * self.quantity
        self.exit_reason = exit_reason

        if self.direction == 'long':
            self.pnl = (self.exit_price - self.entry_price) * self.quantity
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.quantity

        self.pnl -= self.commission + self.slippage
        self.pnl_pct = (self.pnl / self.entry_value) * 100 if self.entry_value > 0 else 0


@dataclass
class Position:
    """Represents current position."""
    symbol: str
    quantity: float = 0.0
    entry_price: float = 0.0
    entry_date: Optional[date] = None
    direction: str = 'long'
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def is_open(self) -> bool:
        return self.quantity != 0

    @property
    def value(self) -> float:
        return abs(self.quantity) * self.entry_price


@dataclass
class BacktestConfig:
    """Configuration for backtesting."""
    initial_capital: float = 100000.0
    commission_rate: float = 0.001
    slippage_rate: float = 0.0001
    max_position_size: float = 0.2
    max_total_exposure: float = 1.0
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10
    risk_free_rate: float = 0.02
    periods_per_year: int = 252

    @classmethod
    def from_yaml(cls, config_path: str = 'config/backtesting.yml') -> 'BacktestConfig':
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            return cls(
                initial_capital=config.get('initial_capital', {}).get('default', 100000.0),
                commission_rate=config.get('commission', {}).get('value', 0.001),
                slippage_rate=config.get('slippage', {}).get('value', 0.0001),
                max_position_size=config.get('risk_management', {}).get('max_position_size', 0.2),
                max_total_exposure=config.get('risk_management', {}).get('max_total_exposure', 1.0),
                stop_loss_pct=config.get('default_stops', {}).get('stop_loss', {}).get('value', 0.05),
                take_profit_pct=config.get('default_stops', {}).get('take_profit', {}).get('value', 0.10),
                risk_free_rate=config.get('metrics', {}).get('risk_free_rate', 0.02),
                periods_per_year=config.get('metrics', {}).get('periods_per_year', 252)
            )
        except Exception as e:
            print(f"Warning: Could not load config file, using defaults: {e}")
            return cls()


class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.parameters = parameters or {}
        self.signals: pd.Series = None

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        pass

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the strategy.
        Override this method to add custom indicators.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicator columns
        """
        return data.copy()


class BacktestEngine:
    """Main backtesting engine."""

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.cash = self.config.initial_capital
        self.equity = self.config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.current_date: Optional[date] = None
        self.data: Optional[pd.DataFrame] = None
        self.strategy: Optional[Strategy] = None
        self.backtest_id: str = str(uuid.uuid4())[:8]

    def set_data(self, data: pd.DataFrame):
        """Set historical data for backtesting."""
        required_cols = ['date', 'open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")

        # Ensure data is sorted by date
        self.data = data.sort_values('date').reset_index(drop=True).copy()
        self.data.set_index('date', inplace=True)

    def set_strategy(self, strategy: Strategy):
        """Set the trading strategy."""
        self.strategy = strategy

    def calculate_position_size(self, price: float, signal: int) -> float:
        """Calculate position size based on risk management."""
        max_position_value = self.equity * self.config.max_position_size
        position_size = max_position_value / price

        # Round to reasonable precision
        position_size = round(position_size, 2)

        return position_size

    def execute_trade(self, symbol: str, signal: int, price: float, date: date) -> Optional[Trade]:
        """Execute a trade based on signal."""
        commission = price * abs(signal) * self.config.commission_rate
        slippage = price * self.config.slippage_rate

        if signal == 1:  # Buy signal
            if symbol in self.positions and self.positions[symbol].is_open:
                return None  # Already have position

            quantity = self.calculate_position_size(price, signal)
            if quantity <= 0:
                return None

            total_cost = (price * quantity) + commission + slippage
            if total_cost > self.cash:
                quantity = (self.cash - commission - slippage) / price
                if quantity <= 0:
                    return None
                total_cost = (price * quantity) + commission + slippage

            self.cash -= total_cost

            trade = Trade(
                entry_date=date,
                entry_price=price,
                quantity=quantity,
                direction='long',
                commission=commission,
                slippage=slippage
            )

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                entry_date=date,
                direction='long',
                stop_loss=price * (1 - self.config.stop_loss_pct),
                take_profit=price * (1 + self.config.take_profit_pct)
            )

            return trade

        elif signal == -1:  # Sell signal
            if symbol not in self.positions or not self.positions[symbol].is_open:
                return None  # No position to close

            position = self.positions[symbol]
            trade = Trade(
                entry_date=position.entry_date,
                entry_price=position.entry_price,
                quantity=position.quantity,
                direction=position.direction,
                commission=commission,
                slippage=slippage
            )

            trade.close(price, date, 'signal')

            self.cash += trade.exit_value - commission - slippage
            self.positions[symbol] = Position(symbol=symbol)

            return trade

        return None

    def check_stops(self, symbol: str, high: float, low: float, date: date) -> Optional[Trade]:
        """Check if stop-loss or take-profit is triggered."""
        if symbol not in self.positions or not self.positions[symbol].is_open:
            return None

        position = self.positions[symbol]
        exit_price = None
        exit_reason = None

        if position.direction == 'long':
            if low <= position.stop_loss:
                exit_price = position.stop_loss
                exit_reason = 'stop_loss'
            elif high >= position.take_profit:
                exit_price = position.take_profit
                exit_reason = 'take_profit'
        else:  # short
            if high >= position.stop_loss:
                exit_price = position.stop_loss
                exit_reason = 'stop_loss'
            elif low <= position.take_profit:
                exit_price = position.take_profit
                exit_reason = 'take_profit'

        if exit_price:
            commission = exit_price * position.quantity * self.config.commission_rate
            slippage = exit_price * self.config.slippage_rate

            trade = Trade(
                entry_date=position.entry_date,
                entry_price=position.entry_price,
                quantity=position.quantity,
                direction=position.direction,
                commission=commission,
                slippage=slippage
            )

            trade.close(exit_price, date, exit_reason)

            self.cash += trade.exit_value - commission - slippage
            self.positions[symbol] = Position(symbol=symbol)

            return trade

        return None

    def update_equity(self, date: date, close_price: float):
        """Update equity curve."""
        position_value = 0
        for pos in self.positions.values():
            if pos.is_open:
                position_value += pos.quantity * close_price

        self.equity = self.cash + position_value

        self.equity_curve.append({
            'date': date,
            'equity': self.equity,
            'cash': self.cash,
            'position_value': position_value
        })

    def run(self) -> Dict[str, Any]:
        """Run the backtest."""
        if self.data is None:
            raise ValueError("No data set for backtesting")
        if self.strategy is None:
            raise ValueError("No strategy set for backtesting")

        # Reset state
        self.cash = self.config.initial_capital
        self.equity = self.config.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []

        # Generate signals
        data_with_indicators = self.strategy.calculate_indicators(self.data)
        signals = self.strategy.generate_signals(data_with_indicators)

        # Run backtest
        for idx, row in data_with_indicators.iterrows():
            self.current_date = idx
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']

            # Check stops for existing positions
            for symbol in list(self.positions.keys()):
                trade = self.check_stops(symbol, high_price, low_price, idx)
                if trade:
                    self.trades.append(trade)

            # Execute new signals
            signal = signals.loc[idx] if idx in signals.index else 0
            if signal != 0:
                trade = self.execute_trade('symbol', signal, close_price, idx)
                if trade:
                    self.trades.append(trade)

            # Update equity
            self.update_equity(idx, close_price)

        # Close any remaining positions at the end
        last_date = data_with_indicators.index[-1]
        last_close = data_with_indicators.iloc[-1]['close']

        for symbol, position in list(self.positions.items()):
            if position.is_open:
                commission = last_close * position.quantity * self.config.commission_rate
                trade = Trade(
                    entry_date=position.entry_date,
                    entry_price=position.entry_price,
                    quantity=position.quantity,
                    direction=position.direction,
                    commission=commission
                )
                trade.close(last_close, last_date, 'end_of_data')
                self.cash += trade.exit_value - commission
                self.trades.append(trade)
                self.positions[symbol] = Position(symbol=symbol)

        # Final equity update
        self.update_equity(last_date, last_close)

        # Calculate performance metrics
        metrics = self.calculate_metrics()

        return {
            'backtest_id': self.backtest_id,
            'strategy_name': self.strategy.name,
            'parameters': self.strategy.parameters,
            'start_date': str(data_with_indicators.index[0]),
            'end_date': str(data_with_indicators.index[-1]),
            'initial_capital': self.config.initial_capital,
            'final_capital': self.equity,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'metrics': metrics
        }

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.equity_curve:
            return {}

        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('date', inplace=True)

        # Basic returns
        total_return = (self.equity - self.config.initial_capital) / self.config.initial_capital
        total_return_pct = total_return * 100

        # Daily returns
        equity_df['returns'] = equity_df['equity'].pct_change().fillna(0)

        # Drawdown calculation
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = equity_df['equity'] - equity_df['cummax']
        equity_df['drawdown_pct'] = (equity_df['drawdown'] / equity_df['cummax']) * 100

        max_drawdown = equity_df['drawdown'].min()
        max_drawdown_pct = equity_df['drawdown_pct'].min()

        # Sharpe ratio
        returns = equity_df['returns']
        if returns.std() > 0:
            sharpe_ratio = (returns.mean() * self.config.periods_per_year - self.config.risk_free_rate) / \
                          (returns.std() * np.sqrt(self.config.periods_per_year))
        else:
            sharpe_ratio = 0

        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino_ratio = (returns.mean() * self.config.periods_per_year - self.config.risk_free_rate) / \
                          (downside_returns.std() * np.sqrt(self.config.periods_per_year))
        else:
            sortino_ratio = 0

        # Trade statistics
        if self.trades:
            winning_trades = [t for t in self.trades if t.pnl and t.pnl > 0]
            losing_trades = [t for t in self.trades if t.pnl and t.pnl <= 0]

            win_rate = len(winning_trades) / len(self.trades) * 100 if self.trades else 0

            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

            profit_factor = abs(sum(t.pnl for t in winning_trades)) / \
                          abs(sum(t.pnl for t in losing_trades)) if losing_trades else float('inf')

            largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
            largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0

            # Average trade duration
            durations = [(t.exit_date - t.entry_date).days for t in self.trades if t.exit_date]
            avg_duration = np.mean(durations) if durations else 0
        else:
            winning_trades = []
            losing_trades = []
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
            largest_win = 0
            largest_loss = 0
            avg_duration = 0

        return {
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'avg_trade_duration': avg_duration
        }


# Predefined Strategies

class MovingAverageCrossover(Strategy):
    """Moving Average Crossover Strategy."""

    def __init__(self, fast_period: int = 10, slow_period: int = 30):
        parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period
        }
        super().__init__('Moving Average Crossover', parameters)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages."""
        df = data.copy()
        if HAS_TALIB:
            df['fast_ma'] = talib.SMA(df['close'], timeperiod=self.parameters['fast_period'])
            df['slow_ma'] = talib.SMA(df['close'], timeperiod=self.parameters['slow_period'])
        else:
            # Fallback to pandas rolling mean
            df['fast_ma'] = df['close'].rolling(window=self.parameters['fast_period']).mean()
            df['slow_ma'] = df['close'].rolling(window=self.parameters['slow_period']).mean()
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate crossover signals."""
        signals = pd.Series(0, index=data.index)

        # Calculate crossovers
        fast_ma = data['fast_ma']
        slow_ma = data['slow_ma']

        # Buy when fast MA crosses above slow MA
        signals[(fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))] = 1

        # Sell when fast MA crosses below slow MA
        signals[(fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))] = -1

        return signals


class RSIStrategy(Strategy):
    """RSI-based Strategy."""

    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        parameters = {
            'period': period,
            'oversold': oversold,
            'overbought': overbought
        }
        super().__init__('RSI Strategy', parameters)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI."""
        df = data.copy()
        if HAS_TALIB:
            df['rsi'] = talib.RSI(df['close'], timeperiod=self.parameters['period'])
        else:
            # Fallback to manual RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.parameters['period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.parameters['period']).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate RSI signals."""
        signals = pd.Series(0, index=data.index)
        rsi = data['rsi']

        # Buy when RSI crosses above oversold level
        signals[(rsi > self.parameters['oversold']) & (rsi.shift(1) <= self.parameters['oversold'])] = 1

        # Sell when RSI crosses below overbought level
        signals[(rsi < self.parameters['overbought']) & (rsi.shift(1) >= self.parameters['overbought'])] = -1

        return signals


class MACDStrategy(Strategy):
    """MACD Strategy."""

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        parameters = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        }
        super().__init__('MACD Strategy', parameters)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD."""
        df = data.copy()
        if HAS_TALIB:
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
                df['close'],
                fastperiod=self.parameters['fast_period'],
                slowperiod=self.parameters['slow_period'],
                signalperiod=self.parameters['signal_period']
            )
        else:
            # Fallback to manual MACD calculation
            exp1 = df['close'].ewm(span=self.parameters['fast_period'], adjust=False).mean()
            exp2 = df['close'].ewm(span=self.parameters['slow_period'], adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=self.parameters['signal_period'], adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate MACD signals."""
        signals = pd.Series(0, index=data.index)
        macd_hist = data['macd_hist']

        # Buy when MACD histogram crosses above zero
        signals[(macd_hist > 0) & (macd_hist.shift(1) <= 0)] = 1

        # Sell when MACD histogram crosses below zero
        signals[(macd_hist < 0) & (macd_hist.shift(1) >= 0)] = -1

        return signals


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands Strategy."""

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        parameters = {
            'period': period,
            'std_dev': std_dev
        }
        super().__init__('Bollinger Bands Strategy', parameters)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        df = data.copy()
        if HAS_TALIB:
            df['bb_middle'], df['bb_upper'], df['bb_lower'] = talib.BBANDS(
                df['close'],
                timeperiod=self.parameters['period'],
                nbdevup=self.parameters['std_dev'],
                nbdevdn=self.parameters['std_dev']
            )
        else:
            # Fallback to manual Bollinger Bands calculation
            df['bb_middle'] = df['close'].rolling(window=self.parameters['period']).mean()
            std = df['close'].rolling(window=self.parameters['period']).std()
            df['bb_upper'] = df['bb_middle'] + (std * self.parameters['std_dev'])
            df['bb_lower'] = df['bb_middle'] - (std * self.parameters['std_dev'])
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate Bollinger Bands signals."""
        signals = pd.Series(0, index=data.index)
        close = data['close']
        bb_lower = data['bb_lower']
        bb_upper = data['bb_upper']

        # Buy when price crosses above lower band
        signals[(close > bb_lower) & (close.shift(1) <= bb_lower.shift(1))] = 1

        # Sell when price crosses below upper band
        signals[(close < bb_upper) & (close.shift(1) >= bb_upper.shift(1))] = -1

        return signals


class BuyAndHold(Strategy):
    """Buy and Hold Benchmark Strategy."""

    def __init__(self):
        super().__init__('Buy and Hold', {})

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """No indicators needed."""
        return data.copy()

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Buy on first day, hold forever."""
        signals = pd.Series(0, index=data.index)
        signals.iloc[0] = 1  # Buy on first day
        return signals


# Strategy Registry
STRATEGY_REGISTRY = {
    'moving_average_crossover': MovingAverageCrossover,
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'bollinger_bands': BollingerBandsStrategy,
    'buy_and_hold': BuyAndHold
}


def get_strategy(strategy_name: str, parameters: Optional[Dict[str, Any]] = None) -> Strategy:
    """Get a strategy instance by name."""
    strategy_class = STRATEGY_REGISTRY.get(strategy_name.lower())
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(STRATEGY_REGISTRY.keys())}")

    if parameters:
        return strategy_class(**parameters)
    return strategy_class()


def list_strategies() -> List[Dict[str, Any]]:
    """List available strategies with their default parameters."""
    strategies = []
    for name, strategy_class in STRATEGY_REGISTRY.items():
        # Create instance to get default parameters
        instance = strategy_class()
        strategies.append({
            'name': name,
            'display_name': instance.name,
            'parameters': instance.parameters
        })
    return strategies


# Parameter Optimization

class ParameterOptimizer:
    """Optimize strategy parameters using grid search or random search."""

    def __init__(self, engine: BacktestEngine, data: pd.DataFrame):
        self.engine = engine
        self.data = data

    def grid_search(self, strategy_name: str, param_grid: Dict[str, List[Any]],
                   metric: str = 'sharpe_ratio') -> Dict[str, Any]:
        """
        Perform grid search optimization.

        Args:
            strategy_name: Name of strategy to optimize
            param_grid: Dictionary of parameter names and values to test
            metric: Metric to optimize (sharpe_ratio, total_return, etc.)

        Returns:
            Best parameters and results
        """
        results = []

        # Generate all parameter combinations
        from itertools import product
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())

        for combination in product(*param_values):
            params = dict(zip(param_names, combination))

            # Run backtest with these parameters
            engine = BacktestEngine(self.engine.config)
            engine.set_data(self.data.copy())
            strategy = get_strategy(strategy_name, params)
            engine.set_strategy(strategy)

            try:
                result = engine.run()
                results.append({
                    'parameters': params,
                    'metrics': result['metrics']
                })
            except Exception as e:
                print(f"Error with parameters {params}: {e}")
                continue

        # Find best result
        if not results:
            return {'best_parameters': {}, 'all_results': []}

        best_result = max(results, key=lambda x: x['metrics'].get(metric, -float('inf')))

        return {
            'best_parameters': best_result['parameters'],
            'best_metrics': best_result['metrics'],
            'all_results': results
        }

    def random_search(self, strategy_name: str, param_ranges: Dict[str, Tuple[Any, Any]],
                     n_iterations: int = 100, metric: str = 'sharpe_ratio') -> Dict[str, Any]:
        """
        Perform random search optimization.

        Args:
            strategy_name: Name of strategy to optimize
            param_ranges: Dictionary of parameter names and (min, max) ranges
            n_iterations: Number of random iterations
            metric: Metric to optimize

        Returns:
            Best parameters and results
        """
        results = []

        for _ in range(n_iterations):
            params = {}
            for param_name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[param_name] = np.random.randint(min_val, max_val + 1)
                else:
                    params[param_name] = np.random.uniform(min_val, max_val)

            # Run backtest
            engine = BacktestEngine(self.engine.config)
            engine.set_data(self.data.copy())
            strategy = get_strategy(strategy_name, params)
            engine.set_strategy(strategy)

            try:
                result = engine.run()
                results.append({
                    'parameters': params,
                    'metrics': result['metrics']
                })
            except Exception as e:
                print(f"Error with parameters {params}: {e}")
                continue

        if not results:
            return {'best_parameters': {}, 'all_results': []}

        best_result = max(results, key=lambda x: x['metrics'].get(metric, -float('inf')))

        return {
            'best_parameters': best_result['parameters'],
            'best_metrics': best_result['metrics'],
            'all_results': results
        }


# Walk-Forward Analysis

class WalkForwardAnalysis:
    """Perform walk-forward analysis for strategy validation."""

    def __init__(self, engine: BacktestEngine, data: pd.DataFrame):
        self.engine = engine
        self.data = data

    def run(self, strategy_name: str, parameters: Dict[str, Any],
            train_size: float = 0.6, test_size: float = 0.2,
            step_size: float = 0.1) -> Dict[str, Any]:
        """
        Run walk-forward analysis.

        Args:
            strategy_name: Name of strategy
            parameters: Strategy parameters
            train_size: Fraction of data for training
            test_size: Fraction of data for testing
            step_size: Fraction of data to step forward

        Returns:
            Walk-forward analysis results
        """
        total_periods = len(self.data)
        train_periods = int(total_periods * train_size)
        test_periods = int(total_periods * test_size)
        step_periods = int(total_periods * step_size)

        results = []
        start_idx = 0

        while start_idx + train_periods + test_periods <= total_periods:
            train_end = start_idx + train_periods
            test_end = train_end + test_periods

            # Split data
            train_data = self.data.iloc[start_idx:train_end]
            test_data = self.data.iloc[train_end:test_end]

            # Optimize on training data
            optimizer = ParameterOptimizer(self.engine, train_data)

            # Define parameter ranges for optimization
            param_ranges = self._get_param_ranges(strategy_name)

            if param_ranges:
                opt_result = optimizer.random_search(strategy_name, param_ranges, n_iterations=50)
                best_params = opt_result['best_parameters']
            else:
                best_params = parameters

            # Test on out-of-sample data
            test_engine = BacktestEngine(self.engine.config)
            test_engine.set_data(test_data.copy())
            strategy = get_strategy(strategy_name, best_params)
            test_engine.set_strategy(strategy)

            test_result = test_engine.run()

            results.append({
                'train_start': str(self.data.index[start_idx]),
                'train_end': str(self.data.index[train_end - 1]),
                'test_start': str(self.data.index[train_end]),
                'test_end': str(self.data.index[test_end - 1]),
                'parameters': best_params,
                'test_metrics': test_result['metrics']
            })

            start_idx += step_periods

        # Aggregate results
        if results:
            avg_metrics = {}
            for metric in results[0]['test_metrics'].keys():
                values = [r['test_metrics'][metric] for r in results if r['test_metrics'][metric] is not None]
                if values:
                    avg_metrics[f'avg_{metric}'] = np.mean(values)
                    avg_metrics[f'std_{metric}'] = np.std(values)

            return {
                'results': results,
                'aggregate_metrics': avg_metrics
            }

        return {'results': [], 'aggregate_metrics': {}}

    def _get_param_ranges(self, strategy_name: str) -> Dict[str, Tuple[Any, Any]]:
        """Get default parameter ranges for optimization."""
        ranges = {
            'moving_average_crossover': {
                'fast_period': (5, 20),
                'slow_period': (20, 60)
            },
            'rsi': {
                'period': (10, 20),
                'oversold': (20, 35),
                'overbought': (65, 80)
            },
            'macd': {
                'fast_period': (8, 16),
                'slow_period': (20, 35),
                'signal_period': (5, 12)
            },
            'bollinger_bands': {
                'period': (10, 30),
                'std_dev': (1.5, 3.0)
            }
        }
        return ranges.get(strategy_name.lower(), {})


# Strategy Comparison

class StrategyComparator:
    """Compare multiple strategies on the same data."""

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()

    def compare(self, data: pd.DataFrame, strategies: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Compare multiple strategies.

        Args:
            data: Historical data
            strategies: List of dicts with 'name' and optional 'parameters'

        Returns:
            DataFrame with comparison results
        """
        results = []

        for strategy_config in strategies:
            strategy_name = strategy_config['name']
            parameters = strategy_config.get('parameters', {})

            engine = BacktestEngine(self.config)
            engine.set_data(data.copy())
            strategy = get_strategy(strategy_name, parameters)
            engine.set_strategy(strategy)

            try:
                result = engine.run()
                metrics = result['metrics']
                metrics['strategy_name'] = strategy.name
                metrics['parameters'] = json.dumps(parameters)
                results.append(metrics)
            except Exception as e:
                print(f"Error running {strategy_name}: {e}")
                continue

        return pd.DataFrame(results)


# Performance Report Generation

class PerformanceReport:
    """Generate performance reports for backtest results."""

    def __init__(self, result: Dict[str, Any]):
        self.result = result

    def generate_text_report(self) -> str:
        """Generate a text-based performance report."""
        metrics = self.result['metrics']
        params = self.result.get('parameters', {})

        report = []
        report.append("=" * 60)
        report.append("BACKTEST PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Strategy: {self.result['strategy_name']}")
        report.append(f"Backtest ID: {self.result['backtest_id']}")
        report.append(f"Period: {self.result['start_date']} to {self.result['end_date']}")
        report.append("")
        report.append("Parameters:")
        for key, value in params.items():
            report.append(f"  {key}: {value}")
        report.append("")
        report.append("-" * 60)
        report.append("PERFORMANCE METRICS")
        report.append("-" * 60)
        report.append(f"Initial Capital: ${self.result['initial_capital']:,.2f}")
        report.append(f"Final Capital: ${self.result['final_capital']:,.2f}")
        report.append(f"Total Return: {metrics['total_return_pct']:.2f}%")
        report.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report.append(f"Sortino Ratio: {metrics['sortino_ratio']:.2f}")
        report.append(f"Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        report.append("")
        report.append("-" * 60)
        report.append("TRADE STATISTICS")
        report.append("-" * 60)
        report.append(f"Total Trades: {metrics['total_trades']}")
        report.append(f"Winning Trades: {metrics['winning_trades']}")
        report.append(f"Losing Trades: {metrics['losing_trades']}")
        report.append(f"Win Rate: {metrics['win_rate']:.2f}%")
        report.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
        report.append(f"Average Win: ${metrics['avg_win']:,.2f}")
        report.append(f"Average Loss: ${metrics['avg_loss']:,.2f}")
        report.append(f"Largest Win: ${metrics['largest_win']:,.2f}")
        report.append(f"Largest Loss: ${metrics['largest_loss']:,.2f}")
        report.append(f"Average Trade Duration: {metrics['avg_trade_duration']:.1f} days")
        report.append("=" * 60)

        return "\n".join(report)

    def generate_json_report(self) -> str:
        """Generate a JSON report."""
        return json.dumps(self.result, indent=2, default=str)

    def save_report(self, output_dir: str = 'backtest_results'):
        """Save report to files."""
        Path(output_dir).mkdir(exist_ok=True)

        backtest_id = self.result['backtest_id']

        # Save text report
        text_path = Path(output_dir) / f"{backtest_id}_report.txt"
        with open(text_path, 'w') as f:
            f.write(self.generate_text_report())

        # Save JSON report
        json_path = Path(output_dir) / f"{backtest_id}_report.json"
        with open(json_path, 'w') as f:
            f.write(self.generate_json_report())

        # Save equity curve
        equity_df = pd.DataFrame(self.result['equity_curve'])
        equity_path = Path(output_dir) / f"{backtest_id}_equity.csv"
        equity_df.to_csv(equity_path, index=False)

        # Save trades
        trades_data = []
        for trade in self.result['trades']:
            trades_data.append({
                'entry_date': trade.entry_date,
                'exit_date': trade.exit_date,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'direction': trade.direction,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnl_pct,
                'commission': trade.commission,
                'exit_reason': trade.exit_reason
            })

        if trades_data:
            trades_df = pd.DataFrame(trades_data)
            trades_path = Path(output_dir) / f"{backtest_id}_trades.csv"
            trades_df.to_csv(trades_path, index=False)

        return {
            'text_report': str(text_path),
            'json_report': str(json_path),
            'equity_curve': str(equity_path),
            'trades': str(trades_path) if trades_data else None
        }
