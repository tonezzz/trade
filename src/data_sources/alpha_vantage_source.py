"""
Alpha Vantage data source for commodities and financial data.
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
import requests
import json

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class AlphaVantageSource(BaseDataSource):
    """Alpha Vantage data source for commodities and financial data."""
    
    # Alpha Vantage function mappings
    FUNCTION_MAPPING = {
        'WTI': 'WTI',
        'BRENT': 'BRENT',
        'WHEAT': 'WHEAT',
        'CORN': 'CORN',
        'COPPER': 'COPPER',
        'NATURAL_GAS': 'NATURAL_GAS'
    }
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch commodity data from Alpha Vantage.
        
        Args:
            symbol: Commodity symbol (WTI, BRENT, WHEAT, CORN, COPPER, NATURAL_GAS)
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters (function, interval, etc.)
            
        Returns:
            DataSourceResult with commodity data
        """
        if not self.config.api_key:
            return self.handle_error(ValueError("API key not configured"), "Alpha Vantage API key required")
        
        if not self.check_rate_limit():
            return DataSourceResult(
                success=False,
                error="Rate limit exceeded",
                source=self.config.name
            )
        
        # Validate date range
        if not self.validate_date_range(start_date, end_date):
            return DataSourceResult(
                success=False,
                error="Invalid date range",
                source=self.config.name
            )
        
        # Normalize symbol
        symbol = self.normalize_symbol(symbol)
        
        # Get Alpha Vantage function
        function = kwargs.get('function', self._get_function_for_symbol(symbol))
        if not function:
            return DataSourceResult(
                success=False,
                error=f"Unknown symbol: {symbol}",
                source=self.config.name
            )
        
        # Build request parameters
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': self.config.api_key,
            'outputsize': 'full'
        }
        
        # Add optional parameters
        if 'interval' in kwargs:
            params['interval'] = kwargs['interval']
        
        try:
            self.record_request()
            self.logger.info(f"Fetching {symbol} data from Alpha Vantage...")
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                return DataSourceResult(
                    success=False,
                    error=data['Error Message'],
                    source=self.config.name
                )
            
            # Parse and format data
            formatted_data = self._parse_alpha_vantage_response(data, symbol)
            
            # Filter by date range if specified
            if start_date or end_date:
                formatted_data = self._filter_by_date_range(formatted_data, start_date, end_date)
            
            return DataSourceResult(
                success=True,
                data=formatted_data,
                metadata={
                    'symbol': symbol,
                    'function': function,
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
        """Validate if symbol is supported by Alpha Vantage."""
        symbol = self.normalize_symbol(symbol)
        return symbol in self.FUNCTION_MAPPING or symbol in ['WTI', 'BRENT', 'WHEAT', 'CORN', 'COPPER', 'NATURAL_GAS']
    
    def _get_function_for_symbol(self, symbol: str) -> Optional[str]:
        """Get Alpha Vantage function for a symbol."""
        symbol = self.normalize_symbol(symbol)
        return self.FUNCTION_MAPPING.get(symbol)
    
    def _parse_alpha_vantage_response(self, data: Dict[str, Any], symbol: str) -> List[Dict[str, Any]]:
        """Parse Alpha Vantage API response."""
        formatted_data = []
        
        # Alpha Vantage returns commodity data in a different format than stock data
        # Check for commodity format (has 'data' key)
        if 'data' in data:
            return self._parse_commodity_response(data, symbol)
        
        # Check for time series format (stock-style data)
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key or 'Time Series' in str(key):
                time_series_key = key
                break
        
        if not time_series_key:
            self.logger.warning(f"No time series data found in response for {symbol}")
            return formatted_data
        
        time_series = data.get(time_series_key, {})
        
        # Determine unit based on symbol
        unit_mapping = {
            'WTI': 'barrel',
            'BRENT': 'barrel',
            'WHEAT': 'bushel',
            'CORN': 'bushel',
            'COPPER': 'lb',
            'NATURAL_GAS': 'mmbtu'
        }
        unit = unit_mapping.get(symbol, 'unknown')
        
        for date_str, values in time_series.items():
            try:
                # Parse date (Alpha Vantage format: YYYY-MM-DD)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Extract OHLCV data
                row = {
                    'date': date_obj.isoformat(),
                    'commodity': self._get_commodity_name(symbol),
                    'symbol': symbol,
                    'price': float(values.get('4. close', values.get('close', 0))),
                    'unit': unit,
                    'open_price': float(values.get('1. open', values.get('open', 0))) if values.get('1. open') else None,
                    'high_price': float(values.get('2. high', values.get('high', 0))) if values.get('2. high') else None,
                    'low_price': float(values.get('3. low', values.get('low', 0))) if values.get('3. low') else None,
                    'close_price': float(values.get('4. close', values.get('close', 0))),
                    'volume': float(values.get('5. volume', values.get('volume', 0))) if values.get('5. volume') else None
                }
                
                formatted_data.append(row)
                
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Skipping invalid data point for {date_str}: {e}")
                continue
        
        # Sort by date
        formatted_data.sort(key=lambda x: x['date'])
        
        return formatted_data
    
    def _parse_commodity_response(self, data: Dict[str, Any], symbol: str) -> List[Dict[str, Any]]:
        """Parse Alpha Vantage commodity response format."""
        formatted_data = []
        
        # Get unit from response and shorten it to fit database constraints
        unit = data.get('unit', 'unknown')
        unit_mapping = {
            'dollar per metric ton': 'USD/ton',
            'dollars per metric ton': 'USD/ton',
            'dollar per bushel': 'USD/bushel',
            'dollars per bushel': 'USD/bushel',
            'dollar per barrel': 'USD/barrel',
            'dollars per barrel': 'USD/barrel',
            'dollar per mmbtu': 'USD/mmbtu',
            'dollars per mmbtu': 'USD/mmbtu',
            'dollars per million BTU': 'USD/mmbtu',
            'dollars per million': 'USD/mmbtu'
        }
        unit = unit_mapping.get(unit, unit[:20])  # Truncate to 20 chars if not in mapping
        
        # Parse data array
        commodity_data = data.get('data', [])
        
        for item in commodity_data:
            try:
                # Parse date
                date_str = item.get('date')
                if not date_str:
                    continue
                    
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Extract value
                value_str = item.get('value')
                if not value_str:
                    continue
                    
                price = float(value_str)
                
                row = {
                    'date': date_obj.isoformat(),
                    'commodity': self._get_commodity_name(symbol),
                    'symbol': symbol,
                    'price': price,
                    'unit': unit,
                    'open_price': None,
                    'high_price': None,
                    'low_price': None,
                    'close_price': price,
                    'volume': None
                }
                
                formatted_data.append(row)
                
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Skipping invalid commodity data point: {e}")
                continue
        
        # Sort by date
        formatted_data.sort(key=lambda x: x['date'])
        
        return formatted_data
    
    def _get_commodity_name(self, symbol: str) -> str:
        """Get commodity name from symbol."""
        commodity_mapping = {
            'WTI': 'OIL',
            'BRENT': 'OIL',
            'WHEAT': 'WHEAT',
            'CORN': 'CORN',
            'COPPER': 'COPPER',
            'NATURAL_GAS': 'NATURAL_GAS'
        }
        return commodity_mapping.get(symbol, symbol)
    
    def _filter_by_date_range(
        self,
        data: List[Dict[str, Any]],
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        """Filter data by date range."""
        if not start_date and not end_date:
            return data
        
        filtered_data = []
        for row in data:
            row_date = datetime.fromisoformat(row['date']).date()
            
            if start_date and row_date < start_date:
                continue
            if end_date and row_date > end_date:
                continue
            
            filtered_data.append(row)
        
        return filtered_data
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported commodity symbols."""
        return list(self.FUNCTION_MAPPING.keys())
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for database import."""
        # Alpha Vantage data is already formatted correctly
        return raw_data
