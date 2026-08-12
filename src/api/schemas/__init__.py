"""
Pydantic schemas for API request/response models.
"""
from .exchange_rates import (
    ExchangeRateResponse,
    ExchangeRateListResponse,
    CurrencyPerformanceResponse
)
from .commodities import (
    CommodityPriceResponse,
    CommodityPriceListResponse
)
from .dollar_index import (
    DollarIndexResponse,
    DollarIndexPerformanceResponse
)
from .signals import (
    SignalResponse,
    SignalHistoryResponse,
    SignalPerformanceResponse
)
from .backtesting import (
    BacktestRequest,
    BacktestResponse,
    OptimizeRequest,
    OptimizeResponse,
    CompareRequest,
    StrategiesResponse
)
from .common import (
    ErrorResponse,
    SuccessResponse,
    PaginatedResponse,
    HealthResponse,
    DataQualityResponse,
    AvailableItemsResponse
)

__all__ = [
    # Common schemas
    'ErrorResponse',
    'SuccessResponse',
    'PaginatedResponse',
    'HealthResponse',
    'DataQualityResponse',
    'AvailableItemsResponse',
    # Exchange rate schemas
    'ExchangeRateResponse',
    'ExchangeRateListResponse',
    'CurrencyPerformanceResponse',
    # Commodity schemas
    'CommodityPriceResponse',
    'CommodityPriceListResponse',
    # Dollar index schemas
    'DollarIndexResponse',
    'DollarIndexPerformanceResponse',
    # Signal schemas
    'SignalResponse',
    'SignalHistoryResponse',
    'SignalPerformanceResponse',
    # Backtesting schemas
    'BacktestRequest',
    'BacktestResponse',
    'OptimizeRequest',
    'OptimizeResponse',
    'CompareRequest',
    'StrategiesResponse',
]
