"""
Pydantic schemas for exchange rate endpoints.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ExchangeRateResponse(BaseModel):
    """Exchange rate data response."""
    date: date
    base_currency: str
    quote_currency: str
    rate: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None

    class Config:
        from_attributes = True


class ExchangeRateListResponse(BaseModel):
    """List of exchange rates response."""
    data: list[ExchangeRateResponse]
    count: int
    currency: str


class CurrencyPerformanceResponse(BaseModel):
    """Currency performance analysis response."""
    currency: str
    start_date: date
    end_date: date
    start_rate: Optional[float] = None
    end_rate: Optional[float] = None
    change: float
    change_percent: float
    high: float
    low: float
    range: float
