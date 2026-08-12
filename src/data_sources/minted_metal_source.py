"""
Minted Metal data source for precious metals (Gold, Silver, etc.).
Free API with no API key required - https://mintedmetal.com/api/prices.json
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import requests
import json

from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceResult, DataSourceType


class MintedMetalSource(BaseDataSource):
    """Minted Metal data source for precious metals."""
    
    # Minted Metal API endpoint
    API_URL = "https://mintedmetal.com/api/prices.json"
    
    # Metal name mapping
    METAL_MAPPING = {
        'GOLD': 'gold',
        'SILVER': 'silver',
        'PLATINUM': 'platinum',
        'PALLADIUM': 'palladium',
        'RHODIUM': 'rhodium',
        'XAU': 'gold',
        'XAG': 'silver',
        'XPT': 'platinum',
        'XPD': 'palladium'
    }
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = self.API_URL
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Fetch precious metals data from Minted Metal API.
        
        Args:
            symbol: Metal symbol (GOLD, SILVER, XAU, XAG, etc.)
            start_date: Start date for data range (not supported for latest)
            end_date: End date for data range (not supported for latest)
            **kwargs: Additional parameters
            
        Returns:
            DataSourceResult with metals data
        """
        # Minted Metal doesn't require API key
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
            self.logger.info(f"Fetching {symbol} data from Minted Metal API...")
            
            # Fetch latest prices
            response = requests.get(self.base_url, timeout=self.config.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and format data
            formatted_data = self._parse_minted_metal_response(data, symbol)
            
            return DataSourceResult(
                success=True,
                data=formatted_data,
                metadata={
                    'symbol': symbol,
                    'source': 'Minted Metal',
                    'attribution': 'Data from mintedmetal.com (CC BY 4.0)',
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
        return symbol in self.METAL_MAPPING.values()
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol to Minted Metal API format.
        
        Args:
            symbol: Symbol to normalize
            
        Returns:
            Normalized symbol in Minted Metal format
        """
        symbol = symbol.upper().strip()
        return self.METAL_MAPPING.get(symbol, symbol.lower())
    
    def _parse_minted_metal_response(self, data: Dict[str, Any], symbol: str) -> List[Dict[str, Any]]:
        """Parse Minted Metal API response."""
        formatted_data = []
        
        # Get metals data
        metals = data.get('metals', {})
        
        # Get the specific metal data
        metal_data = metals.get(symbol)
        
        if not metal_data:
            self.logger.warning(f"No data found for {symbol} in Minted Metal response")
            return formatted_data
        
        try:
            # Get current date
            today = date.today()
            
            # Extract price data
            price = metal_data.get('price')
            currency = metal_data.get('currency', 'USD')
            unit = metal_data.get('unit', 'troy ounce')
            
            # Normalize unit for database
            unit_mapping = {
                'troy ounce': 'oz',
                'troy oz': 'oz',
                'ounce': 'oz',
                'gram': 'gram',
                'kilogram': 'kg'
            }
            unit = unit_mapping.get(unit, unit[:20])  # Truncate to 20 chars if not in mapping
            
            # Determine commodity name
            commodity_mapping = {
                'gold': 'GOLD',
                'silver': 'SILVER',
                'platinum': 'PLATINUM',
                'palladium': 'PALLADIUM',
                'rhodium': 'RHODIUM'
            }
            commodity = commodity_mapping.get(symbol, symbol.upper())
            
            # Create single data point for latest price
            row_data = {
                'date': today.isoformat(),
                'commodity': commodity,
                'symbol': symbol.upper(),
                'price': float(price),
                'unit': unit,
                'open_price': None,
                'high_price': None,
                'low_price': None,
                'close_price': float(price),
                'volume': None
            }
            
            formatted_data.append(row_data)
            
        except (ValueError, KeyError) as e:
            self.logger.warning(f"Error parsing Minted Metal data for {symbol}: {e}")
        
        return formatted_data