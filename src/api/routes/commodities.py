"""
Commodity prices API routes.
"""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.queries import PriceQueries
from src.api.schemas import (
    CommodityPriceResponse,
    CommodityPriceListResponse,
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


@router.get("/commodity_prices", response_model=CommodityPriceListResponse)
async def get_commodity_prices(
    commodity: Optional[str] = Query(None, description="Commodity name (e.g., GOLD, OIL)"),
    symbol: Optional[str] = Query(None, description="Trading symbol (e.g., XAUUSD, USOIL)"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    period: Optional[str] = Query(None, description="Period (1d, 1w, 1m, 3m, 6m, 1y, 5y)"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get commodity prices.
    
    Args:
        commodity: Commodity name (e.g., GOLD, OIL)
        symbol: Trading symbol (e.g., XAUUSD, USOIL)
        start_date: Start date for filtering
        end_date: End date for filtering
        period: Period string (alternative to start/end dates)
        limit: Maximum number of results to return
        offset: Number of results to skip
    
    Returns:
        List of commodity price data
    """
    try:
        # Handle period parameter
        if period:
            start_date, end_date = parse_period(period)
        
        queries = PriceQueries(db)
        df = queries.get_commodity_prices(commodity, symbol, start_date, end_date)
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No commodity price data found for the specified criteria"
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
        commodity_prices = [
            CommodityPriceResponse(
                date=row['date'],
                commodity=row['commodity'],
                symbol=row.get('symbol'),
                price=row['price'],
                unit=row.get('unit'),
                open=row.get('open'),
                high=row.get('high'),
                low=row.get('low'),
                close=row.get('close'),
                volume=row.get('volume')
            )
            for row in paginated_data
        ]
        
        return CommodityPriceListResponse(
            data=commodity_prices,
            count=len(data_list),
            commodity=commodity.upper() if commodity else None,
            symbol=symbol.upper() if symbol else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving commodity prices: {str(e)}"
        )


@router.get("/commodity_prices/latest", response_model=CommodityPriceResponse)
async def get_latest_commodity_price(
    commodity: Optional[str] = Query(None, description="Commodity name (e.g., GOLD, OIL)"),
    symbol: Optional[str] = Query(None, description="Trading symbol (e.g., XAUUSD, USOIL)"),
    db: Session = Depends(get_db)
):
    """
    Get the latest commodity price.
    
    Args:
        commodity: Commodity name (e.g., GOLD, OIL)
        symbol: Trading symbol (e.g., XAUUSD, USOIL)
    
    Returns:
        Latest commodity price data
    """
    try:
        if not commodity and not symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either commodity or symbol must be specified"
            )
        
        queries = PriceQueries(db)
        latest = queries.get_latest_commodity_price(commodity, symbol)
        
        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No commodity price data found for the specified criteria"
            )
        
        return CommodityPriceResponse(
            date=latest.date,
            commodity=latest.commodity,
            symbol=latest.symbol,
            price=latest.price,
            unit=latest.unit,
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
            detail=f"Error retrieving latest commodity price: {str(e)}"
        )


@router.get("/commodities", response_model=AvailableItemsResponse)
async def list_commodities(db: Session = Depends(get_db)):
    """
    List all available commodities.
    
    Returns:
        List of available commodity names
    """
    try:
        from src.queries import PriceAnalysis
        analysis = PriceAnalysis(db)
        commodities = analysis.get_available_commodities()
        
        return AvailableItemsResponse(
            items=commodities,
            count=len(commodities)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing commodities: {str(e)}"
        )
