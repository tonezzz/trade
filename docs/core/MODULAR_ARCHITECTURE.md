---

**Last Updated:** 2026-08-11
# Modular Architecture Documentation

## Overview

The trade service has been refactored to follow a modular architecture pattern with clear separation of concerns. This document describes the new structure and how components interact.

## Architecture Layers

The system is now organized into distinct layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
├──────────────────┬──────────────────┬──────────────────────────┤
│   CLI Tool       │   REST API       │   WebSocket              │
│   (cli.py)       │   (FastAPI)      │   (Real-time)           │
└──────────────────┴──────────────────┴──────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer                                  │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Routes         │   Schemas        │   Main App               │
│   (Endpoints)     │   (Pydantic)     │   (FastAPI Config)       │
└──────────────────┴──────────────────┴──────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Business Logic │   Data Logic     │   Orchestration          │
│   (Services)      │   (Transform)    │   (Workflows)            │
└──────────────────┴──────────────────┴──────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Repository Layer                              │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Data Access    │   Query Logic    │   ORM Abstraction        │
│   (Repositories)  │   (Filters)      │   (SQLAlchemy)           │
└──────────────────┴──────────────────┴──────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Configuration Layer                            │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Settings       │   API Config     │   Data Sources Config    │
│   (Environment)  │   (Server)       │   (Automation)           │
└──────────────────┴──────────────────┴──────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer                               │
├──────────────────┬──────────────────┬──────────────────────────┤
│   PostgreSQL     │   Models         │   Session Management      │
│   (Data Store)   │   (ORM)          │   (Connection Pool)      │
└──────────────────┴──────────────────┴──────────────────────────┘
```

## Directory Structure

```
trade/
├── src/
│   ├── api/                    # API Layer
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app initialization
│   │   ├── routes/             # API route modules
│   │   │   ├── __init__.py
│   │   │   ├── exchange_rates.py
│   │   │   ├── commodities.py
│   │   │   ├── dollar_index.py
│   │   │   ├── signals.py
│   │   │   ├── backtesting.py
│   │   │   ├── health.py
│   │   │   └── websocket.py
│   │   └── schemas/            # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── common.py
│   │       ├── exchange_rates.py
│   │       ├── commodities.py
│   │       ├── dollar_index.py
│   │       ├── signals.py
│   │       └── backtesting.py
│   ├── services/               # Service Layer
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── exchange_rate_service.py
│   │   ├── commodity_service.py
│   │   ├── signal_service.py
│   │   ├── backtesting_service.py
│   │   ├── data_import_service.py
│   │   └── data_quality_service.py
│   ├── repositories/           # Repository Layer
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── exchange_rate_repository.py
│   │   ├── commodity_repository.py
│   │   ├── dollar_index_repository.py
│   │   ├── signal_repository.py
│   │   └── backtest_repository.py
│   ├── config/                 # Configuration Layer
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── database_config.py
│   │   ├── api_config.py
│   │   └── data_sources_config.py
│   ├── models.py               # Database models (unchanged)
│   ├── database.py             # Database connection (refactored)
│   ├── queries.py              # Query functions (unchanged)
│   ├── importer.py             # Data import (unchanged)
│   ├── validators.py           # Data validation (unchanged)
│   ├── backtesting.py          # Backtesting engine (unchanged)
│   ├── signals.py              # Signal generation (unchanged)
│   ├── scheduler.py            # Job scheduler (unchanged)
│   ├── health.py               # Health checks (unchanged)
│   ├── data_quality.py         # Data quality (unchanged)
│   ├── websocket_manager.py     # WebSocket (unchanged)
│   ├── visualization.py        # Visualization (unchanged)
│   ├── notifications.py        # Notifications (unchanged)
│   └── logging_config.py       # Logging (unchanged)
├── config/                     # Configuration files (unchanged)
│   ├── api.yml
│   ├── data_sources.yml
│   ├── infrastructure.yml
│   ├── signals.yml
│   └── backtesting.yml
├── scripts/                    # Scripts (unchanged)
├── tests/                      # Tests (unchanged)
├── cli.py                      # CLI (unchanged)
└── requirements.txt            # Dependencies (unchanged)
```

## Component Descriptions

### API Layer (`src/api/`)

**Purpose**: Handle HTTP requests and responses, provide REST API interface.

**Components**:
- **main.py**: FastAPI application initialization, middleware configuration, lifespan management
- **routes/**: Individual route modules for different endpoints
  - Each route module handles a specific domain (exchange rates, commodities, etc.)
  - Uses dependency injection for database sessions
  - Implements request validation and error handling
- **schemas/**: Pydantic models for request/response validation
  - Common schemas (ErrorResponse, SuccessResponse, etc.)
  - Domain-specific schemas for each endpoint

**Key Changes**:
- Split monolithic `api.py` (2,135 lines) into focused modules
- Separated route logic from business logic
- Centralized schema definitions
- Improved error handling and validation

### Service Layer (`src/services/`)

**Purpose**: Implement business logic, orchestrate data operations, provide reusable functionality.

**Components**:
- **base_service.py**: Common service functionality (logging, error handling, pagination)
- **domain services**: Business logic for specific domains
  - Exchange rate operations
  - Commodity operations
  - Signal generation and analysis
  - Backtesting operations
  - Data import operations
  - Data quality monitoring

**Key Benefits**:
- Centralized business logic
- Reusable across different interfaces (CLI, API, WebSocket)
- Easier testing and mocking
- Consistent error handling and logging

### Repository Layer (`src/repositories/`)

**Purpose**: Abstract data access, provide clean interface to database operations.

**Components**:
- **base_repository.py**: Common repository patterns (CRUD, filtering, pagination)
- **domain repositories**: Data access for specific models
  - Exchange rate repository
  - Commodity repository
  - Dollar index repository
  - Signal repository
  - Backtest repository

**Key Benefits**:
- Abstracted database access
- Easier to swap database implementations
- Better testability with mock repositories
- Consistent data access patterns

### Configuration Layer (`src/config/`)

**Purpose**: Centralized configuration management with type safety.

**Components**:
- **settings.py**: Application settings using environment variables
- **database_config.py**: Database connection configuration
- **api_config.py**: API server configuration from YAML
- **data_sources_config.py**: Data sources configuration from YAML

**Key Benefits**:
- Type-safe configuration
- Environment variable support
- Centralized configuration management
- Easy to override for different environments

## Data Flow

### Request Flow (API)

```
1. HTTP Request → API Route
2. Route validates request (Pydantic schemas)
3. Route calls Service Layer
4. Service Layer applies business logic
5. Service Layer calls Repository Layer
6. Repository Layer executes database queries
7. Results flow back through layers
8. Response formatted and returned
```

### Data Import Flow

```
1. Download Script → Data Import Service
2. Service validates data (Validators)
3. Service transforms data (Formatters)
4. Service calls Repository Layer
5. Repository Layer persists to database
6. Service returns import results
```

### Signal Generation Flow

```
1. Signal Service receives request
2. Service retrieves historical data (Repository)
3. Service calculates technical indicators
4. Service generates trading signals
5. Service stores signal history (Repository)
6. Service returns signal data
```

## Migration Guide

### For API Consumers

**Old Import**:
```python
from src.api import app
```

**New Import**:
```python
from src.api.main import create_app
app = create_app()
```

**Endpoint Changes**:
- All endpoints now prefixed with `/api/v1/`
- Response schemas remain compatible
- Error response format standardized

### For Developers

**Accessing Business Logic**:
```python
# Old: Direct API calls
from src.api import app

# New: Use service layer
from src.services import ExchangeRateService
from src.database import get_db

db = next(get_db())
service = ExchangeRateService(db)
result = service.get_exchange_rates("EUR")
```

**Accessing Data**:
```python
# Old: Direct database queries
from src.queries import PriceQueries

# New: Use repository layer
from src.repositories import ExchangeRateRepository
from src.database import get_db

db = next(get_db())
repo = ExchangeRateRepository(db)
result = repo.get_by_currency("EUR")
```

**Configuration**:
```python
# Old: Environment variables directly
import os
db_host = os.getenv('DB_HOST')

# New: Type-safe settings
from src.config import get_settings
settings = get_settings()
db_host = settings.db_host
```

## Benefits of Modular Architecture

### Maintainability
- **Focused Modules**: Each module has a single, well-defined responsibility
- **Easier Navigation**: Clear directory structure makes finding code easier
- **Reduced Coupling**: Layers interact through well-defined interfaces

### Testability
- **Isolated Testing**: Each layer can be tested independently
- **Mocking**: Easy to mock dependencies for unit tests
- **Integration Testing**: Clear testing boundaries between layers

### Scalability
- **Horizontal Scaling**: Service layer can be extracted to microservices
- **Performance**: Repository layer can be optimized independently
- **Caching**: Service layer can implement caching strategies

### Extensibility
- **New Features**: Add new routes, services, or repositories without affecting existing code
- **Data Sources**: Add new data sources through repository pattern
- **API Versions**: Easy to version API endpoints

## Health Check Improvements

### Enhanced Data Gap Detection
The health check system has been enhanced with type-specific data gap detection:

- **Type-Specific Tolerance**: Uses tolerance settings from `config/data_sources.yml`
  - THB: 2 days tolerance
  - Currencies: 7 days tolerance  
  - DXY: 30 days tolerance
  - Commodities: 90 days tolerance

- **Gap Severity Levels**:
  - **Critical**: Gaps > 2x tolerance (e.g., THB gap > 4 days)
  - **Warning**: Gaps > tolerance (e.g., THB gap > 2 days)
  - **Info**: Gaps within tolerance but worth noting

- **PostgreSQL Compatibility**: Health checks now support both SQLite and PostgreSQL databases

- **Recent Data Focus**: Gap detection focuses on recent 30 days to identify current issues rather than historical gaps

### Health Check Features
- Database connection and table validation
- Type-specific data freshness monitoring
- Data volume and quality checks
- System resource monitoring
- Data gap detection with severity levels
- Configuration-driven tolerance settings

## Future Improvements

### Short-term
1. **Async Operations**: Convert synchronous operations to async where appropriate
2. **Caching Layer**: Add Redis or in-memory caching for frequently accessed data
3. **Event System**: Implement event-driven architecture for decoupling

### Long-term
1. **Microservices**: Extract service layer to independent services
2. **Message Queue**: Add message queue for async processing
3. **API Gateway**: Implement API gateway for routing and rate limiting

## Backward Compatibility

The refactoring maintains backward compatibility where possible:

- **CLI Tool**: Unchanged, continues to work as before
- **Database Schema**: No changes to database structure
- **Existing APIs**: Response formats remain compatible
- **Configuration**: Existing YAML files continue to work

**Breaking Changes**:
- API endpoint paths now include `/api/v1/` prefix
- Import statements for API module have changed
- Some internal APIs have changed (not public facing)

## Performance Considerations

### Potential Performance Improvements
- **Reduced Import Time**: Modular imports load only what's needed
- **Better Caching**: Service layer can implement intelligent caching
- **Database Optimization**: Repository layer can optimize queries

### Monitoring
- **Layer-Specific Metrics**: Each layer can have specific performance metrics
- **Request Tracing**: Clear request flow through layers for debugging
- **Error Tracking**: Centralized error handling improves monitoring

## Security Considerations

### Improved Security
- **Input Validation**: Pydantic schemas provide consistent validation
- **Configuration Management**: Centralized configuration reduces security risks
- **Access Control**: Service layer can implement authorization logic

### Best Practices
- **SQL Injection Prevention**: Repository layer uses parameterized queries
- **Secrets Management**: Configuration layer handles secrets properly
- **Error Messages**: Sanitized error messages prevent information leakage

## Conclusion

The modular architecture provides a solid foundation for future development while maintaining the functionality of the existing system. The clear separation of concerns makes the codebase more maintainable, testable, and scalable.

For questions or issues with the new architecture, please refer to the team documentation or create an issue in the project repository.
