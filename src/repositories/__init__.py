"""
Repository pattern for data access.
"""
from .base_repository import BaseRepository
from .exchange_rate_repository import ExchangeRateRepository
from .commodity_repository import CommodityRepository
from .dollar_index_repository import DollarIndexRepository
from .signal_repository import SignalRepository
from .backtest_repository import BacktestRepository

__all__ = [
    'BaseRepository',
    'ExchangeRateRepository',
    'CommodityRepository',
    'DollarIndexRepository',
    'SignalRepository',
    'BacktestRepository',
]
