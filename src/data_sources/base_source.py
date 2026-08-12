"""
Base data source classes and interfaces.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from dataclasses import dataclass, field
from enum import Enum
import logging


class DataSourceType(Enum):
    """Types of data sources."""
    EXCHANGE_RATE = "exchange_rate"
    COMMODITY = "commodity"
    DOLLAR_INDEX = "dollar_index"
    CRYPTO = "crypto"


@dataclass
class DataSourceConfig:
    """Configuration for a data source."""
    name: str
    source_type: DataSourceType
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5
    cache_enabled: bool = True
    cache_duration_hours: int = 24
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataSourceResult:
    """Result from a data source operation."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cached: bool = False
    records_count: int = 0


class BaseDataSource(ABC):
    """Abstract base class for all data sources."""
    
    def __init__(self, config: DataSourceConfig):
        """
        Initialize data source with configuration.
        
        Args:
            config: Data source configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._request_count = 0
        self._last_request_time = None
    
    @abstractmethod
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch data from the data source.
        
        Args:
            symbol: Symbol to fetch data for
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters specific to the data source
            
        Returns:
            DataSourceResult with fetched data or error
        """
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol is supported by this data source.
        
        Args:
            symbol: Symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        pass
    
    def check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.
        
        Returns:
            True if within limits, False otherwise
        """
        if not self.config.rate_limit_per_minute and not self.config.rate_limit_per_day:
            return True
        
        now = datetime.utcnow()
        
        # Check per-minute limit
        if self.config.rate_limit_per_minute:
            if self._last_request_time:
                time_since_last = (now - self._last_request_time).total_seconds()
                if time_since_last < 60:  # Within the same minute
                    if self._request_count >= self.config.rate_limit_per_minute:
                        self.logger.warning(f"Rate limit reached: {self._request_count}/{self.config.rate_limit_per_minute} per minute")
                        return False
        
        # Check per-day limit
        if self.config.rate_limit_per_day:
            # This would need persistent storage for proper implementation
            # For now, we'll just log a warning
            if self._request_count >= self.config.rate_limit_per_day:
                self.logger.warning(f"Approaching daily rate limit: {self._request_count}/{self.config.rate_limit_per_day}")
        
        return True
    
    def record_request(self):
        """Record a request for rate limiting."""
        self._request_count += 1
        self._last_request_time = datetime.utcnow()
    
    def get_cache_key(self, symbol: str, start_date: Optional[date], end_date: Optional[date]) -> str:
        """
        Generate a cache key for the request.
        
        Args:
            symbol: Symbol being requested
            start_date: Start date
            end_date: End date
            
        Returns:
            Cache key string
        """
        key_parts = [
            self.config.name,
            symbol,
            start_date.isoformat() if start_date else "none",
            end_date.isoformat() if end_date else "none"
        ]
        return ":".join(key_parts)
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format raw data for database import.
        
        Args:
            raw_data: Raw data from data source
            
        Returns:
            Formatted data ready for import
        """
        # Default implementation - override in subclasses
        return raw_data
    
    def get_supported_symbols(self) -> List[str]:
        """
        Get list of symbols supported by this data source.
        
        Returns:
            List of supported symbols
        """
        # Default implementation - override in subclasses
        return []
    
    def handle_error(self, error: Exception, context: str = "") -> DataSourceResult:
        """
        Handle an error and return error result.
        
        Args:
            error: Exception that occurred
            context: Context information
            
        Returns:
            DataSourceResult with error information
        """
        error_message = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_message, exc_info=True)
        
        return DataSourceResult(
            success=False,
            error=error_message,
            source=self.config.name
        )
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol to standard format.
        
        Args:
            symbol: Symbol to normalize
            
        Returns:
            Normalized symbol
        """
        return symbol.upper().strip()
    
    def validate_date_range(self, start_date: Optional[date], end_date: Optional[date]) -> bool:
        """
        Validate date range parameters.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            True if valid, False otherwise
        """
        if start_date and end_date and start_date > end_date:
            self.logger.error(f"Invalid date range: start_date ({start_date}) after end_date ({end_date})")
            return False
        
        if start_date and start_date > date.today():
            self.logger.warning(f"Start date ({start_date}) is in the future")
        
        return True
