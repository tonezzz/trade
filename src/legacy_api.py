"""
FastAPI backend for trading infrastructure.
Provides REST endpoints for dollar price data types.
"""
from datetime import datetime, timezone, date, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import pandas as pd

from src.database import get_db
from src.queries import PriceQueries, PriceAnalysis
from src.validators import DataValidator, ValidationError
from src.health import HealthChecker
from src.data_quality import DataQualityReporter
from src.models import ExchangeRate, DollarIndex, CommodityPrice, BacktestResult, BacktestTrade, BacktestEquity, SignalHistory, SignalPerformance
from src.backtesting import (
    BacktestEngine, BacktestConfig, get_strategy, list_strategies,
    ParameterOptimizer, WalkForwardAnalysis, StrategyComparator, PerformanceReport
)
from src.websocket_manager import get_websocket_manager, get_data_streamer, get_websocket_config
from src.signals import SignalGenerator, SignalHistory as SignalHistoryTracker, Backtester, SignalAlertSystem, validate_data_quality


# Pydantic models for request/response
class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SuccessResponse(BaseModel):
    """Standard success response model."""
    success: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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


class PerformanceResponse(BaseModel):
    """Performance analysis response."""
    currency: Optional[str] = None
    start_date: date
    end_date: date
    start_rate: Optional[float] = None
    end_rate: Optional[float] = None
    start_value: Optional[float] = None
    end_value: Optional[float] = None
    change: float
    change_percent: float
    high: float
    low: float
    range: float


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


class SignalResponse(BaseModel):
    """Trading signal response."""
    signal_type: str
    strength: str
    confidence: float
    timestamp: str
    price: float
    indicators: Dict[str, Any]
    reasons: List[str]
    timeframe: str
    validation: Optional[Dict[str, Any]] = None


class SignalHistoryResponse(BaseModel):
    """Signal history response."""
    id: int
    asset_type: str
    asset_symbol: str
    signal_type: str
    strength: str
    confidence: float
    timestamp: str
    price: float
    indicators: Dict[str, Any]
    reasons: List[str]
    timeframe: Optional[str] = None


class ChartDataResponse(BaseModel):
    """Chart data response for UI consumption."""
    data: List[Dict[str, Any]]
    count: int
    last_updated: str
    symbol: str
    timeframe: str


class ChartDataPoint(BaseModel):
    """Single chart data point."""
    time: int  # Unix timestamp
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


class SignalPerformanceResponse(BaseModel):
    """Signal performance metrics response."""
    asset_type: str
    asset_symbol: str
    timeframe: str
    test_start_date: date
    test_end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    max_drawdown: float
    total_trades: int
    win_rate: float
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    profit_factor: Optional[float] = None
    sharpe_ratio: Optional[float] = None


class BacktestRequest(BaseModel):
    """Backtest request model."""
    asset_type: str
    asset_symbol: str
    start_date: date
    end_date: date
    initial_capital: float = 10000.0
    commission: float = 0.001
    timeframe: str = "1d"


class BacktestResponse(BaseModel):
    """Backtest response model."""
    backtest_id: str
    strategy_name: str
    symbol: str
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    largest_win: Optional[float] = None
    largest_loss: Optional[float] = None
    avg_trade_duration: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    equity_curve: List[Dict[str, Any]] = []
    trades: List[Dict[str, Any]] = []


class StrategiesResponse(BaseModel):
    """Available strategies response model."""
    strategies: List[str]
    count: int


class OptimizeRequest(BaseModel):
    """Optimization request model."""
    asset_type: str
    asset_symbol: str
    start_date: date
    end_date: date
    initial_capital: float = 10000.0
    commission: float = 0.001
    timeframe: str = "1d"
    parameters: Dict[str, Any] = {}


class CompareRequest(BaseModel):
    """Strategy comparison request model."""
    asset_type: str
    asset_symbol: str
    start_date: date
    end_date: date
    initial_capital: float = 10000.0
    commission: float = 0.001
    strategies: List[str] = []


class OptimizeResponse(BaseModel):
    """Optimization response model."""
    best_parameters: Dict[str, Any]
    best_sharpe: float
    all_results: List[Dict[str, Any]]


class IndicatorResponse(BaseModel):
    """Technical indicator response model."""
    symbol: str
    indicator: str
    data: List[Dict[str, Any]]


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    print("Starting FastAPI application...")
    # Start WebSocket data streaming
    streamer = get_data_streamer()
    await streamer.start()
    print("WebSocket data streaming started")
    yield
    # Shutdown
    print("Shutting down FastAPI application...")
    # Stop WebSocket data streaming
    await streamer.stop()
    print("WebSocket data streaming stopped")


# Create FastAPI application
import os
root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(
    title="Trading Data API",
    description="REST API for dollar price data including exchange rates, dollar index, and commodity prices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    root_path=root_path
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility functions
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


def apply_pagination(data: List, limit: Optional[int], offset: int = 0) -> Dict[str, Any]:
    """Apply pagination to data list."""
    if limit is not None and limit > 0:
        paginated_data = data[offset:offset + limit]
        has_more = len(data) > offset + limit
    else:
        paginated_data = data[offset:]
        has_more = False

    return {
        'data': paginated_data,
        'count': len(data),
        'limit': limit,
        'offset': offset,
        'has_more': has_more
    }


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Trading Data API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
        "websocket_status": "/ws/status",
        "endpoints": {
            "exchange_rates": "/api/exchange_rates/{currency}",
            "dollar_index": "/api/dollar_index",
            "commodity_prices": "/api/commodity_prices/{commodity}",
            "ws_exchange_rates": "/ws/exchange_rates/{currency}",
            "ws_dollar_index": "/ws/dollar_index",
            "ws_commodity_prices": "/ws/commodity_prices/{commodity}"
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def get_health():
    """System health check endpoint."""
    try:
        checker = HealthChecker()
        results = checker.run_all_checks()
        return HealthResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/api/data_quality", response_model=DataQualityResponse)
async def get_data_quality():
    """Data quality report endpoint."""
    try:
        reporter = DataQualityReporter()
        report = reporter.generate_report()
        return DataQualityResponse(**report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data quality report failed: {str(e)}"
        )


@app.get("/api/available/currencies", response_model=AvailableItemsResponse)
async def get_available_currencies(db: Session = Depends(get_db)):
    """List available currencies."""
    try:
        currencies = db.query(ExchangeRate.quote_currency).distinct().all()
        items = [c[0] for c in currencies if c[0]]
        return AvailableItemsResponse(items=sorted(items), count=len(items))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve currencies: {str(e)}"
        )


@app.get("/api/available/commodities", response_model=AvailableItemsResponse)
async def get_available_commodities(db: Session = Depends(get_db)):
    """List available commodities."""
    try:
        commodities = db.query(CommodityPrice.commodity).distinct().all()
        items = [c[0] for c in commodities if c[0]]
        return AvailableItemsResponse(items=sorted(items), count=len(items))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve commodities: {str(e)}"
        )


@app.get("/api/exchange_rates/{currency}", response_model=PaginatedResponse)
async def get_exchange_rates(
    currency: str,
    period: Optional[str] = Query(None, description="Time period: 1d, 1w, 1m, 3m, 6m, 1y, 5y"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get exchange rate data for a specific currency."""
    try:
        # Validate currency
        validated_currency = DataValidator.validate_currency_code(currency)

        # Parse dates
        if period and (start_date or end_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both 'period' and 'start_date'/'end_date'"
            )

        if period:
            start_dt, end_dt = parse_period(period)
        else:
            start_dt = DataValidator.validate_date(start_date) if start_date else None
            end_dt = DataValidator.validate_date(end_date) if end_date else None

        # Query data
        queries = PriceQueries(db)
        df = queries.get_exchange_rates(validated_currency, start_dt, end_dt)

        if df.empty:
            return PaginatedResponse(
                data=[],
                count=0,
                limit=limit,
                offset=offset,
                has_more=False
            )

        # Convert to response models
        data = [
            ExchangeRateResponse(
                date=row['date'],
                base_currency='USD',
                quote_currency=validated_currency,
                rate=row['rate'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row.get('volume')
            )
            for _, row in df.iterrows()
        ]

        # Apply pagination
        paginated = apply_pagination(data, limit, offset)

        return PaginatedResponse(**paginated)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve exchange rates: {str(e)}"
        )


@app.get("/api/ui/chart-data/{symbol}", response_model=ChartDataResponse)
async def get_ui_chart_data(
    symbol: str,
    timeframe: str = Query("1y", description="Time period: 1d, 1w, 1m, 3m, 6m, 1y, all"),
    db: Session = Depends(get_db)
):
    """Get chart data formatted for UI consumption (Lightweight Charts format)."""
    try:
        # Determine data type based on symbol
        if symbol.upper() in ['THB', 'EUR', 'GBP', 'JPY', 'CAD', 'CHF', 'AUD', 'NZD']:
            # Currency data
            validated_currency = DataValidator.validate_currency_code(symbol)
            start_dt, end_dt = parse_period(timeframe) if timeframe != 'all' else (None, None)

            queries = PriceQueries(db)
            df = queries.get_exchange_rates(validated_currency, start_dt, end_dt)

            if df.empty:
                return ChartDataResponse(
                    data=[],
                    count=0,
                    last_updated=datetime.now().isoformat(),
                    symbol=symbol.upper(),
                    timeframe=timeframe
                )

            # Convert to chart format
            chart_data = []
            for _, row in df.iterrows():
                chart_data.append({
                    "time": int(datetime.combine(row['date'], datetime.min.time()).timestamp()),
                    "open": float(row['open'] if pd.notna(row['open']) else row['rate']),
                    "high": float(row['high'] if pd.notna(row['high']) else row['rate']),
                    "low": float(row['low'] if pd.notna(row['low']) else row['rate']),
                    "close": float(row['close'] if pd.notna(row['close']) else row['rate']),
                    "volume": float(row['volume']) if pd.notna(row['volume']) else None
                })

            # Get last updated date
            last_updated = df['date'].max() if not df.empty else datetime.now()
            if isinstance(last_updated, date):
                last_updated = datetime.combine(last_updated, datetime.min.time())

        elif symbol.upper() in ['GOLD', 'SILVER', 'OIL', 'WTI', 'BRENT', 'COPPER', 'NATURAL_GAS', 'WHEAT', 'CORN']:
            # Commodity data
            commodity = symbol.upper()
            start_dt, end_dt = parse_period(timeframe) if timeframe != 'all' else (None, None)

            queries = PriceQueries(db)
            df = queries.get_commodity_prices(commodity, start_dt, end_dt)

            if df.empty:
                return ChartDataResponse(
                    data=[],
                    count=0,
                    last_updated=datetime.now().isoformat(),
                    symbol=commodity,
                    timeframe=timeframe
                )

            # Convert to chart format
            chart_data = []
            for _, row in df.iterrows():
                chart_data.append({
                    "time": int(datetime.combine(row['date'], datetime.min.time()).timestamp()),
                    "open": float(row['open_price'] if pd.notna(row['open_price']) else row['price']),
                    "high": float(row['high_price'] if pd.notna(row['high_price']) else row['price']),
                    "low": float(row['low_price'] if pd.notna(row['low_price']) else row['price']),
                    "close": float(row['close_price'] if pd.notna(row['close_price']) else row['price']),
                    "volume": float(row['volume']) if pd.notna(row['volume']) else None
                })

            # Get last updated date
            last_updated = df['date'].max() if not df.empty else datetime.now()
            if isinstance(last_updated, date):
                last_updated = datetime.combine(last_updated, datetime.min.time())

        elif symbol.upper() == 'DXY' or symbol.upper() == 'DOLLAR_INDEX':
            # Dollar index data
            start_dt, end_dt = parse_period(timeframe) if timeframe != 'all' else (None, None)

            queries = PriceQueries(db)
            df = queries.get_dollar_index(start_dt, end_dt)

            if df.empty:
                return ChartDataResponse(
                    data=[],
                    count=0,
                    last_updated=datetime.now().isoformat(),
                    symbol='DXY',
                    timeframe=timeframe
                )

            # Convert to chart format
            chart_data = []
            for _, row in df.iterrows():
                chart_data.append({
                    "time": int(datetime.combine(row['date'], datetime.min.time()).timestamp()),
                    "open": float(row['open_price'] if pd.notna(row['open_price']) else row['value']),
                    "high": float(row['high_price'] if pd.notna(row['high_price']) else row['value']),
                    "low": float(row['low_price'] if pd.notna(row['low_price']) else row['value']),
                    "close": float(row['close_price'] if pd.notna(row['close_price']) else row['value']),
                    "volume": float(row['volume']) if pd.notna(row['volume']) else None
                })

            # Get last updated date
            last_updated = df['date'].max() if not df.empty else datetime.now()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown symbol: {symbol}. Supported: currencies (THB, EUR, etc.), commodities (GOLD, OIL, etc.), DXY"
            )

        # Ensure last_updated is a datetime
        if isinstance(last_updated, date):
            last_updated = datetime.combine(last_updated, datetime.min.time())

        return ChartDataResponse(
            data=chart_data,
            count=len(chart_data),
            last_updated=last_updated.isoformat() if hasattr(last_updated, 'isoformat') else str(last_updated),
            symbol=symbol.upper(),
            timeframe=timeframe
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chart data: {str(e)}"
        )


@app.get("/api/exchange_rates/{currency}/latest", response_model=ExchangeRateResponse)
async def get_latest_exchange_rate(currency: str, db: Session = Depends(get_db)):
    """Get the latest exchange rate for a currency."""
    try:
        validated_currency = DataValidator.validate_currency_code(currency)

        queries = PriceQueries(db)
        latest = queries.get_latest_exchange_rate(validated_currency)

        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exchange rate data found for currency: {validated_currency}"
            )

        return ExchangeRateResponse(
            date=latest.date,
            base_currency=latest.base_currency,
            quote_currency=latest.quote_currency,
            rate=latest.rate,
            open=latest.open_price if latest.open_price is not None else latest.rate,
            high=latest.high_price if latest.high_price is not None else latest.rate,
            low=latest.low_price if latest.low_price is not None else latest.rate,
            close=latest.close_price if latest.close_price is not None else latest.rate,
            volume=latest.volume
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest exchange rate: {str(e)}"
        )


@app.get("/api/dollar_index", response_model=PaginatedResponse)
async def get_dollar_index(
    period: Optional[str] = Query(None, description="Time period: 1d, 1w, 1m, 3m, 6m, 1y, 5y"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get Dollar Index (DXY) data."""
    try:
        # Parse dates
        if period and (start_date or end_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both 'period' and 'start_date'/'end_date'"
            )

        if period:
            start_dt, end_dt = parse_period(period)
        else:
            start_dt = DataValidator.validate_date(start_date) if start_date else None
            end_dt = DataValidator.validate_date(end_date) if end_date else None

        # Query data
        queries = PriceQueries(db)
        df = queries.get_dollar_index(start_dt, end_dt)

        if df.empty:
            return PaginatedResponse(
                data=[],
                count=0,
                limit=limit,
                offset=offset,
                has_more=False
            )

        # Convert to response models
        data = [
            DollarIndexResponse(
                date=row['date'],
                value=row['value'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row.get('volume')
            )
            for _, row in df.iterrows()
        ]

        # Apply pagination
        paginated = apply_pagination(data, limit, offset)

        return PaginatedResponse(**paginated)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dollar index data: {str(e)}"
        )


@app.get("/api/dollar_index/latest", response_model=DollarIndexResponse)
async def get_latest_dollar_index(db: Session = Depends(get_db)):
    """Get the latest Dollar Index value."""
    try:
        queries = PriceQueries(db)
        latest = queries.get_latest_dollar_index()

        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No dollar index data found"
            )

        return DollarIndexResponse(
            date=latest.date,
            value=latest.value,
            open=latest.open_price if latest.open_price is not None else latest.value,
            high=latest.high_price if latest.high_price is not None else latest.value,
            low=latest.low_price if latest.low_price is not None else latest.value,
            close=latest.close_price if latest.close_price is not None else latest.value,
            volume=latest.volume
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest dollar index: {str(e)}"
        )


@app.get("/api/commodity_prices/{commodity}", response_model=PaginatedResponse)
async def get_commodity_prices(
    commodity: str,
    period: Optional[str] = Query(None, description="Time period: 1d, 1w, 1m, 3m, 6m, 1y, 5y"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get commodity price data."""
    try:
        # Validate commodity
        validated_commodity = DataValidator.validate_commodity(commodity)

        # Parse dates
        if period and (start_date or end_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both 'period' and 'start_date'/'end_date'"
            )

        if period:
            start_dt, end_dt = parse_period(period)
        else:
            start_dt = DataValidator.validate_date(start_date) if start_date else None
            end_dt = DataValidator.validate_date(end_date) if end_date else None

        # Query data
        queries = PriceQueries(db)
        df = queries.get_commodity_prices(commodity=validated_commodity, start_date=start_dt, end_date=end_dt)

        if df.empty:
            return PaginatedResponse(
                data=[],
                count=0,
                limit=limit,
                offset=offset,
                has_more=False
            )

        # Convert to response models
        data = [
            CommodityPriceResponse(
                date=row['date'],
                commodity=row['commodity'],
                symbol=row.get('symbol'),
                price=row['price'],
                unit=row.get('unit'),
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row.get('volume')
            )
            for _, row in df.iterrows()
        ]

        # Apply pagination
        paginated = apply_pagination(data, limit, offset)

        return PaginatedResponse(**paginated)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve commodity prices: {str(e)}"
        )


@app.get("/api/commodity_prices/{commodity}/latest", response_model=CommodityPriceResponse)
async def get_latest_commodity_price(commodity: str, db: Session = Depends(get_db)):
    """Get the latest commodity price."""
    try:
        validated_commodity = DataValidator.validate_commodity(commodity)

        queries = PriceQueries(db)
        latest = queries.get_latest_commodity_price(commodity=validated_commodity)

        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No commodity price data found for: {validated_commodity}"
            )

        return CommodityPriceResponse(
            date=latest.date,
            commodity=latest.commodity,
            symbol=latest.symbol,
            price=latest.price,
            unit=latest.unit,
            open=latest.open_price if latest.open_price is not None else latest.price,
            high=latest.high_price if latest.high_price is not None else latest.price,
            low=latest.low_price if latest.low_price is not None else latest.price,
            close=latest.close_price if latest.close_price is not None else latest.price,
            volume=latest.volume
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest commodity price: {str(e)}"
        )


@app.get("/api/performance/{currency}", response_model=PerformanceResponse)
async def get_performance(
    currency: str,
    period: Optional[str] = Query(None, description="Time period: 1d, 1w, 1m, 3m, 6m, 1y, 5y"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """Get performance analysis for a currency."""
    try:
        validated_currency = DataValidator.validate_currency_code(currency)

        # Parse dates
        if period and (start_date or end_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both 'period' and 'start_date'/'end_date'"
            )

        if period:
            start_dt, end_dt = parse_period(period)
        else:
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Must specify both 'start_date' and 'end_date' when not using 'period'"
                )
            start_dt = DataValidator.validate_date(start_date)
            end_dt = DataValidator.validate_date(end_date)

        # Calculate performance
        analysis = PriceAnalysis(db)
        performance = analysis.calculate_currency_performance(validated_currency, start_dt, end_dt)

        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No performance data found for currency: {validated_currency}"
            )

        return PerformanceResponse(**performance)

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate performance: {str(e)}"
        )


# Signal API Endpoints

@app.get("/api/signals/{currency}", response_model=SignalResponse)
async def get_currency_signal(
    currency: str,
    timeframe: str = Query("1d", description="Timeframe for analysis (1d, 1w, 1m)"),
    db: Session = Depends(get_db)
):
    """
    Get current trading signal for a currency.

    Args:
        currency: Currency code (e.g., EUR, GBP, JPY)
        timeframe: Timeframe for analysis
        db: Database session

    Returns:
        Current trading signal with indicators
    """
    try:
        # Validate currency
        validated_currency = DataValidator.validate_currency_code(currency)

        # Get historical data
        queries = PriceQueries(db)
        df = queries.get_exchange_rates(validated_currency)

        if df.empty or len(df) < 50:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insufficient data for currency: {validated_currency}"
            )

        # Prepare data for signal generation
        df = df.set_index('date')
        if 'close' not in df.columns and 'rate' in df.columns:
            df['close'] = df['rate']
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 1.0

        # Generate signal
        generator = SignalGenerator()
        signal = generator.generate_signal(df, timeframe)

        # Validate signal
        validation = generator.validate_signal(signal)

        # Save signal to history
        history_tracker = SignalHistoryTracker(db)
        history_tracker.save_signal(signal, 'currency', validated_currency)

        response = SignalResponse(
            signal_type=signal.signal_type.value,
            strength=signal.strength.value,
            confidence=signal.confidence,
            timestamp=signal.timestamp.isoformat(),
            price=signal.price,
            indicators=signal.indicators,
            reasons=signal.reasons,
            timeframe=signal.timeframe,
            validation=validation
        )

        return response

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate signal: {str(e)}"
        )


@app.get("/api/signals/dollar_index", response_model=SignalResponse)
async def get_dollar_index_signal(
    timeframe: str = Query("1d", description="Timeframe for analysis (1d, 1w, 1m)"),
    db: Session = Depends(get_db)
):
    """
    Get current trading signal for Dollar Index (DXY).

    Args:
        timeframe: Timeframe for analysis
        db: Database session

    Returns:
        Current trading signal with indicators
    """
    try:
        # Get historical data
        queries = PriceQueries(db)
        df = queries.get_dollar_index()

        if df.empty or len(df) < 50:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insufficient data for Dollar Index"
            )

        # Prepare data for signal generation
        df = df.set_index('date')
        if 'close' not in df.columns and 'value' in df.columns:
            df['close'] = df['value']
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 1.0

        # Generate signal
        generator = SignalGenerator()
        signal = generator.generate_signal(df, timeframe)

        # Validate signal
        validation = generator.validate_signal(signal)

        # Save signal to history
        history_tracker = SignalHistoryTracker(db)
        history_tracker.save_signal(signal, 'dollar_index', 'DXY')

        response = SignalResponse(
            signal_type=signal.signal_type.value,
            strength=signal.strength.value,
            confidence=signal.confidence,
            timestamp=signal.timestamp.isoformat(),
            price=signal.price,
            indicators=signal.indicators,
            reasons=signal.reasons,
            timeframe=signal.timeframe,
            validation=validation
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DXY signal: {str(e)}"
        )


@app.get("/api/signals/commodity/{commodity}", response_model=SignalResponse)
async def get_commodity_signal(
    commodity: str,
    timeframe: str = Query("1d", description="Timeframe for analysis (1d, 1w, 1m)"),
    db: Session = Depends(get_db)
):
    """
    Get current trading signal for a commodity.

    Args:
        commodity: Commodity name or symbol (e.g., GOLD, XAU, OIL)
        timeframe: Timeframe for analysis
        db: Database session

    Returns:
        Current trading signal with indicators
    """
    try:
        # Get historical data
        queries = PriceQueries(db)
        df = queries.get_commodity_prices(commodity=commodity.upper())

        if df.empty:
            # Try by symbol
            df = queries.get_commodity_prices(symbol=commodity.upper())

        if df.empty or len(df) < 50:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insufficient data for commodity: {commodity}"
            )

        # Prepare data for signal generation
        df = df.set_index('date')
        if 'close' not in df.columns and 'price' in df.columns:
            df['close'] = df['price']
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 1.0

        # Generate signal
        generator = SignalGenerator()
        signal = generator.generate_signal(df, timeframe)

        # Validate signal
        validation = generator.validate_signal(signal)

        # Save signal to history
        history_tracker = SignalHistoryTracker(db)
        symbol = df['symbol'].iloc[-1] if 'symbol' in df.columns else commodity.upper()
        history_tracker.save_signal(signal, 'commodity', symbol)

        response = SignalResponse(
            signal_type=signal.signal_type.value,
            strength=signal.strength.value,
            confidence=signal.confidence,
            timestamp=signal.timestamp.isoformat(),
            price=signal.price,
            indicators=signal.indicators,
            reasons=signal.reasons,
            timeframe=signal.timeframe,
            validation=validation
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate commodity signal: {str(e)}"
        )


@app.get("/api/signals/history", response_model=List[SignalHistoryResponse])
async def get_signal_history(
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    asset_symbol: Optional[str] = Query(None, description="Filter by asset symbol"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of signals"),
    db: Session = Depends(get_db)
):
    """
    Get signal history.

    Args:
        asset_type: Filter by asset type (currency, commodity, dollar_index)
        asset_symbol: Filter by asset symbol
        limit: Maximum number of signals to return
        db: Database session

    Returns:
        List of historical signals
    """
    try:
        history_tracker = SignalHistoryTracker(db)
        signals = history_tracker.get_recent_signals(
            asset_type=asset_type,
            asset_symbol=asset_symbol,
            limit=limit
        )

        return [SignalHistoryResponse(**s) for s in signals]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve signal history: {str(e)}"
        )


@app.post("/api/signals/backtest", response_model=Dict[str, Any])
async def run_signal_backtest(
    request: BacktestRequest,
    db: Session = Depends(get_db)
):
    """
    Run backtest on historical data using signal generation.

    Args:
        request: Backtest request parameters
        db: Database session

    Returns:
        Backtest results
    """
    try:
        # Get historical data based on asset type
        queries = PriceQueries(db)

        if request.asset_type == 'currency':
            df = queries.get_exchange_rates(request.asset_symbol, request.start_date, request.end_date)
        elif request.asset_type == 'dollar_index':
            df = queries.get_dollar_index(request.start_date, request.end_date)
        elif request.asset_type == 'commodity':
            df = queries.get_commodity_prices(commodity=request.asset_symbol,
                                             start_date=request.start_date,
                                             end_date=request.end_date)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid asset type: {request.asset_type}"
            )

        if df.empty or len(df) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data for backtesting (minimum 100 data points required)"
            )

        # Prepare data
        df = df.set_index('date')
        if 'close' not in df.columns:
            df['close'] = df.get('rate', df.get('price', df.get('value')))
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 1.0

        # Run backtest
        generator = SignalGenerator()
        backtester = Backtester(generator)
        results = backtester.run_backtest(
            df,
            initial_capital=request.initial_capital,
            commission=request.commission
        )

        # Save performance to database
        if 'error' not in results:
            try:
                perf_entry = SignalPerformance(
                    asset_type=request.asset_type,
                    asset_symbol=request.asset_symbol,
                    timeframe=request.timeframe,
                    test_start_date=request.start_date,
                    test_end_date=request.end_date,
                    initial_capital=request.initial_capital,
                    final_capital=results['final_capital'],
                    total_return=results['total_return'],
                    max_drawdown=results['max_drawdown'],
                    total_trades=results['total_trades'],
                    win_rate=results['win_rate']
                )
                db.add(perf_entry)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error saving backtest results: {e}")

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backtest failed: {str(e)}"
        )


@app.get("/api/signals/performance", response_model=List[SignalPerformanceResponse])
async def get_signal_performance(
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    asset_symbol: Optional[str] = Query(None, description="Filter by asset symbol"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Get signal performance metrics from backtests.

    Args:
        asset_type: Filter by asset type
        asset_symbol: Filter by asset symbol
        limit: Maximum number of results
        db: Database session

    Returns:
        List of performance metrics
    """
    try:
        query = db.query(SignalPerformance)

        if asset_type:
            query = query.filter(SignalPerformance.asset_type == asset_type)
        if asset_symbol:
            query = query.filter(SignalPerformance.asset_symbol == asset_symbol)

        results = query.order_by(
            SignalPerformance.test_end_date.desc()
        ).limit(limit).all()

        return [SignalPerformanceResponse(
            asset_type=r.asset_type,
            asset_symbol=r.asset_symbol,
            timeframe=r.timeframe,
            test_start_date=r.test_start_date,
            test_end_date=r.test_end_date,
            initial_capital=r.initial_capital,
            final_capital=r.final_capital,
            total_return=r.total_return,
            max_drawdown=r.max_drawdown,
            total_trades=r.total_trades,
            win_rate=r.win_rate,
            avg_win=r.avg_win,
            avg_loss=r.avg_loss,
            profit_factor=r.profit_factor,
            sharpe_ratio=r.sharpe_ratio
        ) for r in results]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance metrics: {str(e)}"
        )


@app.get("/api/signals/indicators/{currency}")
async def get_currency_indicators(
    currency: str,
    db: Session = Depends(get_db)
):
    """
    Get all technical indicators for a currency without generating a signal.

    Args:
        currency: Currency code
        db: Database session

    Returns:
        Dictionary of all calculated indicators
    """
    try:
        validated_currency = DataValidator.validate_currency_code(currency)

        queries = PriceQueries(db)
        df = queries.get_exchange_rates(validated_currency)

        if df.empty or len(df) < 50:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insufficient data for currency: {validated_currency}"
            )

        # Prepare data
        df = df.set_index('date')
        if 'close' not in df.columns and 'rate' in df.columns:
            df['close'] = df['rate']
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 1.0

        # Calculate indicators
        generator = SignalGenerator()
        indicators = generator.calculate_all_indicators(df)

        # Return only the latest values
        latest_indicators = {}
        for key, series in indicators.items():
            if isinstance(series, pd.Series):
                latest_indicators[key] = float(series.iloc[-1])
            elif isinstance(series, list):
                latest_indicators[key] = series
            else:
                latest_indicators[key] = series

        return {
            'currency': validated_currency,
            'timestamp': datetime.now().isoformat(),
            'indicators': latest_indicators
        }

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate indicators: {str(e)}"
        )


# Backtesting Endpoints

@app.post("/api/backtest/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest, db: Session = Depends(get_db)):
    """
    Run a backtest for a trading strategy.

    Args:
        request: Backtest configuration
        db: Database session

    Returns:
        Backtest results with performance metrics
    """
    try:
        # Validate dates
        start_dt = DataValidator.validate_date(request.start_date)
        end_dt = DataValidator.validate_date(request.end_date)

        # Determine data type based on symbol
        symbol = request.symbol.upper()

        # Get historical data
        queries = PriceQueries(db)

        # Try to get as exchange rate first
        if len(symbol) == 3:
            data = queries.get_exchange_rates(symbol, start_dt, end_dt)
            if not data.empty:
                data = data.rename(columns={'rate': 'close'})
        else:
            data = pd.DataFrame()

        # Try as commodity
        if data.empty:
            data = queries.get_commodity_prices(symbol=symbol, start_date=start_dt, end_date=end_dt)
            if not data.empty:
                data = data.rename(columns={'price': 'close'})

        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for symbol: {symbol}"
            )

        # Ensure required columns
        required_cols = ['date', 'open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in data.columns:
                if col == 'open' and 'close' in data.columns:
                    data['open'] = data['close']
                elif col == 'high' and 'close' in data.columns:
                    data['high'] = data['close']
                elif col == 'low' and 'close' in data.columns:
                    data['low'] = data['close']

        # Create backtest configuration
        config = BacktestConfig(
            initial_capital=request.initial_capital,
            commission_rate=request.commission_rate,
            slippage_rate=request.slippage_rate,
            stop_loss_pct=request.stop_loss_pct,
            take_profit_pct=request.take_profit_pct
        )

        # Create engine and set data
        engine = BacktestEngine(config)
        engine.set_data(data)

        # Get strategy
        strategy = get_strategy(request.strategy_name, request.parameters)
        engine.set_strategy(strategy)

        # Run backtest
        result = engine.run()

        # Save to database
        backtest_result = BacktestResult(
            backtest_id=result['backtest_id'],
            strategy_name=result['strategy_name'],
            symbol=symbol,
            start_date=start_dt,
            end_date=end_dt,
            initial_capital=result['initial_capital'],
            final_capital=result['final_capital'],
            total_return=result['metrics']['total_return'],
            total_return_pct=result['metrics']['total_return_pct'],
            sharpe_ratio=result['metrics']['sharpe_ratio'],
            sortino_ratio=result['metrics']['sortino_ratio'],
            max_drawdown=result['metrics']['max_drawdown'],
            max_drawdown_pct=result['metrics']['max_drawdown_pct'],
            win_rate=result['metrics']['win_rate'],
            profit_factor=result['metrics']['profit_factor'],
            total_trades=result['metrics']['total_trades'],
            winning_trades=result['metrics']['winning_trades'],
            losing_trades=result['metrics']['losing_trades'],
            avg_win=result['metrics']['avg_win'],
            avg_loss=result['metrics']['avg_loss'],
            largest_win=result['metrics']['largest_win'],
            largest_loss=result['metrics']['largest_loss'],
            avg_trade_duration=result['metrics']['avg_trade_duration'],
            parameters=json.dumps(result.get('parameters', {}))
        )
        db.add(backtest_result)
        db.commit()

        # Save trades
        for trade in result['trades']:
            backtest_trade = BacktestTrade(
                backtest_id=result['backtest_id'],
                symbol=symbol,
                entry_date=trade.entry_date,
                exit_date=trade.exit_date,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                quantity=trade.quantity,
                direction=trade.direction,
                entry_value=trade.entry_value,
                exit_value=trade.exit_value,
                pnl=trade.pnl,
                pnl_pct=trade.pnl_pct,
                commission=trade.commission,
                slippage=trade.slippage,
                exit_reason=trade.exit_reason,
                duration_days=(trade.exit_date - trade.entry_date).days if trade.exit_date else None
            )
            db.add(backtest_trade)
        db.commit()

        # Save equity curve
        for equity_point in result['equity_curve']:
            backtest_equity = BacktestEquity(
                backtest_id=result['backtest_id'],
                date=equity_point['date'],
                equity=equity_point['equity'],
                returns=equity_point.get('returns'),
                drawdown=equity_point.get('drawdown'),
                drawdown_pct=equity_point.get('drawdown_pct'),
                peak_equity=equity_point.get('peak_equity'),
                position=equity_point.get('position_value')
            )
            db.add(backtest_equity)
        db.commit()

        # Format response
        trades_data = []
        for trade in result['trades']:
            trades_data.append({
                'entry_date': str(trade.entry_date),
                'exit_date': str(trade.exit_date) if trade.exit_date else None,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'direction': trade.direction,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnl_pct,
                'exit_reason': trade.exit_reason
            })

        return BacktestResponse(
            backtest_id=result['backtest_id'],
            strategy_name=result['strategy_name'],
            symbol=symbol,
            start_date=result['start_date'],
            end_date=result['end_date'],
            initial_capital=result['initial_capital'],
            final_capital=result['final_capital'],
            total_return=result['metrics']['total_return'],
            total_return_pct=result['metrics']['total_return_pct'],
            sharpe_ratio=result['metrics']['sharpe_ratio'],
            sortino_ratio=result['metrics']['sortino_ratio'],
            max_drawdown=result['metrics']['max_drawdown'],
            max_drawdown_pct=result['metrics']['max_drawdown_pct'],
            win_rate=result['metrics']['win_rate'],
            profit_factor=result['metrics']['profit_factor'],
            total_trades=result['metrics']['total_trades'],
            winning_trades=result['metrics']['winning_trades'],
            losing_trades=result['metrics']['losing_trades'],
            avg_win=result['metrics']['avg_win'],
            avg_loss=result['metrics']['avg_loss'],
            largest_win=result['metrics']['largest_win'],
            largest_loss=result['metrics']['largest_loss'],
            avg_trade_duration=result['metrics']['avg_trade_duration'],
            parameters=result.get('parameters'),
            equity_curve=result['equity_curve'],
            trades=trades_data
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run backtest: {str(e)}"
        )


@app.get("/api/backtest/results/{backtest_id}", response_model=BacktestResponse)
async def get_backtest_results(backtest_id: str, db: Session = Depends(get_db)):
    """
    Get backtest results by ID.

    Args:
        backtest_id: Backtest ID
        db: Database session

    Returns:
        Backtest results
    """
    try:
        # Get backtest result
        result = db.query(BacktestResult).filter(
            BacktestResult.backtest_id == backtest_id
        ).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backtest not found: {backtest_id}"
            )

        # Get trades
        trades = db.query(BacktestTrade).filter(
            BacktestTrade.backtest_id == backtest_id
        ).all()

        trades_data = []
        for trade in trades:
            trades_data.append({
                'entry_date': str(trade.entry_date),
                'exit_date': str(trade.exit_date) if trade.exit_date else None,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'direction': trade.direction,
                'pnl': trade.pnl,
                'pnl_pct': trade.pnl_pct,
                'exit_reason': trade.exit_reason
            })

        # Get equity curve
        equity = db.query(BacktestEquity).filter(
            BacktestEquity.backtest_id == backtest_id
        ).order_by(BacktestEquity.date).all()

        equity_curve = []
        for eq in equity:
            equity_curve.append({
                'date': str(eq.date),
                'equity': eq.equity,
                'returns': eq.returns,
                'drawdown': eq.drawdown,
                'drawdown_pct': eq.drawdown_pct,
                'peak_equity': eq.peak_equity,
                'position': eq.position
            })

        return BacktestResponse(
            backtest_id=result.backtest_id,
            strategy_name=result.strategy_name,
            symbol=result.symbol,
            start_date=str(result.start_date),
            end_date=str(result.end_date),
            initial_capital=result.initial_capital,
            final_capital=result.final_capital,
            total_return=result.total_return,
            total_return_pct=result.total_return_pct,
            sharpe_ratio=result.sharpe_ratio or 0,
            sortino_ratio=result.sortino_ratio or 0,
            max_drawdown=result.max_drawdown,
            max_drawdown_pct=result.max_drawdown_pct,
            win_rate=result.win_rate,
            profit_factor=result.profit_factor or 0,
            total_trades=result.total_trades,
            winning_trades=result.winning_trades,
            losing_trades=result.losing_trades,
            avg_win=result.avg_win or 0,
            avg_loss=result.avg_loss or 0,
            largest_win=result.largest_win or 0,
            largest_loss=result.largest_loss or 0,
            avg_trade_duration=result.avg_trade_duration or 0,
            parameters=json.loads(result.parameters) if result.parameters else None,
            equity_curve=equity_curve,
            trades=trades_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve backtest results: {str(e)}"
        )


@app.get("/api/backtest/strategies", response_model=StrategiesResponse)
async def get_backtest_strategies():
    """
    List available backtesting strategies.

    Returns:
        List of available strategies with their parameters
    """
    try:
        strategies = list_strategies()
        strategy_infos = [
            StrategyInfo(
                name=s['name'],
                display_name=s['display_name'],
                parameters=s['parameters']
            )
            for s in strategies
        ]
        return StrategiesResponse(strategies=strategy_infos, count=len(strategy_infos))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve strategies: {str(e)}"
        )


@app.post("/api/backtest/optimize", response_model=OptimizeResponse)
async def optimize_strategy(request: OptimizeRequest, db: Session = Depends(get_db)):
    """
    Optimize strategy parameters.

    Args:
        request: Optimization configuration
        db: Database session

    Returns:
        Optimization results with best parameters
    """
    try:
        # Validate dates
        start_dt = DataValidator.validate_date(request.start_date)
        end_dt = DataValidator.validate_date(request.end_date)

        # Get historical data
        queries = PriceQueries(db)
        symbol = request.symbol.upper()

        if len(symbol) == 3:
            data = queries.get_exchange_rates(symbol, start_dt, end_dt)
            if not data.empty:
                data = data.rename(columns={'rate': 'close'})
        else:
            data = pd.DataFrame()

        if data.empty:
            data = queries.get_commodity_prices(symbol=symbol, start_date=start_dt, end_date=end_dt)
            if not data.empty:
                data = data.rename(columns={'price': 'close'})

        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for symbol: {symbol}"
            )

        # Ensure required columns
        for col in ['date', 'open', 'high', 'low', 'close']:
            if col not in data.columns:
                if col == 'open' and 'close' in data.columns:
                    data['open'] = data['close']
                elif col == 'high' and 'close' in data.columns:
                    data['high'] = data['close']
                elif col == 'low' and 'close' in data.columns:
                    data['low'] = data['close']

        # Create engine
        config = BacktestConfig()
        engine = BacktestEngine(config)

        # Create optimizer
        optimizer = ParameterOptimizer(engine, data)

        # Use provided param ranges or defaults
        if request.param_ranges:
            param_ranges = {}
            for param_name, range_config in request.param_ranges.items():
                param_ranges[param_name] = (range_config['min'], range_config['max'])
        else:
            from src.backtesting import WalkForwardAnalysis
            wfa = WalkForwardAnalysis(engine, data)
            param_ranges = wfa._get_param_ranges(request.strategy_name)

        if not param_ranges:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No parameter ranges defined for strategy: {request.strategy_name}"
            )

        # Run optimization
        if request.optimization_method == 'grid':
            # Convert ranges to discrete values for grid search
            param_grid = {}
            for param_name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    param_grid[param_name] = list(range(min_val, max_val + 1, max(1, (max_val - min_val) // 10)))
                else:
                    param_grid[param_name] = np.linspace(min_val, max_val, 10).tolist()

            result = optimizer.grid_search(request.strategy_name, param_grid, request.metric)
        else:
            result = optimizer.random_search(
                request.strategy_name,
                param_ranges,
                request.n_iterations,
                request.metric
            )

        return OptimizeResponse(
            best_parameters=result['best_parameters'],
            best_metrics=result['best_metrics'],
            all_results=result['all_results'],
            strategy_name=request.strategy_name
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize strategy: {str(e)}"
        )


@app.post("/api/backtest/compare")
async def compare_strategies(request: CompareRequest, db: Session = Depends(get_db)):
    """
    Compare multiple strategies on the same data.

    Args:
        request: Comparison configuration
        db: Database session

    Returns:
        Comparison results as DataFrame
    """
    try:
        # Validate dates
        start_dt = DataValidator.validate_date(request.start_date)
        end_dt = DataValidator.validate_date(request.end_date)

        # Get historical data
        queries = PriceQueries(db)
        symbol = request.symbol.upper()

        if len(symbol) == 3:
            data = queries.get_exchange_rates(symbol, start_dt, end_dt)
            if not data.empty:
                data = data.rename(columns={'rate': 'close'})
        else:
            data = pd.DataFrame()

        if data.empty:
            data = queries.get_commodity_prices(symbol=symbol, start_date=start_dt, end_date=end_dt)
            if not data.empty:
                data = data.rename(columns={'price': 'close'})

        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for symbol: {symbol}"
            )

        # Ensure required columns
        for col in ['date', 'open', 'high', 'low', 'close']:
            if col not in data.columns:
                if col == 'open' and 'close' in data.columns:
                    data['open'] = data['close']
                elif col == 'high' and 'close' in data.columns:
                    data['high'] = data['close']
                elif col == 'low' and 'close' in data.columns:
                    data['low'] = data['close']

        # Create comparator
        config = BacktestConfig(initial_capital=request.initial_capital)
        comparator = StrategyComparator(config)

        # Run comparison
        results_df = comparator.compare(data, request.strategies)

        # Convert to dict for JSON response
        return {
            'symbol': symbol,
            'start_date': str(start_dt),
            'end_date': str(end_dt),
            'comparison': results_df.to_dict(orient='records')
        }

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare strategies: {str(e)}"
        )


# WebSocket Endpoints

@app.websocket("/ws/exchange_rates/{currency}")
async def websocket_exchange_rates(websocket: WebSocket, currency: str):
    """
    WebSocket endpoint for live exchange rate updates.

    Subscribe to real-time exchange rate updates for a specific currency.

    Args:
        websocket: WebSocket connection
        currency: Currency code (e.g., EUR, GBP, JPY)
    """
    manager = get_websocket_manager()
    config = get_websocket_config()

    # Get client IP
    client_host = websocket.client.host if websocket.client else "unknown"

    try:
        # Validate currency
        validated_currency = DataValidator.validate_currency_code(currency)

        # Connect client
        client_id = await manager.connect(websocket, client_host)

        # Subscribe to data stream
        await manager.subscribe(client_id, 'exchange_rate', validated_currency)

        # Send initial data
        db = next(get_db())
        queries = PriceQueries(db)
        latest = queries.get_latest_exchange_rate(validated_currency)
        db.close()

        if latest:
            await manager.send_personal_message({
                'type': 'exchange_rate',
                'currency': validated_currency,
                'date': latest.date.isoformat(),
                'rate': latest.rate,
                'open': latest.open_price,
                'high': latest.high_price,
                'low': latest.low_price,
                'close': latest.close_price,
                'volume': latest.volume,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Connected to exchange rate stream'
            }, client_id)

        # Handle client messages
        while True:
            data = await websocket.receive_json()

            # Handle subscription changes
            if data.get('action') == 'unsubscribe':
                await manager.unsubscribe(client_id, 'exchange_rate', validated_currency)
                await manager.send_personal_message({
                    'type': 'info',
                    'message': f'Unsubscribed from {validated_currency}'
                }, client_id)
                break

            # Handle ping/pong
            elif data.get('action') == 'ping':
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, client_id)

    except ValidationError as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.error(f"WebSocket error for exchange rates: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(e))
    finally:
        await manager.disconnect(client_id)


@app.websocket("/ws/dollar_index")
async def websocket_dollar_index(websocket: WebSocket):
    """
    WebSocket endpoint for live Dollar Index (DXY) updates.

    Subscribe to real-time Dollar Index updates.

    Args:
        websocket: WebSocket connection
    """
    manager = get_websocket_manager()

    # Get client IP
    client_host = websocket.client.host if websocket.client else "unknown"

    try:
        # Connect client
        client_id = await manager.connect(websocket, client_host)

        # Subscribe to data stream
        await manager.subscribe(client_id, 'dollar_index', 'DXY')

        # Send initial data
        db = next(get_db())
        queries = PriceQueries(db)
        latest = queries.get_latest_dollar_index()
        db.close()

        if latest:
            await manager.send_personal_message({
                'type': 'dollar_index',
                'date': latest.date.isoformat(),
                'value': latest.value,
                'open': latest.open_price,
                'high': latest.high_price,
                'low': latest.low_price,
                'close': latest.close_price,
                'volume': latest.volume,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Connected to dollar index stream'
            }, client_id)

        # Handle client messages
        while True:
            data = await websocket.receive_json()

            # Handle subscription changes
            if data.get('action') == 'unsubscribe':
                await manager.unsubscribe(client_id, 'dollar_index', 'DXY')
                await manager.send_personal_message({
                    'type': 'info',
                    'message': 'Unsubscribed from dollar index'
                }, client_id)
                break

            # Handle ping/pong
            elif data.get('action') == 'ping':
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, client_id)

    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.error(f"WebSocket error for dollar index: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(e))
    finally:
        await manager.disconnect(client_id)


@app.websocket("/ws/commodity_prices/{commodity}")
async def websocket_commodity_prices(websocket: WebSocket, commodity: str):
    """
    WebSocket endpoint for live commodity price updates.

    Subscribe to real-time commodity price updates for a specific commodity.

    Args:
        websocket: WebSocket connection
        commodity: Commodity name (e.g., GOLD, SILVER, OIL)
    """
    manager = get_websocket_manager()

    # Get client IP
    client_host = websocket.client.host if websocket.client else "unknown"

    try:
        # Validate commodity (basic validation)
        validated_commodity = commodity.upper().strip()

        # Connect client
        client_id = await manager.connect(websocket, client_host)

        # Subscribe to data stream
        await manager.subscribe(client_id, 'commodity', validated_commodity)

        # Send initial data
        db = next(get_db())
        queries = PriceQueries(db)
        latest = queries.get_latest_commodity_price(commodity=validated_commodity)
        db.close()

        if latest:
            await manager.send_personal_message({
                'type': 'commodity',
                'commodity': latest.commodity,
                'symbol': latest.symbol,
                'date': latest.date.isoformat(),
                'price': latest.price,
                'unit': latest.unit,
                'open': latest.open_price,
                'high': latest.high_price,
                'low': latest.low_price,
                'close': latest.close_price,
                'volume': latest.volume,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': f'Connected to {validated_commodity} stream'
            }, client_id)

        # Handle client messages
        while True:
            data = await websocket.receive_json()

            # Handle subscription changes
            if data.get('action') == 'unsubscribe':
                await manager.unsubscribe(client_id, 'commodity', validated_commodity)
                await manager.send_personal_message({
                    'type': 'info',
                    'message': f'Unsubscribed from {validated_commodity}'
                }, client_id)
                break

            # Handle ping/pong
            elif data.get('action') == 'ping':
                await manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }, client_id)

    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.error(f"WebSocket error for commodity prices: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(e))
    finally:
        await manager.disconnect(client_id)


@app.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status and statistics.

    Returns:
        Dictionary with connection statistics
    """
    manager = get_websocket_manager()
    return {
        "active_connections": manager.get_connection_count(),
        "subscriptions": {
            "exchange_rates": {
                currency: manager.get_subscription_count('exchange_rate', currency)
                for currency in manager.subscriptions.get('exchange_rate', {}).keys()
            },
            "dollar_index": {
                "DXY": manager.get_subscription_count('dollar_index', 'DXY')
            },
            "commodities": {
                commodity: manager.get_subscription_count('commodity', commodity)
                for commodity in manager.subscriptions.get('commodity', {}).keys()
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
