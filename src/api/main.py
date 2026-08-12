"""
FastAPI application initialization and configuration.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml
import logging

from src.database import get_db
from src.health import HealthChecker
from src.data_quality import DataQualityReporter
from src.websocket_manager import get_websocket_manager, get_data_streamer, load_websocket_config
from .routes import (
    exchange_rates,
    commodities,
    dollar_index,
    signals,
    backtesting,
    health,
    websocket
)

logger = logging.getLogger(__name__)


def load_api_config():
    """Load API configuration from config/api.yml."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'api.yml')
    
    default_config = {
        'server': {
            'host': '0.0.0.0',
            'port': 9000,
            'workers': 1,
            'reload': False,
            'log_level': 'info'
        },
        'cors': {
            'enabled': True,
            'allow_origins': ['http://localhost:8080', 'http://127.0.0.1:8080'],
            'allow_credentials': True,
            'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With']
        },
        'docs': {
            'enabled': True,
            'docs_url': '/docs',
            'redoc_url': '/redoc',
            'openapi_url': '/openapi.json'
        }
    }
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            if config_data:
                # Merge with defaults
                for key, value in config_data.items():
                    if key in default_config and isinstance(default_config[key], dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        logger.info(f"Loaded API configuration from {config_path}")
    except Exception as e:
        logger.warning(f"Failed to load API configuration from {config_path}: {e}")
        logger.info("Using default API configuration")
    
    return default_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    logger.info("Starting FastAPI application...")
    
    # Load WebSocket configuration
    ws_config = load_websocket_config()
    app.state.ws_config = ws_config
    
    # Start WebSocket data streaming
    try:
        streamer = get_data_streamer()
        await streamer.start()
        logger.info("WebSocket data streaming started")
    except Exception as e:
        logger.error(f"Failed to start WebSocket data streaming: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    try:
        # Stop WebSocket data streaming
        streamer = get_data_streamer()
        await streamer.stop()
        logger.info("WebSocket data streaming stopped")
    except Exception as e:
        logger.error(f"Failed to stop WebSocket data streaming: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Load configuration
    api_config = load_api_config()
    server_config = api_config.get('server', {})
    cors_config = api_config.get('cors', {})
    docs_config = api_config.get('docs', {})
    
    # Get root path from environment
    root_path = os.getenv("ROOT_PATH", "")
    
    # Create FastAPI application
    app = FastAPI(
        title="Trading Data API",
        description="REST API for dollar price data including exchange rates, dollar index, and commodity prices",
        version="0.1.0",
        docs_url=docs_config.get('docs_url') if docs_config.get('enabled') else None,
        redoc_url=docs_config.get('redoc_url') if docs_config.get('enabled') else None,
        openapi_url=docs_config.get('openapi_url') if docs_config.get('enabled') else None,
        lifespan=lifespan,
        root_path=root_path
    )
    
    # Add CORS middleware
    if cors_config.get('enabled', True):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get('allow_origins', ['*']),
            allow_credentials=cors_config.get('allow_credentials', True),
            allow_methods=cors_config.get('allow_methods', ['*']),
            allow_headers=cors_config.get('allow_headers', ['*']),
        )
    
    # Include routers
    app.include_router(exchange_rates.router, prefix="/api/v1", tags=["exchange_rates"])
    app.include_router(commodities.router, prefix="/api/v1", tags=["commodities"])
    app.include_router(dollar_index.router, prefix="/api/v1", tags=["dollar_index"])
    app.include_router(signals.router, prefix="/api/v1", tags=["signals"])
    app.include_router(backtesting.router, prefix="/api/v1", tags=["backtesting"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Trading Data API",
            "version": "0.1.0",
            "docs": "/docs" if docs_config.get('enabled') else None
        }
    
    return app


# Create app instance for development
app = create_app()
