"""
Repository for Dollar Index data access.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.repositories.base_repository import BaseRepository
from src.models import DollarIndex


class DollarIndexRepository(BaseRepository):
    """Repository for Dollar Index data access."""
    
    def __init__(self, db: Session):
        super().__init__(db, DollarIndex)
    
    def get_by_date_range(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DollarIndex]:
        """
        Get Dollar Index data within a date range.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of Dollar Index records
        """
        return super().get_by_date_range('date', start_date, end_date)
    
    def get_latest(self) -> Optional[DollarIndex]:
        """
        Get the latest Dollar Index value.
        
        Returns:
            Latest Dollar Index record or None
        """
        return super().get_latest('date')
    
    def get_date_range(self) -> Optional[tuple[date, date]]:
        """
        Get the overall date range for Dollar Index data.
        
        Returns:
            Tuple of (start_date, end_date) or None
        """
        try:
            result = self.db.query(
                func.min(self.model.date),
                func.max(self.model.date)
            ).first()
            
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None
        except Exception as e:
            self.log_error(f"Error getting Dollar Index date range: {e}")
            return None
    
    def get_by_value_range(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[DollarIndex]:
        """
        Get Dollar Index data within a value range.
        
        Args:
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)
            
        Returns:
            List of Dollar Index records
        """
        try:
            query = self.db.query(self.model)
            
            if min_value is not None:
                query = query.filter(self.model.value >= min_value)
            if max_value is not None:
                query = query.filter(self.model.value <= max_value)
            
            return query.order_by(self.model.date).all()
        except Exception as e:
            self.log_error(f"Error getting Dollar Index by value range: {e}")
            return []
