"""
Repository for commodity price data access.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.repositories.base_repository import BaseRepository
from src.models import CommodityPrice


class CommodityRepository(BaseRepository):
    """Repository for commodity price data access."""
    
    def __init__(self, db: Session):
        super().__init__(db, CommodityPrice)
    
    def get_by_commodity(
        self,
        commodity: Optional[str] = None,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CommodityPrice]:
        """
        Get commodity prices by commodity or symbol.
        
        Args:
            commodity: Commodity name (e.g., GOLD, OIL)
            symbol: Trading symbol (e.g., XAUUSD, USOIL)
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of commodity price records
        """
        try:
            query = self.db.query(self.model)
            
            if commodity:
                query = query.filter(self.model.commodity == commodity.upper())
            if symbol:
                query = query.filter(self.model.symbol == symbol.upper())
            
            if start_date:
                query = query.filter(self.model.date >= start_date)
            if end_date:
                query = query.filter(self.model.date <= end_date)
            
            return query.order_by(self.model.date).all()
        except Exception as e:
            self.log_error(f"Error getting commodity prices: {e}")
            return []
    
    def get_latest_by_commodity(
        self,
        commodity: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> Optional[CommodityPrice]:
        """
        Get the latest commodity price.
        
        Args:
            commodity: Commodity name
            symbol: Trading symbol
            
        Returns:
            Latest commodity price record or None
        """
        try:
            query = self.db.query(self.model)
            
            if commodity:
                query = query.filter(self.model.commodity == commodity.upper())
            if symbol:
                query = query.filter(self.model.symbol == symbol.upper())
            
            return query.order_by(self.model.date.desc()).first()
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
            commodities = self.db.query(self.model.commodity).distinct().all()
            return [commodity[0] for commodity in commodities]
        except Exception as e:
            self.log_error(f"Error getting available commodities: {e}")
            return []
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of available trading symbols.
        
        Returns:
            List of trading symbols
        """
        try:
            symbols = self.db.query(self.model.symbol).distinct().filter(
                self.model.symbol.isnot(None)
            ).all()
            return [symbol[0] for symbol in symbols if symbol[0]]
        except Exception as e:
            self.log_error(f"Error getting available symbols: {e}")
            return []
    
    def get_date_range_for_commodity(
        self,
        commodity: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> Optional[tuple[date, date]]:
        """
        Get the date range for a specific commodity.
        
        Args:
            commodity: Commodity name
            symbol: Trading symbol
            
        Returns:
            Tuple of (start_date, end_date) or None
        """
        try:
            query = self.db.query(
                func.min(self.model.date),
                func.max(self.model.date)
            )
            
            if commodity:
                query = query.filter(self.model.commodity == commodity.upper())
            if symbol:
                query = query.filter(self.model.symbol == symbol.upper())
            
            result = query.first()
            
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None
        except Exception as e:
            self.log_error(f"Error getting date range for commodity: {e}")
            return None
