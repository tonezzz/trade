"""
Metal Prices data source for precious metals (Gold, Silver, etc.).
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import requests
import json

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class MetalPricesSource(BaseDataSource):
    """Metal Prices data source for precious metals."""
    
    # Metal Prices API endpoints
    API_ENDPOINTS = {
        'XAU': 'https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=XAU&currencies=USD',
        'XAG': 'https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=XAG&currencies=USD',
    }
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://api.metalpriceapi.com/v1"
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch precious metals data from Metal Prices API.
        
        Args:
            symbol: Metal symbol (XAU for Gold, XAG for Silver)
            start_date: Start date for data range (not supported for latest)
            end_date: End date for data range (not supported for latest)
            **kwargs: Additional parameters
            
        Returns:
            DataSourceResult with metals data
        """
        if not self.config.api_key:
            return self.handle_error(ValueError("API key not configured"), "Metal Prices API key required")
        
        if not self.check_rate_limit():
            return DataSourceResult(
                success=False,
                error="Rate limit exceeded",
                source=self.config.name
            )
        
        # Normalize symbol
        symbol = self.normalize_symbol(symbol)
        
        if not self.validate_symbol(symbol):
            return DataSourceResult(
                success=False,
                error=f"Unsupported metal symbol: {symbol}",
                source=self.config.name
            )
        
        try:
            self.record_request()
            self.logger.info(f"Fetching {symbol} data from Metal Prices API...")
            
            # Build URL for latest price
            url = f"{self.base_url}/latest"
            params = {
                'api_key': self.config.api_key,
                'base': symbol,
                'currencies': 'USD'
            }
            
            response = requests.get(url, params=params, timeout=self.config.timeout)
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
            formatted_data = self._parse_metal_prices_response(data, symbol)
            
            return DataSourceResult(
                success=True,
                data=formatted_data,
                metadata={
                    'symbol': symbol,
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
        """Validate if metal symbol is supported."""
        symbol = self.normalize_symbol(symbol)
        # Accept both common names and API symbols
        return symbol in ['XAU', 'XAG', 'XPT', 'XPD', 'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM']
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol to standard format.
        
        Args:
            symbol: Symbol to normalize
            
        Returns:
            Normalized symbol in API format
        """
        symbol = symbol.upper().strip()
        # Map common names to API symbols
        symbol_mapping = {
            'GOLD': 'XAU',
            'SILVER': 'XAG',
            'PLATINUM': 'XPT',
            'PALLADIUM': 'XPD'
        }
        return symbol_mapping.get(symbol, symbol)
    
    def _parse_metal_prices_response(self, data: Dict[str, Any], symbol: str) -> List[Dict[str, Any]]:
        """Parse Metal Prices API response."""
        formatted_data = []
        
        # Metal Prices API returns rates in format: {"rates": {"USD": 1850.50}}
        rates = data.get('rates', {})
        usd_rate = rates.get('USD')
        
        if not usd_rate:
            self.logger.warning(f"No USD rate found in response for {symbol}")
            return formatted_data
        
        # Get current date
        today = date.today()
        
        # Determine commodity name
        commodity_mapping = {
            'XAU': 'GOLD',
            'XAG': 'SILVER',
            'XPT': 'PLATINUM',
            'XPD': 'PALLADIUM',
            'GOLD': 'GOLD',
            'SILVER': 'SILVER',
            'PLATINUM': 'PLATINUM',
            'PALLADIUM': 'PALLADIUM'
        }
        commodity = commodity_mapping.get(symbol, symbol)
        
        # Create single data point for latest price
        row_data = {
            'date': today.isoformat(),
            'commodity': commodity,
            'symbol': f"{symbol}USD",
            'price': usd_rate,
            'unit': 'oz',
            'open_price': None,
            'high_price': None,
            'low_price': None,
            'close_price': usd_rate,
            'volume': None
        }
        
        formatted_data.append(row_data)
        
        return formatted_data
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported metal symbols."""
        return ['XAU', 'XAG', 'XPT', 'XPD']
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for database import."""
        # Metal Prices data is already formatted correctly
        return raw_data
