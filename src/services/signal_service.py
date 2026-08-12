"""
Service for trading signal business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.services.base_service import BaseService
from src.signals import SignalGenerator, SignalHistory as SignalHistoryTracker, Backtester


class SignalService(BaseService):
    """Service for trading signal operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.generator = SignalGenerator(db)
        self.history_tracker = SignalHistoryTracker(db)
        self.backtester = Backtester(db)
    
    def generate_signal(
        self,
        asset_type: str,
        asset_symbol: str,
        timeframe: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a trading signal for an asset.
        
        Args:
            asset_type: Type of asset (currency, commodity, dollar_index)
            asset_symbol: Symbol of the asset
            timeframe: Timeframe for analysis
            
        Returns:
            Dictionary with signal data or None
        """
        try:
            signal = self.generator.generate_signal(asset_type, asset_symbol, timeframe)
            
            if not signal:
                return None
            
            return signal.to_dict()
            
        except Exception as e:
            self.log_error(f"Error generating signal for {asset_type}/{asset_symbol}: {e}")
            return None
    
    def get_signal_history(
        self,
        asset_type: str,
        asset_symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get signal history for an asset.
        
        Args:
            asset_type: Type of asset
            asset_symbol: Symbol of the asset
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dictionary with signal history data
        """
        try:
            history = self.history_tracker.get_history(
                asset_type, asset_symbol, start_date, end_date, limit, offset
            )
            
            data_list = [
                {
                    'id': signal.id,
                    'asset_type': signal.asset_type,
                    'asset_symbol': signal.asset_symbol,
                    'signal_type': signal.signal_type,
                    'strength': signal.strength,
                    'confidence': signal.confidence,
                    'timestamp': signal.timestamp.isoformat(),
                    'price': signal.price,
                    'indicators': signal.indicators or {},
                    'reasons': signal.reasons or [],
                    'timeframe': signal.timeframe
                }
                for signal in history
            ]
            
            return {
                'data': data_list,
                'count': len(data_list),
                'asset_type': asset_type,
                'asset_symbol': asset_symbol
            }
            
        except Exception as e:
            return self.handle_exception(e, f"Error getting signal history for {asset_type}/{asset_symbol}")
    
    def get_signal_performance(
        self,
        asset_type: str,
        asset_symbol: str,
        timeframe: str = "1d",
        test_start_date: date = None,
        test_end_date: date = None,
        initial_capital: float = 10000.0
    ) -> Optional[Dict[str, Any]]:
        """
        Get signal performance metrics.
        
        Args:
            asset_type: Type of asset
            asset_symbol: Symbol of the asset
            timeframe: Timeframe for analysis
            test_start_date: Start date for performance test
            test_end_date: End date for performance test
            initial_capital: Initial capital for performance calculation
            
        Returns:
            Dictionary with performance metrics or None
        """
        try:
            performance = self.backtester.backtest_signals(
                asset_type, asset_symbol, timeframe,
                test_start_date, test_end_date, initial_capital
            )
            
            if not performance:
                return None
            
            return performance
            
        except Exception as e:
            self.log_error(f"Error getting signal performance for {asset_type}/{asset_symbol}: {e}")
            return None
    
    def get_active_signals(self) -> List[Dict[str, Any]]:
        """
        Get all currently active signals.
        
        Returns:
            List of active signal data
        """
        try:
            active_signals = self.history_tracker.get_active_signals()
            
            return [
                {
                    'asset_type': signal.asset_type,
                    'asset_symbol': signal.asset_symbol,
                    'signal_type': signal.signal_type,
                    'strength': signal.strength,
                    'confidence': signal.confidence,
                    'timestamp': signal.timestamp.isoformat(),
                    'price': signal.price
                }
                for signal in active_signals
            ]
            
        except Exception as e:
            self.log_error(f"Error getting active signals: {e}")
            return []
    
    def get_signal_statistics(
        self,
        asset_type: Optional[str] = None,
        asset_symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for signals.
        
        Args:
            asset_type: Optional asset type filter
            asset_symbol: Optional asset symbol filter
            
        Returns:
            Dictionary with signal statistics
        """
        try:
            # Get signal history
            history = self.history_tracker.get_history(
                asset_type, asset_symbol, limit=1000
            )
            
            if not history:
                return {'error': 'No signal history found'}
            
            # Calculate statistics
            buy_signals = [s for s in history if s.signal_type == 'buy']
            sell_signals = [s for s in history if s.signal_type == 'sell']
            hold_signals = [s for s in history if s.signal_type == 'hold']
            
            strong_signals = [s for s in history if s.strength == 'strong']
            weak_signals = [s for s in history if s.strength == 'weak']
            
            avg_confidence = sum(s.confidence for s in history) / len(history) if history else 0
            
            return {
                'total_signals': len(history),
                'by_type': {
                    'buy': len(buy_signals),
                    'sell': len(sell_signals),
                    'hold': len(hold_signals)
                },
                'by_strength': {
                    'strong': len(strong_signals),
                    'weak': len(weak_signals)
                },
                'average_confidence': avg_confidence,
                'asset_type': asset_type,
                'asset_symbol': asset_symbol
            }
            
        except Exception as e:
            return self.handle_exception(e, "Error getting signal statistics")
