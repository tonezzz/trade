"""
Pydantic schemas for trading signal endpoints.
"""
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SignalResponse(BaseModel):
    """Trading signal response."""
    signal_type: str
    strength: str
    confidence: float
    timestamp: str
    price: float
    indicators: Dict[str, Any]
    reasons: List[str]
    timeframe: str
    validation: Optional[Dict[str, Any]] = None


class SignalHistoryResponse(BaseModel):
    """Signal history response."""
    id: int
    asset_type: str
    asset_symbol: str
    signal_type: str
    strength: str
    confidence: float
    timestamp: str
    price: float
    indicators: Dict[str, Any]
    reasons: List[str]
    timeframe: Optional[str] = None


class SignalPerformanceResponse(BaseModel):
    """Signal performance metrics response."""
    asset_type: str
    asset_symbol: str
    timeframe: str
    test_start_date: date
    test_end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    profit_factor: Optional[float] = None
    sharpe_ratio: Optional[float] = None
