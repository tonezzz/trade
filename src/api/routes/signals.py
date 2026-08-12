"""
Trading signals API routes.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.signals import SignalGenerator, SignalHistory as SignalHistoryTracker
from src.api.schemas import (
    SignalResponse,
    SignalHistoryResponse,
    SignalPerformanceResponse
)

router = APIRouter()


@router.get("/signals/{asset_type}/{asset_symbol}", response_model=SignalResponse)
async def generate_signal(
    asset_type: str,
    asset_symbol: str,
    timeframe: str = Query("1d", description="Timeframe (1d, 1w, 1m)"),
    db: Session = Depends(get_db)
):
    """
    Generate a trading signal for an asset.
    
    Args:
        asset_type: Type of asset (currency, commodity, dollar_index)
        asset_symbol: Symbol of the asset (EUR, GOLD, DXY, etc.)
        timeframe: Timeframe for analysis (1d, 1w, 1m)
    
    Returns:
        Generated trading signal with indicators and reasoning
    """
    try:
        generator = SignalGenerator(db)
        signal = generator.generate_signal(asset_type, asset_symbol, timeframe)
        
        if not signal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to generate signal for {asset_type}/{asset_symbol}"
            )
        
        return SignalResponse(**signal.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating signal: {str(e)}"
        )


@router.get("/signals/{asset_type}/{asset_symbol}/history", response_model=list[SignalHistoryResponse])
async def get_signal_history(
    asset_type: str,
    asset_symbol: str,
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get signal history for an asset.
    
    Args:
        asset_type: Type of asset (currency, commodity, dollar_index)
        asset_symbol: Symbol of the asset (EUR, GOLD, DXY, etc.)
        start_date: Start date for filtering
        end_date: End date for filtering
        limit: Maximum number of results to return
        offset: Number of results to skip
    
    Returns:
        List of historical signals
    """
    try:
        tracker = SignalHistoryTracker(db)
        history = tracker.get_history(
            asset_type, asset_symbol, start_date, end_date, limit, offset
        )
        
        return [
            SignalHistoryResponse(
                id=signal.id,
                asset_type=signal.asset_type,
                asset_symbol=signal.asset_symbol,
                signal_type=signal.signal_type,
                strength=signal.strength,
                confidence=signal.confidence,
                timestamp=signal.timestamp.isoformat(),
                price=signal.price,
                indicators=signal.indicators or {},
                reasons=signal.reasons or [],
                timeframe=signal.timeframe
            )
            for signal in history
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving signal history: {str(e)}"
        )


@router.get("/signals/{asset_type}/{asset_symbol}/performance", response_model=SignalPerformanceResponse)
async def get_signal_performance(
    asset_type: str,
    asset_symbol: str,
    timeframe: str = Query("1d", description="Timeframe"),
    test_start_date: date = Query(..., description="Test start date"),
    test_end_date: date = Query(..., description="Test end date"),
    initial_capital: float = Query(10000.0, description="Initial capital"),
    db: Session = Depends(get_db)
):
    """
    Get signal performance metrics.
    
    Args:
        asset_type: Type of asset (currency, commodity, dollar_index)
        asset_symbol: Symbol of the asset (EUR, GOLD, DXY, etc.)
        timeframe: Timeframe for analysis
        test_start_date: Start date for performance test
        test_end_date: End date for performance test
        initial_capital: Initial capital for performance calculation
    
    Returns:
        Signal performance metrics
    """
    try:
        from src.signals import Backtester
        backtester = Backtester(db)
        performance = backtester.backtest_signals(
            asset_type, asset_symbol, timeframe, test_start_date, test_end_date, initial_capital
        )
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No performance data available for {asset_type}/{asset_symbol}"
            )
        
        return SignalPerformanceResponse(**performance)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving signal performance: {str(e)}"
        )


@router.get("/signals/active")
async def list_active_signals(db: Session = Depends(get_db)):
    """
    List all active signals.
    
    Returns:
        List of currently active trading signals
    """
    try:
        tracker = SignalHistoryTracker(db)
        active_signals = tracker.get_active_signals()
        
        return {
            "count": len(active_signals),
            "signals": [
                {
                    "asset_type": signal.asset_type,
                    "asset_symbol": signal.asset_symbol,
                    "signal_type": signal.signal_type,
                    "strength": signal.strength,
                    "confidence": signal.confidence,
                    "timestamp": signal.timestamp.isoformat(),
                    "price": signal.price
                }
                for signal in active_signals
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing active signals: {str(e)}"
        )
