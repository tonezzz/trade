"""
Base repository class for common data access functionality.
"""
from typing import Optional, List, Dict, Any, Type
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import logging


class BaseRepository:
    """Base class for all repositories with common data access functionality."""
    
    def __init__(self, db: Session, model: Type):
        """
        Initialize repository with database session and model.
        
        Args:
            db: SQLAlchemy database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            self.log_error(f"Error getting {self.model.__name__} by id {id}: {e}")
            return None
    
    def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[Any]:
        """
        Get all records with optional pagination and ordering.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Column name to order by
            descending: Order in descending order
            
        Returns:
            List of model instances
        """
        try:
            query = self.db.query(self.model)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                column = getattr(self.model, order_by)
                if descending:
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(column)
            
            # Apply pagination
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except Exception as e:
            self.log_error(f"Error getting all {self.model.__name__}: {e}")
            return []
    
    def count(self) -> int:
        """
        Count total number of records.
        
        Returns:
            Total count of records
        """
        try:
            return self.db.query(self.model).count()
        except Exception as e:
            self.log_error(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    def create(self, **kwargs) -> Optional[Any]:
        """
        Create a new record.
        
        Args:
            **kwargs: Field values for the new record
            
        Returns:
            Created model instance or None
        """
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error creating {self.model.__name__}: {e}")
            return None
    
    def update(self, id: int, **kwargs) -> Optional[Any]:
        """
        Update an existing record.
        
        Args:
            id: Record ID
            **kwargs: Field values to update
            
        Returns:
            Updated model instance or None
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error updating {self.model.__name__} with id {id}: {e}")
            return None
    
    def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            self.db.delete(instance)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            return False
    
    def filter_by(self, **kwargs) -> List[Any]:
        """
        Filter records by field values.
        
        Args:
            **kwargs: Field values to filter by
            
        Returns:
            List of model instances
        """
        try:
            query = self.db.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.all()
        except Exception as e:
            self.log_error(f"Error filtering {self.model.__name__}: {e}")
            return []
    
    def get_by_date_range(
        self,
        date_field: str = 'date',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Any]:
        """
        Get records within a date range.
        
        Args:
            date_field: Name of the date field
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of model instances
        """
        try:
            query = self.db.query(self.model)
            
            if hasattr(self.model, date_field):
                date_column = getattr(self.model, date_field)
                
                if start_date:
                    query = query.filter(date_column >= start_date)
                if end_date:
                    query = query.filter(date_column <= end_date)
            
            return query.order_by(date_column).all()
        except Exception as e:
            self.log_error(f"Error getting {self.model.__name__} by date range: {e}")
            return []
    
    def get_latest(self, date_field: str = 'date') -> Optional[Any]:
        """
        Get the latest record by date.
        
        Args:
            date_field: Name of the date field
            
        Returns:
            Latest model instance or None
        """
        try:
            if hasattr(self.model, date_field):
                date_column = getattr(self.model, date_field)
                return self.db.query(self.model).order_by(desc(date_column)).first()
            return None
        except Exception as e:
            self.log_error(f"Error getting latest {self.model.__name__}: {e}")
            return None
    
    def exists(self, **kwargs) -> bool:
        """
        Check if a record exists matching the criteria.
        
        Args:
            **kwargs: Field values to check
            
        Returns:
            True if record exists, False otherwise
        """
        try:
            query = self.db.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.first() is not None
        except Exception as e:
            self.log_error(f"Error checking existence of {self.model.__name__}: {e}")
            return False
    
    def bulk_create(self, items: List[Dict[str, Any]]) -> int:
        """
        Create multiple records in bulk.
        
        Args:
            items: List of dictionaries with field values
            
        Returns:
            Number of records created
        """
        try:
            instances = [self.model(**item) for item in items]
            self.db.bulk_save_objects(instances)
            self.db.commit()
            return len(instances)
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error bulk creating {self.model.__name__}: {e}")
            return 0
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
