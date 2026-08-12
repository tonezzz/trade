"""
Repository for exchange rate data access.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.repositories.base_repository import BaseRepository
from src.models import ExchangeRate


class ExchangeRateRepository(BaseRepository):
    """Repository for exchange rate data access."""
    
    def __init__(self, db: Session):
        super().__init__(db, ExchangeRate)
    
    def get_by_currency(
        self,
        quote_currency: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ExchangeRate]:
        """
        Get exchange rates for a specific currency.
        
        Args:
            quote_currency: Currency code (e.g., EUR, GBP, JPY)
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of exchange rate records
        """
        return self.get_by_date_range(
            date_field='date',
            start_date=start_date,
            end_date=end_date
        )
    
    def get_latest_by_currency(self, quote_currency: str) -> Optional[ExchangeRate]:
        """
        Get the latest exchange rate for a currency.
        
        Args:
            quote_currency: Currency code
            
        Returns:
            Latest exchange rate record or None
        """
        try:
            return self.db.query(self.model).filter(
                self.model.quote_currency == quote_currency.upper()
            ).order_by(self.model.date.desc()).first()
        except Exception as e:
            self.log_error(f"Error getting latest exchange rate for {quote_currency}: {e}")
            return None
    
    def get_available_currencies(self) -> List[str]:
        """
        Get list of available currencies.
        
        Returns:
            List of currency codes
        """
        try:
            currencies = self.db.query(self.model.quote_currency).distinct().all()
            return [currency[0] for currency in currencies]
        except Exception as e:
            self.log_error(f"Error getting available currencies: {e}")
            return []
    
    def get_date_range_for_currency(self, quote_currency: str) -> Optional[tuple[date, date]]:
        """
        Get the date range for a specific currency.
        
        Args:
            quote_currency: Currency code
            
        Returns:
            Tuple of (start_date, end_date) or None
        """
        try:
            result = self.db.query(
                func.min(self.model.date),
                func.max(self.model.date)
            ).filter(
                self.model.quote_currency == quote_currency.upper()
            ).first()
            
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None
        except Exception as e:
            self.log_error(f"Error getting date range for {quote_currency}: {e}")
            return None
