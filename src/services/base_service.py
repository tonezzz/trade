"""
Base service class for common service functionality.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
import logging


class BaseService:
    """Base class for all services with common functionality."""
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def validate_date_range(self, start_date: Optional[date], end_date: Optional[date]) -> tuple[date, date]:
        """
        Validate and normalize date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValueError: If date range is invalid
        """
        if start_date and end_date and start_date > end_date:
            raise ValueError(f"Start date ({start_date}) cannot be after end date ({end_date})")
        
        if not start_date:
            start_date = date.min
        if not end_date:
            end_date = date.max
            
        return start_date, end_date
    
    def parse_period(self, period: str) -> tuple[date, date]:
        """
        Parse period string to start and end dates.
        
        Args:
            period: Period string (1d, 1w, 1m, 3m, 6m, 1y, 5y)
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValueError: If period is invalid
        """
        from datetime import timedelta
        today = date.today()
        period_map = {
            '1d': (today, today),
            '1w': (today - timedelta(days=7), today),
            '1m': (today - timedelta(days=30), today),
            '3m': (today - timedelta(days=90), today),
            '6m': (today - timedelta(days=180), today),
            '1y': (today - timedelta(days=365), today),
            '5y': (today - timedelta(days=1825), today),
        }
        
        if period not in period_map:
            raise ValueError(f"Invalid period: {period}. Must be one of: {list(period_map.keys())}")
        
        return period_map[period]
    
    def apply_pagination(self, data: list, limit: Optional[int], offset: int = 0) -> Dict[str, Any]:
        """
        Apply pagination to data list.
        
        Args:
            data: List of data items
            limit: Maximum number of items to return
            offset: Number of items to skip
            
        Returns:
            Dictionary with paginated data and metadata
        """
        if limit is not None and limit > 0:
            paginated_data = data[offset:offset + limit]
            has_more = len(data) > offset + limit
        else:
            paginated_data = data[offset:]
            has_more = False
        
        return {
            'data': paginated_data,
            'count': len(data),
            'limit': limit,
            'offset': offset,
            'has_more': has_more
        }
    
    def handle_exception(self, exception: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle exception and return error response.
        
        Args:
            exception: Exception to handle
            context: Context information for the error
            
        Returns:
            Dictionary with error information
        """
        error_message = f"{context}: {str(exception)}" if context else str(exception)
        self.log_error(error_message, exc_info=True)
        
        return {
            'error': error_message,
            'error_type': type(exception).__name__,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
