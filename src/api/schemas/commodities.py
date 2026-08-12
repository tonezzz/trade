"""
Pydantic schemas for commodity price endpoints.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class CommodityPriceResponse(BaseModel):
    """Commodity price data response."""
    date: date
    commodity: str
    symbol: Optional[str] = None
    price: float
    unit: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None

    class Config:
        from_attributes = True


class CommodityPriceListResponse(BaseModel):
    """List of commodity prices response."""
    data: list[CommodityPriceResponse]
    count: int
    commodity: Optional[str] = None
    symbol: Optional[str] = None
