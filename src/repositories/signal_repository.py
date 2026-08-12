"""
Repository for signal data access.
"""
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from src.repositories.base_repository import BaseRepository
from src.models import SignalHistory, SignalPerformance


class SignalRepository(BaseRepository):
    """Repository for signal data access."""
    
    def __init__(self, db: Session):
        # Initialize with SignalHistory as the primary model
        super().__init__(db, SignalHistory)
        self.performance_model = SignalPerformance
    
    def get_by_asset(
        self,
        asset_type: str,
        asset_symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SignalHistory]:
        """
        Get signal history for an asset.
        
        Args:
            asset_type: Type of asset (currency, commodity, dollar_index)
            asset_symbol: Symbol of the asset
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of signal history records
        """
        try:
            query = self.db.query(self.model).filter(
                self.model.asset_type == asset_type,
                self.model.asset_symbol == asset_symbol.upper()
            )
            
            if start_date:
                query = query.filter(self.model.timestamp >= start_date)
            if end_date:
                query = query.filter(self.model.timestamp <= end_date)
            
            query = query.order_by(desc(self.model.timestamp))
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except Exception as e:
            self.log_error(f"Error getting signal history for {asset_type}/{asset_symbol}: {e}")
            return []
    
    def get_active_signals(self) -> List[SignalHistory]:
        """
        Get all active signals (most recent for each asset).
        
        Returns:
            List of active signal records
        """
        try:
            # Get the most recent signal for each asset
            subquery = self.db.query(
                self.model.asset_type,
                self.model.asset_symbol,
                func.max(self.model.timestamp).label('max_timestamp')
            ).group_by(
                self.model.asset_type,
                self.model.asset_symbol
            ).subquery()
            
            query = self.db.query(self.model).join(
                subquery,
                and_(
                    self.model.asset_type == subquery.c.asset_type,
                    self.model.asset_symbol == subquery.c.asset_symbol,
                    self.model.timestamp == subquery.c.max_timestamp
                )
            )
            
            return query.all()
        except Exception as e:
            self.log_error(f"Error getting active signals: {e}")
            return []
    
    def get_signal_performance(
        self,
        asset_type: str,
        asset_symbol: str,
        timeframe: str
    ) -> Optional[SignalPerformance]:
        """
        Get signal performance metrics for an asset.
        
        Args:
            asset_type: Type of asset
            asset_symbol: Symbol of the asset
            timeframe: Timeframe for analysis
            
        Returns:
            Signal performance record or None
        """
        try:
            return self.db.query(self.performance_model).filter(
                self.performance_model.asset_type == asset_type,
                self.performance_model.asset_symbol == asset_symbol.upper(),
                self.performance_model.timeframe == timeframe
            ).order_by(desc(self.performance_model.test_end_date)).first()
        except Exception as e:
            self.log_error(f"Error getting signal performance for {asset_type}/{asset_symbol}: {e}")
            return None
    
    def create_signal_performance(self, **kwargs) -> Optional[SignalPerformance]:
        """
        Create a new signal performance record.
        
        Args:
            **kwargs: Field values for the performance record
            
        Returns:
            Created performance record or None
        """
        try:
            instance = self.performance_model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error creating signal performance: {e}")
            return None
    
    def get_signal_statistics(
        self,
        asset_type: Optional[str] = None,
        asset_symbol: Optional[str] = None
    ) -> dict:
        """
        Get statistics for signals.
        
        Args:
            asset_type: Optional asset type filter
            asset_symbol: Optional asset symbol filter
            
        Returns:
            Dictionary with signal statistics
        """
        try:
            query = self.db.query(self.model)
            
            if asset_type:
                query = query.filter(self.model.asset_type == asset_type)
            if asset_symbol:
                query = query.filter(self.model.asset_symbol == asset_symbol.upper())
            
            total_signals = query.count()
            
            # Count by signal type
            buy_count = query.filter(self.model.signal_type == 'buy').count()
            sell_count = query.filter(self.model.signal_type == 'sell').count()
            hold_count = query.filter(self.model.signal_type == 'hold').count()
            
            # Count by strength
            strong_count = query.filter(self.model.strength == 'strong').count()
            moderate_count = query.filter(self.model.strength == 'moderate').count()
            weak_count = query.filter(self.model.strength == 'weak').count()
            
            # Average confidence
            avg_confidence = query.with_entities(
                func.avg(self.model.confidence)
            ).scalar() or 0
            
            return {
                'total_signals': total_signals,
                'by_type': {
                    'buy': buy_count,
                    'sell': sell_count,
                    'hold': hold_count
                },
                'by_strength': {
                    'strong': strong_count,
                    'moderate': moderate_count,
                    'weak': weak_count
                },
                'average_confidence': float(avg_confidence)
            }
        except Exception as e:
            self.log_error(f"Error getting signal statistics: {e}")
            return {}
