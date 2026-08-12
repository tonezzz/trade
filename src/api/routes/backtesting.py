"""
Backtesting API routes.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.backtesting import (
    BacktestEngine, BacktestConfig, get_strategy, list_strategies,
    ParameterOptimizer, WalkForwardAnalysis, StrategyComparator, PerformanceReport
)
from src.api.schemas import (
    BacktestRequest,
    BacktestResponse,
    OptimizeRequest,
    OptimizeResponse,
    CompareRequest,
    StrategiesResponse
)

router = APIRouter()


@router.get("/backtesting/strategies", response_model=StrategiesResponse)
async def list_available_strategies():
    """
    List all available backtesting strategies.
    
    Returns:
        List of available strategy names
    """
    try:
        strategies = list_strategies()
        return StrategiesResponse(
            strategies=strategies,
            count=len(strategies)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing strategies: {str(e)}"
        )


@router.post("/backtesting/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    strategy_name: str = Query(..., description="Strategy name"),
    db: Session = Depends(get_db)
):
    """
    Run a backtest for a specific strategy.
    
    Args:
        request: Backtest configuration
        strategy_name: Name of the strategy to use
    
    Returns:
        Backtest results with performance metrics
    """
    try:
        # Load configuration
        config = BacktestConfig.from_yaml()
        
        # Override with request parameters
        config.initial_capital = request.initial_capital
        config.commission_rate = request.commission
        
        # Get strategy
        strategy = get_strategy(strategy_name)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy not found: {strategy_name}"
            )
        
        # Get historical data
        from src.queries import PriceQueries
        queries = PriceQueries(db)
        
        if request.asset_type == "currency":
            df = queries.get_exchange_rates(request.asset_symbol, request.start_date, request.end_date)
        elif request.asset_type == "commodity":
            df = queries.get_commodity_prices(
                commodity=request.asset_symbol, 
                start_date=request.start_date, 
                end_date=request.end_date
            )
        elif request.asset_type == "dollar_index":
            df = queries.get_dollar_index(request.start_date, request.end_date)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {request.asset_type}"
            )
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data available for {request.asset_type}/{request.asset_symbol}"
            )
        
        # Prepare data for backtesting
        df = df.rename(columns={
            'rate': 'close',
            'value': 'close',
            'price': 'close'
        })
        
        # Ensure required columns
        for col in ['open', 'high', 'low']:
            if col not in df.columns:
                df[col] = df['close']
        
        # Run backtest
        engine = BacktestEngine(config)
        engine.set_data(df)
        engine.set_strategy(strategy)
        results = engine.run()
        
        return BacktestResponse(
            backtest_id=engine.backtest_id,
            strategy_name=strategy_name,
            symbol=request.asset_symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            final_capital=results['final_capital'],
            total_return=results['total_return'],
            total_return_pct=results['total_return_pct'],
            sharpe_ratio=results.get('sharpe_ratio'),
            sortino_ratio=results.get('sortino_ratio'),
            max_drawdown=results['max_drawdown'],
            max_drawdown_pct=results['max_drawdown_pct'],
            win_rate=results['win_rate'],
            profit_factor=results['profit_factor'],
            total_trades=results['total_trades'],
            winning_trades=results['winning_trades'],
            losing_trades=results['losing_trades'],
            avg_win=results.get('avg_win'),
            avg_loss=results.get('avg_loss'),
            largest_win=results.get('largest_win'),
            largest_loss=results.get('largest_loss'),
            avg_trade_duration=results.get('avg_trade_duration'),
            parameters=strategy.parameters,
            equity_curve=results.get('equity_curve', []),
            trades=results.get('trades', [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running backtest: {str(e)}"
        )


@router.post("/backtesting/optimize", response_model=OptimizeResponse)
async def optimize_strategy(
    request: OptimizeRequest,
    strategy_name: str = Query(..., description="Strategy name"),
    db: Session = Depends(get_db)
):
    """
    Optimize strategy parameters.
    
    Args:
        request: Optimization configuration
        strategy_name: Name of the strategy to optimize
    
    Returns:
        Optimization results with best parameters
    """
    try:
        # Load configuration
        config = BacktestConfig.from_yaml()
        
        # Get historical data (same as backtest)
        from src.queries import PriceQueries
        queries = PriceQueries(db)
        
        if request.asset_type == "currency":
            df = queries.get_exchange_rates(request.asset_symbol, request.start_date, request.end_date)
        elif request.asset_type == "commodity":
            df = queries.get_commodity_prices(
                commodity=request.asset_symbol, 
                start_date=request.start_date, 
                end_date=request.end_date
            )
        elif request.asset_type == "dollar_index":
            df = queries.get_dollar_index(request.start_date, request.end_date)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {request.asset_type}"
            )
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data available for {request.asset_type}/{request.asset_symbol}"
            )
        
        # Prepare data
        df = df.rename(columns={'rate': 'close', 'value': 'close', 'price': 'close'})
        for col in ['open', 'high', 'low']:
            if col not in df.columns:
                df[col] = df['close']
        
        # Run optimization
        optimizer = ParameterOptimizer(config)
        results = optimizer.optimize(
            strategy_name, df, request.parameters
        )
        
        return OptimizeResponse(
            best_parameters=results['best_parameters'],
            best_sharpe=results['best_sharpe'],
            all_results=results['all_results']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing strategy: {str(e)}"
        )


@router.post("/backtesting/compare")
async def compare_strategies(
    request: CompareRequest,
    db: Session = Depends(get_db)
):
    """
    Compare multiple strategies.
    
    Args:
        request: Comparison configuration
    
    Returns:
        Comparison results for all strategies
    """
    try:
        # Load configuration
        config = BacktestConfig.from_yaml()
        
        # Get historical data
        from src.queries import PriceQueries
        queries = PriceQueries(db)
        
        if request.asset_type == "currency":
            df = queries.get_exchange_rates(request.asset_symbol, request.start_date, request.end_date)
        elif request.asset_type == "commodity":
            df = queries.get_commodity_prices(
                commodity=request.asset_symbol, 
                start_date=request.start_date, 
                end_date=request.end_date
            )
        elif request.asset_type == "dollar_index":
            df = queries.get_dollar_index(request.start_date, request.end_date)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {request.asset_type}"
            )
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data available for {request.asset_type}/{request.asset_symbol}"
            )
        
        # Prepare data
        df = df.rename(columns={'rate': 'close', 'value': 'close', 'price': 'close'})
        for col in ['open', 'high', 'low']:
            if col not in df.columns:
                df[col] = df['close']
        
        # Run comparison
        comparator = StrategyComparator(config)
        results = comparator.compare(
            request.strategies, df, request.asset_symbol
        )
        
        return {
            "strategies": request.strategies,
            "comparison": results,
            "best_strategy": results.get('best_strategy'),
            "summary": results.get('summary')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing strategies: {str(e)}"
        )
