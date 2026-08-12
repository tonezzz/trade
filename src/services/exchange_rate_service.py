"""
Service for exchange rate business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.services.base_service import BaseService
from src.queries import PriceQueries, PriceAnalysis
from src.models import ExchangeRate


class ExchangeRateService(BaseService):
    """Service for exchange rate operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.queries = PriceQueries(db)
        self.analysis = PriceAnalysis(db)
    
    def get_exchange_rates(
        self,
        currency: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get exchange rates for a currency.
        
        Args:
            currency: Currency code (e.g., EUR, GBP, JPY)
            start_date: Start date for filtering
            end_date: End date for filtering
            period: Period string (alternative to start/end dates)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dictionary with exchange rate data and metadata
        """
        try:
            # Handle period parameter
            if period:
                start_date, end_date = self.parse_period(period)
            
            # Validate date range
            start_date, end_date = self.validate_date_range(start_date, end_date)
            
            # Get data
            df = self.queries.get_exchange_rates(currency.upper(), start_date, end_date)
            
            if df.empty:
                return {
                    'data': [],
                    'count': 0,
                    'currency': currency.upper(),
                    'error': f"No data found for currency: {currency}"
                }
            
            # Convert to list of dictionaries
            data_list = df.to_dict('records')
            
            # Apply pagination
            paginated_result = self.apply_pagination(data_list, limit, offset)
            
            return {
                **paginated_result,
                'currency': currency.upper()
            }
            
        except Exception as e:
            return self.handle_exception(e, f"Error getting exchange rates for {currency}")
    
    def get_latest_exchange_rate(self, currency: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest exchange rate for a currency.
        
        Args:
            currency: Currency code
            
        Returns:
            Dictionary with latest exchange rate data or None
        """
        try:
            latest = self.queries.get_latest_exchange_rate(currency.upper())
            
            if not latest:
                return None
            
            return {
                'date': latest.date,
                'base_currency': latest.base_currency,
                'quote_currency': latest.quote_currency,
                'rate': latest.rate,
                'open': latest.open_price,
                'high': latest.high_price,
                'low': latest.low_price,
                'close': latest.close_price,
                'volume': latest.volume,
                'source': latest.source
            }
            
        except Exception as e:
            self.log_error(f"Error getting latest exchange rate for {currency}: {e}")
            return None
    
    def calculate_performance(
        self,
        currency: str,
        start_date: date,
        end_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate currency performance over a period.
        
        Args:
            currency: Currency code
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with performance metrics or None
        """
        try:
            performance = self.analysis.calculate_currency_performance(
                currency.upper(),
                start_date,
                end_date
            )
            
            if not performance:
                return None
            
            return performance
            
        except Exception as e:
            self.log_error(f"Error calculating performance for {currency}: {e}")
            return None
    
    def get_available_currencies(self) -> List[str]:
        """
        Get list of available currencies.
        
        Returns:
            List of currency codes
        """
        try:
            return self.analysis.get_available_currencies()
        except Exception as e:
            self.log_error(f"Error getting available currencies: {e}")
            return []
    
    def get_currency_summary(self, currency: str) -> Dict[str, Any]:
        """
        Get summary information for a currency.
        
        Args:
            currency: Currency code
            
        Returns:
            Dictionary with currency summary
        """
        try:
            latest = self.get_latest_exchange_rate(currency)
            if not latest:
                return {'error': f'No data found for currency: {currency}'}
            
            # Get basic statistics
            df = self.queries.get_exchange_rates(currency.upper())
            
            if df.empty:
                return {'error': f'No historical data found for currency: {currency}'}
            
            return {
                'currency': currency.upper(),
                'latest': latest,
                'data_points': len(df),
                'date_range': {
                    'start': df['date'].min(),
                    'end': df['date'].max()
                },
                'price_range': {
                    'high': df['high'].max() if 'high' in df.columns else df['rate'].max(),
                    'low': df['low'].min() if 'low' in df.columns else df['rate'].min(),
                    'average': df['rate'].mean()
                }
            }
            
        except Exception as e:
            return self.handle_exception(e, f"Error getting summary for {currency}")
