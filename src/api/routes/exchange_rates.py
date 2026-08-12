"""
Exchange rates API routes.
"""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.queries import PriceQueries, PriceAnalysis
from src.api.schemas import (
    ExchangeRateResponse,
    ExchangeRateListResponse,
    CurrencyPerformanceResponse,
    AvailableItemsResponse
)

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


@router.get("/exchange_rates/{currency}", response_model=ExchangeRateListResponse)
async def get_exchange_rates(
    currency: str,
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    period: Optional[str] = Query(None, description="Period (1d, 1w, 1m, 3m, 6m, 1y, 5y)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get exchange rates for a specific currency.
    
    Args:
        currency: Currency code (e.g., EUR, GBP, JPY)
        start_date: Start date for filtering
        end_date: End date for filtering
        period: Period string (alternative to start/end dates)
        limit: Maximum number of results to return
        offset: Number of results to skip
    
    Returns:
        List of exchange rate data
    """
    try:
        # Handle period parameter
        if period:
            start_date, end_date = parse_period(period)
        
        queries = PriceQueries(db)
        df = queries.get_exchange_rates(currency.upper(), start_date, end_date)
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exchange rate data found for currency: {currency}"
            )
        
        # Apply pagination
        data_list = df.to_dict('records')
        if limit:
            paginated_data = data_list[offset:offset + limit]
            has_more = len(data_list) > offset + limit
        else:
            paginated_data = data_list[offset:]
            has_more = False
        
        # Convert to response models
        exchange_rates = [
            ExchangeRateResponse(
                date=row['date'],
                base_currency='USD',
                quote_currency=currency.upper(),
                rate=row['rate'],
                open=row.get('open'),
                high=row.get('high'),
                low=row.get('low'),
                close=row.get('close'),
                volume=row.get('volume')
            )
            for row in paginated_data
        ]
        
        return ExchangeRateListResponse(
            data=exchange_rates,
            count=len(data_list),
            currency=currency.upper()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exchange rates: {str(e)}"
        )


@router.get("/exchange_rates/{currency}/latest", response_model=ExchangeRateResponse)
async def get_latest_exchange_rate(
    currency: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest exchange rate for a currency.
    
    Args:
        currency: Currency code (e.g., EUR, GBP, JPY)
    
    Returns:
        Latest exchange rate data
    """
    try:
        queries = PriceQueries(db)
        latest = queries.get_latest_exchange_rate(currency.upper())
        
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exchange rate data found for currency: {currency}"
            )
        
        return ExchangeRateResponse(
            date=latest.date,
            base_currency=latest.base_currency,
            quote_currency=latest.quote_currency,
            rate=latest.rate,
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
            detail=f"Error retrieving latest exchange rate: {str(e)}"
        )


@router.get("/exchange_rates/{currency}/performance", response_model=CurrencyPerformanceResponse)
async def get_currency_performance(
    currency: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """
    Calculate currency performance over a period.
    
    Args:
        currency: Currency code (e.g., EUR, GBP, JPY)
        start_date: Start date for analysis
        end_date: End date for analysis
    
    Returns:
        Performance metrics
    """
    try:
        analysis = PriceAnalysis(db)
        performance = analysis.calculate_currency_performance(
            currency.upper(),
            start_date,
            end_date
        )
        
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data available for performance analysis: {currency}"
            )
        
        return CurrencyPerformanceResponse(**performance)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating performance: {str(e)}"
        )


@router.get("/currencies", response_model=AvailableItemsResponse)
async def list_currencies(db: Session = Depends(get_db)):
    """
    List all available currencies.
    
    Returns:
        List of available currency codes
    """
    try:
        analysis = PriceAnalysis(db)
        currencies = analysis.get_available_currencies()
        
        return AvailableItemsResponse(
            items=currencies,
            count=len(currencies)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing currencies: {str(e)}"
        )
