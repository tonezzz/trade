"""
Data source module for unified data access.
"""
from .base_source import BaseDataSource, DataSourceConfig, DataSourceResult
from .registry import DataSourceRegistry
from .alpha_vantage_source import AlphaVantageSource
from .fred_source import FREDSource
from .ecb_source import ECBSource
from .metal_prices_source import MetalPricesSource
from .minted_metal_source import MintedMetalSource
from .open_exchange_rates_source import OpenExchangeRatesSource
from .frankfurter_source import FrankfurterSource
from .downloader import UnifiedDataDownloader

__all__ = [
    'BaseDataSource',
    'DataSourceConfig',
    'DataSourceResult',
    'DataSourceRegistry',
    'AlphaVantageSource',
    'FREDSource',
    'ECBSource',
    'MetalPricesSource',
    'MintedMetalSource',
    'OpenExchangeRatesSource',
    'FrankfurterSource',
    'UnifiedDataDownloader',
]
