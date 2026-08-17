"""
FRED (Federal Reserve Economic Data) data source for economic and financial data.
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import requests
import csv
import io

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class FREDSource(BaseDataSource):
    """FRED data source for economic and financial data."""
    
    # FRED series mappings
    SERIES_MAPPING = {
        'DXY': 'DTWEXBGS',  # Dollar Index
        'THB': 'DEXTHUS',    # USD/THB Exchange Rate
        'JPY': 'DEXJPUS',    # USD/JPY Exchange Rate
        'CAD': 'DEXCAUS',    # USD/CAD Exchange Rate
        'CHF': 'DEXSZUS',    # USD/CHF Exchange Rate
        'AUD': 'DEXUSAL',    # USD/AUD Exchange Rate
        'NZD': 'DEXUSNZ',    # USD/NZD Exchange Rate
    }
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch data from FRED API.
        
        Args:
            symbol: FRED series symbol or common symbol (DXY, THB, JPY, etc.)
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters
            
        Returns:
            DataSourceResult with fetched data
        """
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
        
        # Normalize symbol and get FRED series ID
        symbol = self.normalize_symbol(symbol)
        fred_series = self._get_fred_series(symbol)
        
        if not fred_series:
            return DataSourceResult(
                success=False,
                error=f"Unknown symbol: {symbol}",
                source=self.config.name
            )
        
        # Build URL
        url = f"{self.base_url}?id={fred_series}"
        
        try:
            self.record_request()
            self.logger.info(f"Fetching {symbol} (FRED: {fred_series}) data from FRED...")
            
            response = requests.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            # Parse CSV data
            formatted_data = self._parse_fred_csv(response.text, symbol)
            
            # Filter by date range if specified
            if start_date or end_date:
                formatted_data = self._filter_by_date_range(formatted_data, start_date, end_date)
            
            return DataSourceResult(
                success=True,
                data=formatted_data,
                metadata={
                    'symbol': symbol,
                    'fred_series': fred_series,
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
        """Validate if symbol is supported by FRED."""
        symbol = self.normalize_symbol(symbol)
        return symbol in self.SERIES_MAPPING or symbol in self.SERIES_MAPPING.values()
    
    def _get_fred_series(self, symbol: str) -> Optional[str]:
        """Get FRED series ID for a symbol."""
        symbol = self.normalize_symbol(symbol)
        return self.SERIES_MAPPING.get(symbol, symbol)
    
    def _parse_fred_csv(self, csv_text: str, symbol: str) -> List[Dict[str, Any]]:
        """Parse FRED CSV response."""
        formatted_data = []
        
        # Parse CSV
        csv_reader = csv.reader(io.StringIO(csv_text))
        
        # Skip header
        try:
            next(csv_reader)
        except StopIteration:
            self.logger.warning(f"Empty CSV response for {symbol}")
            return formatted_data
        
        # Determine data type based on symbol
        is_exchange_rate = symbol in ['THB', 'JPY', 'CAD', 'CHF', 'AUD', 'NZD']
        is_dollar_index = symbol == 'DXY'
        
        for row in csv_reader:
            if len(row) < 2:
                continue
            
            date_str = row[0].strip()
            value_str = row[1].strip()
            
            # Skip empty or invalid values
            if not date_str or not value_str or value_str == '.' or value_str == 'ND':
                continue
            
            try:
                # Parse date (FRED format is YYYY-MM-DD)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                value = float(value_str)
                
                # Format based on data type
                if is_dollar_index:
                    row_data = {
                        'date': date_obj.isoformat(),
                        'value': value,
                        'open_price': None,
                        'high_price': None,
                        'low_price': None,
                        'close_price': value,
                        'volume': None
                    }
                elif is_exchange_rate:
                    # FRED DEX*US series returns quote-currency per 1 USD
                    # (e.g. DEXTHUS is Thai Baht to 1 US Dollar), so use directly.
                    rate = value if value > 0 else value
                    
                    row_data = {
                        'date': date_obj.isoformat(),
                        'base_currency': 'USD',
                        'quote_currency': symbol,
                        'rate': rate,
                        'open_price': None,
                        'high_price': None,
                        'low_price': None,
                        'close_price': rate,
                        'volume': None
                    }
                else:
                    # Generic format
                    row_data = {
                        'date': date_obj.isoformat(),
                        'value': value,
                        'open_price': None,
                        'high_price': None,
                        'low_price': None,
                        'close_price': value,
                        'volume': None
                    }
                
                formatted_data.append(row_data)
                
            except (ValueError, IndexError) as e:
                self.logger.warning(f"Skipping invalid row for {date_str}: {e}")
                continue
        
        # Sort by date
        formatted_data.sort(key=lambda x: x['date'])
        
        return formatted_data
    
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
        """Get list of supported symbols."""
        return list(self.SERIES_MAPPING.keys())
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for database import."""
        # FRED data is already formatted correctly
        return raw_data
