"""
Pydantic schemas for dollar index endpoints.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class DollarIndexResponse(BaseModel):
    """Dollar Index data response."""
    date: date
    value: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None

    class Config:
        from_attributes = True


class DollarIndexPerformanceResponse(BaseModel):
    """Dollar Index performance analysis response."""
    start_date: date
    end_date: date
    start_value: Optional[float] = None
    end_value: Optional[float] = None
    change: float
    change_percent: float
    high: float
    low: float
    range: float
