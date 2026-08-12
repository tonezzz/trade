"""
Service for commodity price business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.services.base_service import BaseService
from src.queries import PriceQueries, PriceAnalysis
from src.models import CommodityPrice


class CommodityService(BaseService):
    """Service for commodity price operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.queries = PriceQueries(db)
        self.analysis = PriceAnalysis(db)
    
    def get_commodity_prices(
        self,
        commodity: Optional[str] = None,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get commodity prices.
        
        Args:
            commodity: Commodity name (e.g., GOLD, OIL)
            symbol: Trading symbol (e.g., XAUUSD, USOIL)
            start_date: Start date for filtering
            end_date: End date for filtering
            period: Period string (alternative to start/end dates)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dictionary with commodity price data and metadata
        """
        try:
            # Handle period parameter
            if period:
                start_date, end_date = self.parse_period(period)
            
            # Validate date range
            start_date, end_date = self.validate_date_range(start_date, end_date)
            
            # Get data
            df = self.queries.get_commodity_prices(commodity, symbol, start_date, end_date)
            
            if df.empty:
                return {
                    'data': [],
                    'count': 0,
                    'commodity': commodity,
                    'symbol': symbol,
                    'error': "No data found for the specified criteria"
                }
            
            # Convert to list of dictionaries
            data_list = df.to_dict('records')
            
            # Apply pagination
            paginated_result = self.apply_pagination(data_list, limit, offset)
            
            return {
                **paginated_result,
                'commodity': commodity.upper() if commodity else None,
                'symbol': symbol.upper() if symbol else None
            }
            
        except Exception as e:
            return self.handle_exception(e, "Error getting commodity prices")
    
    def get_latest_commodity_price(
        self,
        commodity: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest commodity price.
        
        Args:
            commodity: Commodity name
            symbol: Trading symbol
            
        Returns:
            Dictionary with latest commodity price data or None
        """
        try:
            if not commodity and not symbol:
                return None
            
            latest = self.queries.get_latest_commodity_price(commodity, symbol)
            
            if not latest:
                return None
            
            return {
                'date': latest.date,
                'commodity': latest.commodity,
                'symbol': latest.symbol,
                'price': latest.price,
                'unit': latest.unit,
                'open': latest.open_price,
                'high': latest.high_price,
                'low': latest.low_price,
                'close': latest.close_price,
                'volume': latest.volume,
                'source': latest.source
            }
            
        except Exception as e:
            self.log_error(f"Error getting latest commodity price: {e}")
            return None
    
    def get_available_commodities(self) -> List[str]:
        """
        Get list of available commodities.
        
        Returns:
            List of commodity names
        """
        try:
            return self.analysis.get_available_commodities()
        except Exception as e:
            self.log_error(f"Error getting available commodities: {e}")
            return []
    
    def get_commodity_summary(
        self,
        commodity: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary information for a commodity.
        
        Args:
            commodity: Commodity name
            symbol: Trading symbol
            
        Returns:
            Dictionary with commodity summary
        """
        try:
            if not commodity and not symbol:
                return {'error': 'Either commodity or symbol must be specified'}
            
            latest = self.get_latest_commodity_price(commodity, symbol)
            if not latest:
                return {'error': 'No data found for the specified commodity'}
            
            # Get basic statistics
            df = self.queries.get_commodity_prices(commodity, symbol)
            
            if df.empty:
                return {'error': 'No historical data found for the specified commodity'}
            
            return {
                'commodity': latest.get('commodity'),
                'symbol': latest.get('symbol'),
                'latest': latest,
                'data_points': len(df),
                'date_range': {
                    'start': df['date'].min(),
                    'end': df['date'].max()
                },
                'price_range': {
                    'high': df['high'].max() if 'high' in df.columns else df['price'].max(),
                    'low': df['low'].min() if 'low' in df.columns else df['price'].min(),
                    'average': df['price'].mean()
                }
            }
            
        except Exception as e:
            return self.handle_exception(e, "Error getting commodity summary")
