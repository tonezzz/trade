"""
ECB (European Central Bank) data source for exchange rates.
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import requests
import xml.etree.ElementTree as ET

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class ECBSource(BaseDataSource):
    """ECB data source for European exchange rates."""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch exchange rate data from ECB.
        
        Args:
            symbol: Currency code (EUR is base, so quote currency like USD, GBP, etc.)
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters
            
        Returns:
            DataSourceResult with exchange rate data
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
        
        # Normalize symbol
        symbol = self.normalize_symbol(symbol)
        
        if not self.validate_symbol(symbol):
            return DataSourceResult(
                success=False,
                error=f"Unsupported currency: {symbol}",
                source=self.config.name
            )
        
        try:
            self.record_request()
            self.logger.info(f"Fetching {symbol} exchange rate data from ECB...")
            
            response = requests.get(self.base_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            # Parse XML data
            formatted_data = self._parse_ecb_xml(response.text, symbol)
            
            # Filter by date range if specified
            if start_date or end_date:
                formatted_data = self._filter_by_date_range(formatted_data, start_date, end_date)
            
            return DataSourceResult(
                success=True,
                data=formatted_data,
                metadata={
                    'symbol': symbol,
                    'base_currency': 'EUR',
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
        """Validate if currency is supported by ECB."""
        # ECB supports major currencies, but we'll be permissive
        # and let the API return an error if unsupported
        symbol = self.normalize_symbol(symbol)
        return len(symbol) == 3 and symbol.isalpha()
    
    def _parse_ecb_xml(self, xml_text: str, symbol: str) -> List[Dict[str, Any]]:
        """Parse ECB XML response."""
        formatted_data = []
        
        try:
            root = ET.fromstring(xml_text)
            
            # ECB namespace
            ns = {'gesmes': 'http://www.ecb.int/vocabulary/2002-08-01/ecb-int/vocabulary'}
            
            # Find the Cube with time and Cube with currency
            for time_cube in root.findall('.//{*}Cube[@time]', namespaces=ns):
                time_str = time_cube.get('time')
                
                if not time_str:
                    continue
                
                try:
                    date_obj = datetime.strptime(time_str, '%Y-%m-%d').date()
                except ValueError:
                    continue
                
                # Find the specific currency
                for currency_cube in time_cube.findall('.//{*}Cube', namespaces=ns):
                    if currency_cube.get('currency') == symbol:
                        rate = float(currency_cube.get('rate'))
                        
                        # ECB provides EUR/base, we need to convert to USD/base if needed
                        # For now, we'll store as EUR/base
                        row_data = {
                            'date': date_obj.isoformat(),
                            'base_currency': 'EUR',
                            'quote_currency': symbol,
                            'rate': rate,
                            'open_price': None,
                            'high_price': None,
                            'low_price': None,
                            'close_price': rate,
                            'volume': None
                        }
                        
                        formatted_data.append(row_data)
            
            # Sort by date
            formatted_data.sort(key=lambda x: x['date'])
            
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse ECB XML: {e}")
        
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
        """Get list of commonly supported currencies."""
        # ECB supports many currencies, here are common ones
        return ['USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NOK', 'SEK', 'DKK', 'PLN', 'HUF', 'CZK']
    
    def format_data_for_import(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format data for database import."""
        # ECB data is already formatted correctly
        return raw_data
