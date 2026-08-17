"""
Frankfurter (ECB reference rates) data source for live exchange rates.
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import requests
import json

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class FrankfurterSource(BaseDataSource):
    """Frankfurter ECB reference rate data source for live exchange rates."""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.frankfurter.app/v1"
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch latest exchange rate from Frankfurter.
        
        Args:
            symbol: Quote currency code (THB, EUR, GBP, etc.)
            start_date: Not supported for latest endpoint
            end_date: Not supported for latest endpoint
            **kwargs: Additional parameters (base_currency)
        
        Returns:
            DataSourceResult with a single rate record
        """
        if not self.check_rate_limit():
            return DataSourceResult(
                success=False,
                error="Rate limit exceeded",
                source=self.config.name
            )
        
        symbol = self.normalize_symbol(symbol)
        base_currency = kwargs.get('base_currency', 'USD')
        
        try:
            self.record_request()
            self.logger.info(f"Fetching {symbol} exchange rate from Frankfurter...")
            
            url = f"{self.base_url}/latest?from={base_currency}&to={symbol}"
            response = requests.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            formatted_data = self._parse_frankfurter_response(data, symbol, base_currency)
            
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
    
    def _parse_frankfurter_response(
        self,
        data: Dict[str, Any],
        symbol: str,
        base_currency: str
    ) -> List[Dict[str, Any]]:
        """Parse Frankfurter latest response."""
        formatted_data = []
        
        rates = data.get('rates', {})
        rate = rates.get(symbol)
        if rate is None:
            self.logger.warning(f"No rate found for {symbol} in Frankfurter response")
            return formatted_data
        
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date_obj = date.today()
        
        formatted_data.append({
            'date': date_obj.isoformat(),
            'base_currency': base_currency,
            'quote_currency': symbol,
            'rate': float(rate),
            'open_price': None,
            'high_price': None,
            'low_price': None,
            'close_price': float(rate),
            'volume': None
        })
        
        return formatted_data
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for database import."""
        return raw_data
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of commonly supported currencies."""
        return ['THB', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'SGD', 'HKD', 'MXN', 'TRY', 'ZAR']
