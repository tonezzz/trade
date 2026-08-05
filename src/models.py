"""
Database models for dollar price data.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ExchangeRate(Base):
    """USD exchange rates to other currencies."""
    __tablename__ = 'exchange_rates'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    base_currency = Column(String(3), nullable=False, default='USD')  # USD
    quote_currency = Column(String(3), nullable=False, index=True)  # EUR, GBP, JPY, etc.
    rate = Column(Float, nullable=False)  # USD to quote_currency
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)  # Data source
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_exchange_date_currency', 'date', 'quote_currency'),
        Index('idx_exchange_currency_date', 'quote_currency', 'date'),
    )
    
    def __repr__(self):
        return f"<ExchangeRate(date={self.date}, base={self.base_currency}, quote={self.quote_currency}, rate={self.rate})>"


class DollarIndex(Base):
    """USD Dollar Index (DXY) data."""
    __tablename__ = 'dollar_index'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    value = Column(Float, nullable=False)  # DXY value
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DollarIndex(date={self.date}, value={self.value})>"


class CommodityPrice(Base):
    """Commodity prices in USD."""
    __tablename__ = 'commodity_prices'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    commodity = Column(String(50), nullable=False, index=True)  # GOLD, SILVER, OIL, etc.
    symbol = Column(String(20), nullable=True, index=True)  # XAUUSD, USOIL, etc.
    price = Column(Float, nullable=False)  # Price in USD
    unit = Column(String(20), nullable=True)  # oz, barrel, lb, etc.
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_commodity_date_symbol', 'date', 'symbol'),
        Index('idx_commodity_symbol_date', 'symbol', 'date'),
    )
    
    def __repr__(self):
        return f"<CommodityPrice(date={self.date}, commodity={self.commodity}, price={self.price})>"


class SignalHistory(Base):
    """Trading signal history for tracking generated signals."""
    __tablename__ = 'signal_history'
    
    id = Column(Integer, primary_key=True)
    asset_type = Column(String(50), nullable=False, index=True)  # currency, commodity, dollar_index
    asset_symbol = Column(String(20), nullable=False, index=True)  # EUR, GOLD, DXY, etc.
    signal_type = Column(String(10), nullable=False)  # buy, sell, hold
    strength = Column(String(20), nullable=False)  # weak, moderate, strong
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    timestamp = Column(DateTime, nullable=False, index=True)
    price = Column(Float, nullable=False)
    indicators = Column(JSON, nullable=True)  # Dictionary of indicator values
    reasons = Column(JSON, nullable=True)  # List of reasons for signal
    timeframe = Column(String(10), nullable=True)  # 1d, 1w, 1m
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_signal_asset_timestamp', 'asset_type', 'asset_symbol', 'timestamp'),
        Index('idx_signal_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SignalHistory(asset={self.asset_symbol}, type={self.signal_type}, confidence={self.confidence})>"


class SignalPerformance(Base):
    """Signal performance metrics for backtesting and evaluation."""
    __tablename__ = 'signal_performance'
    
    id = Column(Integer, primary_key=True)
    asset_type = Column(String(50), nullable=False)
    asset_symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    test_start_date = Column(Date, nullable=False)
    test_end_date = Column(Date, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    total_trades = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    parameters = Column(JSON, nullable=True)  # Signal parameters used
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_performance_asset', 'asset_type', 'asset_symbol'),
        Index('idx_performance_date', 'test_end_date'),
    )
    
    def __repr__(self):
        return f"<SignalPerformance(asset={self.asset_symbol}, return={self.total_return}%, trades={self.total_trades})>"


class BacktestResult(Base):
    """Backtest execution results."""
    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True)
    backtest_id = Column(String(100), nullable=False, unique=True, index=True)
    strategy_name = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    total_return_pct = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=False)
    max_drawdown_pct = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=True)
    total_trades = Column(Integer, nullable=False)
    winning_trades = Column(Integer, nullable=False)
    losing_trades = Column(Integer, nullable=False)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    largest_win = Column(Float, nullable=True)
    largest_loss = Column(Float, nullable=True)
    avg_trade_duration = Column(Float, nullable=True)
    parameters = Column(String(1000), nullable=True)  # JSON string of parameters
    status = Column(String(20), nullable=False, default='completed')  # pending, running, completed, failed
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_backtest_strategy', 'strategy_name', 'symbol'),
        Index('idx_backtest_date', 'start_date', 'end_date'),
    )

    def __repr__(self):
        return f"<BacktestResult(id={self.backtest_id}, strategy={self.strategy_name}, return_pct={self.total_return_pct})>"


class BacktestTrade(Base):
    """Individual trades from backtest execution."""
    __tablename__ = 'backtest_trades'

    id = Column(Integer, primary_key=True)
    backtest_id = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    entry_date = Column(Date, nullable=False, index=True)
    exit_date = Column(Date, nullable=True, index=True)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    direction = Column(String(10), nullable=False)  # long, short
    entry_value = Column(Float, nullable=False)
    exit_value = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    commission = Column(Float, nullable=True)
    slippage = Column(Float, nullable=True)
    exit_reason = Column(String(50), nullable=True)  # stop_loss, take_profit, signal, end_of_data
    duration_days = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_trade_backtest', 'backtest_id', 'entry_date'),
        Index('idx_trade_symbol', 'symbol', 'entry_date'),
    )

    def __repr__(self):
        return f"<BacktestTrade(backtest={self.backtest_id}, entry={self.entry_date}, pnl={self.pnl})>"


class BacktestEquity(Base):
    """Equity curve data points from backtest."""
    __tablename__ = 'backtest_equity'

    id = Column(Integer, primary_key=True)
    backtest_id = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    equity = Column(Float, nullable=False)
    returns = Column(Float, nullable=True)
    drawdown = Column(Float, nullable=True)
    drawdown_pct = Column(Float, nullable=True)
    peak_equity = Column(Float, nullable=True)
    position = Column(Float, nullable=True)  # Current position size
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_equity_backtest_date', 'backtest_id', 'date'),
    )

    def __repr__(self):
        return f"<BacktestEquity(backtest={self.backtest_id}, date={self.date}, equity={self.equity})>"
