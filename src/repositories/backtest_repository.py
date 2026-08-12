"""
Repository for backtest data access.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from src.repositories.base_repository import BaseRepository
from src.models import BacktestResult, BacktestTrade, BacktestEquity


class BacktestRepository(BaseRepository):
    """Repository for backtest data access."""
    
    def __init__(self, db: Session):
        # Initialize with BacktestResult as the primary model
        super().__init__(db, BacktestResult)
        self.trade_model = BacktestTrade
        self.equity_model = BacktestEquity
    
    def get_by_backtest_id(self, backtest_id: str) -> Optional[BacktestResult]:
        """
        Get a backtest result by backtest ID.
        
        Args:
            backtest_id: Backtest ID
            
        Returns:
            Backtest result record or None
        """
        try:
            return self.db.query(self.model).filter(
                self.model.backtest_id == backtest_id
            ).first()
        except Exception as e:
            self.log_error(f"Error getting backtest {backtest_id}: {e}")
            return None
    
    def get_by_strategy(
        self,
        strategy_name: str,
        symbol: str,
        limit: int = 10
    ) -> List[BacktestResult]:
        """
        Get backtest results for a specific strategy and symbol.
        
        Args:
            strategy_name: Name of the strategy
            symbol: Trading symbol
            limit: Maximum number of results
            
        Returns:
            List of backtest result records
        """
        try:
            return self.db.query(self.model).filter(
                self.model.strategy_name == strategy_name,
                self.model.symbol == symbol.upper()
            ).order_by(desc(self.model.created_at)).limit(limit).all()
        except Exception as e:
            self.log_error(f"Error getting backtests for {strategy_name}/{symbol}: {e}")
            return []
    
    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100
    ) -> List[BacktestResult]:
        """
        Get backtest results within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            limit: Maximum number of results
            
        Returns:
            List of backtest result records
        """
        try:
            return self.db.query(self.model).filter(
                self.model.start_date >= start_date,
                self.model.end_date <= end_date
            ).order_by(desc(self.model.created_at)).limit(limit).all()
        except Exception as e:
            self.log_error(f"Error getting backtests by date range: {e}")
            return []
    
    def get_trades(self, backtest_id: str) -> List[BacktestTrade]:
        """
        Get all trades for a backtest.
        
        Args:
            backtest_id: Backtest ID
            
        Returns:
            List of trade records
        """
        try:
            return self.db.query(self.trade_model).filter(
                self.trade_model.backtest_id == backtest_id
            ).order_by(self.trade_model.entry_date).all()
        except Exception as e:
            self.log_error(f"Error getting trades for backtest {backtest_id}: {e}")
            return []
    
    def get_equity_curve(self, backtest_id: str) -> List[BacktestEquity]:
        """
        Get equity curve for a backtest.
        
        Args:
            backtest_id: Backtest ID
            
        Returns:
            List of equity curve records
        """
        try:
            return self.db.query(self.equity_model).filter(
                self.equity_model.backtest_id == backtest_id
            ).order_by(self.equity_model.date).all()
        except Exception as e:
            self.log_error(f"Error getting equity curve for backtest {backtest_id}: {e}")
            return []
    
    def create_backtest_result(self, **kwargs) -> Optional[BacktestResult]:
        """
        Create a new backtest result.
        
        Args:
            **kwargs: Field values for the backtest result
            
        Returns:
            Created backtest result or None
        """
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error creating backtest result: {e}")
            return None
    
    def create_trade(self, **kwargs) -> Optional[BacktestTrade]:
        """
        Create a new trade record.
        
        Args:
            **kwargs: Field values for the trade
            
        Returns:
            Created trade record or None
        """
        try:
            instance = self.trade_model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error creating trade: {e}")
            return None
    
    def create_equity_point(self, **kwargs) -> Optional[BacktestEquity]:
        """
        Create a new equity curve point.
        
        Args:
            **kwargs: Field values for the equity point
            
        Returns:
            Created equity point or None
        """
        try:
            instance = self.equity_model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            self.db.rollback()
            self.log_error(f"Error creating equity point: {e}")
            return None
    
    def get_backtest_statistics(self, strategy_name: Optional[str] = None) -> dict:
        """
        Get statistics for backtests.
        
        Args:
            strategy_name: Optional strategy name filter
            
        Returns:
            Dictionary with backtest statistics
        """
        try:
            query = self.db.query(self.model)
            
            if strategy_name:
                query = query.filter(self.model.strategy_name == strategy_name)
            
            total_backtests = query.count()
            
            # Count by status
            completed_count = query.filter(self.model.status == 'completed').count()
            failed_count = query.filter(self.model.status == 'failed').count()
            running_count = query.filter(self.model.status == 'running').count()
            
            # Average performance
            avg_return = query.with_entities(
                func.avg(self.model.total_return_pct)
            ).scalar() or 0
            
            avg_sharpe = query.with_entities(
                func.avg(self.model.sharpe_ratio)
            ).scalar() or 0
            
            return {
                'total_backtests': total_backtests,
                'by_status': {
                    'completed': completed_count,
                    'failed': failed_count,
                    'running': running_count
                },
                'average_return_pct': float(avg_return),
                'average_sharpe_ratio': float(avg_sharpe)
            }
        except Exception as e:
            self.log_error(f"Error getting backtest statistics: {e}")
            return {}
