"""
Common Pydantic schemas for API responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Standard success response model."""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """Paginated data response."""
    data: List[Any]
    count: int
    limit: Optional[int] = None
    offset: Optional[int] = None
    has_more: bool


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    checks: Dict[str, bool]
    issues: List[str]
    warnings: List[str]


class DataQualityResponse(BaseModel):
    """Data quality report response."""
    timestamp: str
    summary: Dict[str, Any]
    tables: Dict[str, Any]
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]


class AvailableItemsResponse(BaseModel):
    """Available currencies/commodities response."""
    items: List[str]
    count: int
