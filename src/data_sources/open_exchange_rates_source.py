"""
Open Exchange Rates data source for live exchange rates.
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import requests
import json

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class OpenExchangeRatesSource(BaseDataSource):
    """Open Exchange Rates data source for live exchange rates."""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://open.er-api.com/v6/latest"
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch live exchange rate data from Open Exchange Rates.
        
        Args:
            symbol: Currency code (THB, EUR, GBP, etc.) - base is USD
            start_date: Start date for data range (not supported for latest)
            end_date: End date for data range (not supported for latest)
            **kwargs: Additional parameters (base currency, etc.)
            
        Returns:
            DataSourceResult with exchange rate data
        """
        if not self.check_rate_limit():
            return DataSourceResult(
                success=False,
                error="Rate limit exceeded",
                source=self.config.name
            )
        
        # Normalize symbol
        symbol = self.normalize_symbol(symbol)
        
        # Determine base currency (default USD)
        base_currency = kwargs.get('base_currency', 'USD')
        
        try:
            self.record_request()
            self.logger.info(f"Fetching {symbol} exchange rate from Open Exchange Rates...")
            
            # Build URL
            url = f"{self.base_url}/{base_currency}"
            
            response = requests.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                return DataSourceResult(
                    success=False,
                    error=data.get('error', 'Unknown API error'),
                    source=self.config.name
                )
            
            # Parse and format data
            formatted_data = self._parse_open_exchange_rates_response(data, symbol, base_currency)
            
            return DataSourceResult(
                success=True,
                data=formatted_data,
                metadata={
                    'symbol': symbol,
                    'base_currency': base_currency,
                    'records_count': len(formatted_data)
                },
                source=self.config.name,
                records_count=len(formatted_data)
            )
            
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, f"HTTP request failed for {symbol}")
        except Exception as e:
            return self.handle_error(e, f"Failed to fetch {symbol} data")
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if currency code is supported."""
        symbol = self.normalize_symbol(symbol)
        return len(symbol) == 3 and symbol.isalpha()
    
    def _parse_open_exchange_rates_response(self, data: Dict[str, Any], symbol: str, base_currency: str) -> List[Dict[str, Any]]:
        """Parse Open Exchange Rates API response."""
        formatted_data = []
        
        # Open Exchange Rates returns rates in format: {"rates": {"THB": 33.5, "EUR": 0.85}}
        rates = data.get('rates', {})
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get the specific currency rate
        rate = rates.get(symbol)
        
        if not rate:
            self.logger.warning(f"No rate found for {symbol} in response")
            return formatted_data
        
        try:
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date_obj = date.today()
        
        # Create single data point for latest rate
        row_data = {
            'date': date_obj.isoformat(),
            'base_currency': base_currency,
            'quote_currency': symbol,
            'rate': rate,
            'open_price': None,
            'high_price': None,
            'low_price': None,
            'close_price': rate,
            'volume': None
        }
        
        formatted_data.append(row_data)
        
        return formatted_data
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of commonly supported currencies."""
        # Open Exchange Rates supports many currencies
        return ['THB', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'SGD', 'HKD', 'MXN', 'TRY', 'ZAR']
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for database import."""
        # Open Exchange Rates data is already formatted correctly
        return raw_data
