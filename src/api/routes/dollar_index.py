"""
Dollar Index API routes.
"""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.queries import PriceQueries, PriceAnalysis
from src.api.schemas import DollarIndexResponse, DollarIndexPerformanceResponse

router = APIRouter()


def parse_period(period: str) -> tuple[date, date]:
    """Parse period string to start and end dates."""
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period: {period}. Must be one of: {list(period_map.keys())}"
        )
    
    return period_map[period]


@router.get("/dollar_index", response_model=list[DollarIndexResponse])
async def get_dollar_index(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    period: Optional[str] = Query(None, description="Period (1d, 1w, 1m, 3m, 6m, 1y, 5y)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get Dollar Index (DXY) data.
    
    Args:
        start_date: Start date for filtering
        end_date: End date for filtering
        period: Period string (alternative to start/end dates)
        limit: Maximum number of results to return
        offset: Number of results to skip
    
    Returns:
        List of Dollar Index data
    """
    try:
        # Handle period parameter
        if period:
            start_date, end_date = parse_period(period)
        
        queries = PriceQueries(db)
        df = queries.get_dollar_index(start_date, end_date)
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Dollar Index data found"
            )
        
        # Apply pagination
        data_list = df.to_dict('records')
        if limit:
            paginated_data = data_list[offset:offset + limit]
        else:
            paginated_data = data_list[offset:]
        
        # Convert to response models
        dollar_index_data = [
            DollarIndexResponse(
                date=row['date'],
                value=row['value'],
                open=row.get('open'),
                high=row.get('high'),
                low=row.get('low'),
                close=row.get('close'),
                volume=row.get('volume')
            )
            for row in paginated_data
        ]
        
        return dollar_index_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Dollar Index data: {str(e)}"
        )


@router.get("/dollar_index/latest", response_model=DollarIndexResponse)
async def get_latest_dollar_index(db: Session = Depends(get_db)):
    """
    Get the latest Dollar Index value.
    
    Returns:
        Latest Dollar Index data
    """
    try:
        queries = PriceQueries(db)
        latest = queries.get_latest_dollar_index()
        
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Dollar Index data found"
            )
        
        return DollarIndexResponse(
            date=latest.date,
            value=latest.value,
            open=latest.open_price,
            high=latest.high_price,
            low=latest.low_price,
            close=latest.close_price,
            volume=latest.volume
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving latest Dollar Index: {str(e)}"
        )


@router.get("/dollar_index/performance", response_model=DollarIndexPerformanceResponse)
async def get_dxy_performance(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """
    Calculate Dollar Index performance over a period.
    
    Args:
        start_date: Start date for analysis
        end_date: End date for analysis
    
    Returns:
        Performance metrics
    """
    try:
        analysis = PriceAnalysis(db)
        performance = analysis.calculate_dxy_performance(start_date, end_date)
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data available for performance analysis"
            )
        
        return DollarIndexPerformanceResponse(**performance)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating performance: {str(e)}"
        )
