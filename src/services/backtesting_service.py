"""
Service for backtesting business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.services.base_service import BaseService
from src.backtesting import (
    BacktestEngine, BacktestConfig, get_strategy, list_strategies,
    ParameterOptimizer, WalkForwardAnalysis, StrategyComparator, PerformanceReport
)
from src.queries import PriceQueries


class BacktestingService(BaseService):
    """Service for backtesting operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.queries = PriceQueries(db)
        self.config = BacktestConfig.from_yaml()
    
    def list_strategies(self) -> List[str]:
        """
        Get list of available backtesting strategies.
        
        Returns:
            List of strategy names
        """
        try:
            return list_strategies()
        except Exception as e:
            self.log_error(f"Error listing strategies: {e}")
            return []
    
    def run_backtest(
        self,
        strategy_name: str,
        asset_type: str,
        asset_symbol: str,
        start_date: date,
        end_date: date,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        timeframe: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Run a backtest for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
            asset_type: Type of asset
            asset_symbol: Symbol of the asset
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_capital: Initial capital
            commission: Commission rate
            timeframe: Timeframe for analysis
            
        Returns:
            Dictionary with backtest results or None
        """
        try:
            # Override config with request parameters
            self.config.initial_capital = initial_capital
            self.config.commission_rate = commission
            
            # Get strategy
            strategy = get_strategy(strategy_name)
            if not strategy:
                return None
            
            # Get historical data
            df = self._get_historical_data(asset_type, asset_symbol, start_date, end_date)
            
            if df.empty:
                return None
            
            # Prepare data for backtesting
            df = self._prepare_backtest_data(df)
            
            # Run backtest
            engine = BacktestEngine(self.config)
            engine.set_data(df)
            engine.set_strategy(strategy)
            results = engine.run()
            
            return {
                'backtest_id': engine.backtest_id,
                'strategy_name': strategy_name,
                'symbol': asset_symbol,
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': initial_capital,
                **results
            }
            
        except Exception as e:
            self.log_error(f"Error running backtest: {e}")
            return None
    
    def optimize_strategy(
        self,
        strategy_name: str,
        asset_type: str,
        asset_symbol: str,
        start_date: date,
        end_date: date,
        parameters: Dict[str, Any],
        initial_capital: float = 10000.0,
        commission: float = 0.001
    ) -> Optional[Dict[str, Any]]:
        """
        Optimize strategy parameters.
        
        Args:
            strategy_name: Name of the strategy
            asset_type: Type of asset
            asset_symbol: Symbol of the asset
            start_date: Start date for optimization
            end_date: End date for optimization
            parameters: Parameter ranges for optimization
            initial_capital: Initial capital
            commission: Commission rate
            
        Returns:
            Dictionary with optimization results or None
        """
        try:
            # Override config
            self.config.initial_capital = initial_capital
            self.config.commission_rate = commission
            
            # Get historical data
            df = self._get_historical_data(asset_type, asset_symbol, start_date, end_date)
            
            if df.empty:
                return None
            
            # Prepare data
            df = self._prepare_backtest_data(df)
            
            # Run optimization
            optimizer = ParameterOptimizer(self.config)
            results = optimizer.optimize(strategy_name, df, parameters)
            
            return results
            
        except Exception as e:
            self.log_error(f"Error optimizing strategy: {e}")
            return None
    
    def compare_strategies(
        self,
        strategies: List[str],
        asset_type: str,
        asset_symbol: str,
        start_date: date,
        end_date: date,
        initial_capital: float = 10000.0,
        commission: float = 0.001
    ) -> Optional[Dict[str, Any]]:
        """
        Compare multiple strategies.
        
        Args:
            strategies: List of strategy names to compare
            asset_type: Type of asset
            asset_symbol: Symbol of the asset
            start_date: Start date for comparison
            end_date: End date for comparison
            initial_capital: Initial capital
            commission: Commission rate
            
        Returns:
            Dictionary with comparison results or None
        """
        try:
            # Override config
            self.config.initial_capital = initial_capital
            self.config.commission_rate = commission
            
            # Get historical data
            df = self._get_historical_data(asset_type, asset_symbol, start_date, end_date)
            
            if df.empty:
                return None
            
            # Prepare data
            df = self._prepare_backtest_data(df)
            
            # Run comparison
            comparator = StrategyComparator(self.config)
            results = comparator.compare(strategies, df, asset_symbol)
            
            return results
            
        except Exception as e:
            self.log_error(f"Error comparing strategies: {e}")
            return None
    
    def _get_historical_data(
        self,
        asset_type: str,
        asset_symbol: str,
        start_date: date,
        end_date: date
    ) -> Any:
        """Get historical data for backtesting."""
        if asset_type == "currency":
            return self.queries.get_exchange_rates(asset_symbol, start_date, end_date)
        elif asset_type == "commodity":
            return self.queries.get_commodity_prices(
                commodity=asset_symbol, start_date=start_date, end_date=end_date
            )
        elif asset_type == "dollar_index":
            return self.queries.get_dollar_index(start_date, end_date)
        else:
            raise ValueError(f"Invalid asset type: {asset_type}")
    
    def _prepare_backtest_data(self, df: Any) -> Any:
        """Prepare data for backtesting."""
        import pandas as pd
        
        # Rename columns to standard format
        column_mapping = {
            'rate': 'close',
            'value': 'close',
            'price': 'close'
        }
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        for col in ['open', 'high', 'low']:
            if col not in df.columns:
                df[col] = df['close']
        
        return df
