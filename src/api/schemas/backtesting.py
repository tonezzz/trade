"""
Pydantic schemas for backtesting endpoints.
"""
from datetime import date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    """Backtest request model."""
    asset_type: str
    asset_symbol: str
    start_date: date
    end_date: date
    initial_capital: float = 10000.0
    commission: float = 0.001
    timeframe: str = "1d"


class BacktestResponse(BaseModel):
    """Backtest response model."""
    backtest_id: str
    strategy_name: str
    symbol: str
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    largest_win: Optional[float] = None
    largest_loss: Optional[float] = None
    avg_trade_duration: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    equity_curve: List[Dict[str, Any]] = []
    trades: List[Dict[str, Any]] = []


class StrategiesResponse(BaseModel):
    """Available strategies response model."""
    strategies: List[str]
    count: int


class OptimizeRequest(BaseModel):
    """Optimization request model."""
    asset_type: str
    asset_symbol: str
    start_date: date
    end_date: date
    initial_capital: float = 10000.0
    commission: float = 0.001
    timeframe: str = "1d"
    parameters: Dict[str, Any] = {}


class CompareRequest(BaseModel):
    """Strategy comparison request model."""
    asset_type: str
    asset_symbol: str
    start_date: date
    end_date: date
    initial_capital: float = 10000.0
    commission: float = 0.001
    strategies: List[str] = []


class OptimizeResponse(BaseModel):
    """Optimization response model."""
    best_parameters: Dict[str, Any]
    best_sharpe: float
    all_results: List[Dict[str, Any]]
