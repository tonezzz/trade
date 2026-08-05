# Recurring Patterns

**Purpose**: Document recurring patterns, solutions, and approaches that can be reused across the project.

**Last Updated**: 2026-08-04

---

## Template for New Patterns

```markdown
### [Pattern Name]
**Category**: database|api|ui|automation|testing|documentation
**Frequency**: High/Medium/Low
**Complexity**: Simple/Medium/Complex

**Context**:
When this pattern is applicable...

**Solution**:
The pattern implementation...

**Examples**:
- Example 1
- Example 2

**Related Files**:
- path/to/file1.py
- path/to/file2.md

**Related Skills**:
- skill-name
```

---

## Database Patterns

### Parameterized Queries
**Category**: database
**Frequency**: High
**Complexity**: Simple

**Context**:
Any database query that includes user input or dynamic values.

**Solution**:
Always use parameterized queries to prevent SQL injection and ensure proper escaping.

**Examples**:
```python
# Good - Parameterized query
cursor.execute(
    "SELECT * FROM exchange_rates WHERE date = %s AND currency = %s",
    (date_value, currency)
)

# Bad - String concatenation (vulnerable to SQL injection)
cursor.execute(
    f"SELECT * FROM exchange_rates WHERE date = '{date_value}' AND currency = '{currency}'"
)
```

**Related Files**:
- docs/knowledge/best-practices/code-conventions.md
- src/db.py

**Related Skills**:
- trade-verify

---

### Time-Series Query Optimization
**Category**: database
**Frequency**: High
**Complexity**: Medium

**Context**:
Queries that filter by date ranges on time-series data.

**Solution**:
Use date indexes and optimize query patterns for time-series data.

**Examples**:
```python
# Optimized time-series query
SELECT * FROM exchange_rates 
WHERE date BETWEEN '2020-01-01' AND '2020-12-31'
AND currency = 'EUR'
ORDER BY date;

# Ensure date index exists
CREATE INDEX idx_exchange_rates_date ON exchange_rates(date);
```

**Related Files**:
- docs/core/DEPLOYMENT.md
- docs/core/ARCHITECTURE.md

---

## API Patterns

### Pydantic Models for Validation
**Category**: api
**Frequency**: High
**Complexity**: Simple

**Context**:
All API endpoints that accept request data or return response data.

**Solution**:
Use Pydantic models for request/response validation and automatic documentation.

**Examples**:
```python
from pydantic import BaseModel, Field
from datetime import date

class ExchangeRateRequest(BaseModel):
    currency: str = Field(..., description="Currency pair (e.g., EUR/USD)")
    start_date: date = Field(..., description="Start date for query")
    end_date: date = Field(..., description="End date for query")

class ExchangeRateResponse(BaseModel):
    date: date
    currency: str
    rate: float
    volume: Optional[float]

@app.post("/api/exchange-rates", response_model=List[ExchangeRateResponse])
def get_exchange_rates(request: ExchangeRateRequest):
    # Implementation
    pass
```

**Related Files**:
- docs/core/API_GUIDE.md
- src/api.py

---

### Error Handling with HTTP Exceptions
**Category**: api
**Frequency**: High
**Complexity**: Simple

**Context**:
All API endpoints that can encounter errors.

**Solution**:
Use FastAPI's HTTPException for consistent error responses.

**Examples**:
```python
from fastapi import HTTPException, status

@app.get("/api/exchange-rates/{currency}")
def get_exchange_rate(currency: str):
    if not is_valid_currency(currency):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid currency: {currency}"
        )
    
    data = fetch_exchange_rate(currency)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for currency: {currency}"
        )
    
    return data
```

**Related Files**:
- docs/core/API_GUIDE.md
- docs/core/TROUBLESHOOTING.md

---

### Pagination for Large Datasets
**Category**: api
**Frequency**: Medium
**Complexity**: Medium

**Context**:
API endpoints that return large datasets.

**Solution**:
Implement pagination with skip/limit parameters.

**Examples**:
```python
from pydantic import BaseModel

class PaginatedRequest(BaseModel):
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")

@app.get("/api/exchange-rates")
def get_exchange_rates_paginated(
    currency: str,
    skip: int = 0,
    limit: int = 100
):
    query = """
        SELECT * FROM exchange_rates 
        WHERE currency = %s
        ORDER BY date
        LIMIT %s OFFSET %s
    """
    results = execute_query(query, (currency, limit, skip))
    
    total = execute_query(
        "SELECT COUNT(*) FROM exchange_rates WHERE currency = %s",
        (currency,)
    )[0]['count']
    
    return {
        "data": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

**Related Files**:
- docs/core/API_GUIDE.md

---

## UI Patterns

### WebSocket Real-Time Updates
**Category**: ui
**Frequency**: Medium
**Complexity**: Medium

**Context**:
UIs that need real-time data updates.

**Solution**:
Use WebSocket connections for bi-directional real-time communication.

**Examples**:
```python
from fastapi import WebSocket

@app.websocket("/ws/real-time")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive client message
            data = await websocket.receive_text()
            
            # Process and send response
            result = process_real_time_data(data)
            await websocket.send_json(result)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
```

**Related Files**:
- docs/features/websocket/WEBSOCKET.md
- docs/features/websocket/WEBSOCKET_IMPLEMENTATION_SUMMARY.md

---

## Automation Patterns

### YAML Configuration
**Category**: automation
**Frequency**: High
**Complexity**: Simple

**Context**:
All automation jobs and scheduled tasks.

**Solution**:
Use YAML for structured, readable configuration.

**Examples**:
```yaml
# config/automation.yml
jobs:
  - name: download_wti_data
    schedule: "0 6 * * *"  # Daily at 6 AM
    source: eia
    type: commodity
    symbol: WTI
    retry_count: 3
    retry_delay: 300  # 5 minutes
    
  - name: download_ecb_data
    schedule: "0 8 * * *"  # Daily at 8 AM
    source: ecb
    type: exchange_rate
    currencies:
      - EUR/USD
      - GBP/USD
```

**Related Files**:
- CONFIGURATION_MANAGEMENT.md
- docs/features/automation/AUTOMATION_GUIDE.md

**Related Skills**:
- config-helper

---

### Exponential Backoff for Retries
**Category**: automation
**Frequency**: High
**Complexity**: Simple

**Context**:
Any operation that may fail and needs retry logic.

**Solution**:
Implement exponential backoff with jitter for retries.

**Examples**:
```python
import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s")
            time.sleep(delay)
```

**Related Files**:
- docs/features/automation/AUTOMATION_GUIDE.md

---

## Testing Patterns

### Fixture-Based Test Data
**Category**: testing
**Frequency**: High
**Complexity**: Simple

**Context**:
Tests that need consistent test data.

**Solution**:
Use pytest fixtures for test data setup and teardown.

**Examples**:
```python
import pytest
from datetime import date

@pytest.fixture
def sample_exchange_rate():
    return {
        "date": date(2020, 1, 1),
        "currency": "EUR/USD",
        "rate": 1.1234,
        "volume": 1000000
    }

@pytest.fixture
def database_connection():
    # Setup
    conn = create_test_database()
    
    yield conn
    
    # Teardown
    conn.close()

def test_exchange_rate_insert(sample_exchange_rate, database_connection):
    result = insert_exchange_rate(database_connection, sample_exchange_rate)
    assert result is True
```

**Related Files**:
- CONTRIBUTING.md
- tests/

---

### Test Isolation
**Category**: testing
**Frequency**: High
**Complexity**: Simple

**Context**:
All tests to ensure they don't interfere with each other.

**Solution**:
Use in-memory databases and clean up after each test.

**Examples**:
```python
@pytest.fixture(autouse=True)
def clean_database(database_connection):
    yield
    # Clean up after each test
    database_connection.execute("DELETE FROM exchange_rates")
    database_connection.execute("DELETE FROM dollar_index")
    database_connection.execute("DELETE FROM commodity_prices")
```

**Related Files**:
- CONTRIBUTING.md
- tests/

---

## Documentation Patterns

### Consistent Documentation Structure
**Category**: documentation
**Frequency**: High
**Complexity**: Simple

**Context**:
All documentation files.

**Solution**:
Follow consistent structure with Last Updated field.

**Examples**:
```markdown
# Document Title

**Last Updated:** YYYY-MM-DD

## Context
Brief description...

## Section 1
Content...

## Examples
Example code...

## Related Documentation
- [Related Doc](path/to/doc.md)

---
**Last Updated:** YYYY-MM-DD
```

**Related Files**:
- CONTRIBUTING.md
- docs/INDEX.md

---

### Cross-References
**Category**: documentation
**Frequency**: High
**Complexity**: Simple

**Context**:
Documentation that references other documentation.

**Solution**:
Always include cross-references to related documentation.

**Examples**:
```markdown
## Related Documentation
- [API Guide](core/API_GUIDE.md) - Complete API reference
- [Deployment Guide](core/DEPLOYMENT.md) - Deployment instructions
- [Troubleshooting](core/TROUBLESHOOTING.md) - Common issues
```

**Related Files**:
- docs/INDEX.md
- CONTRIBUTING.md

---

## Configuration Patterns

### Environment Variables for Secrets
**Category**: configuration
**Frequency**: High
**Complexity**: Simple

**Context**:
Any sensitive configuration (API keys, passwords, tokens).

**Solution**:
Use environment variables, never commit secrets to code.

**Examples**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")

# Validate required environment variables
required_vars = ["DATABASE_URL", "API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")
```

**Related Files**:
- docs/knowledge/best-practices/code-conventions.md
- .env.example
- CONFIGURATION_MANAGEMENT.md

**Related Skills**:
- config-helper

---

### YAML for Structured Configuration
**Category**: configuration
**Frequency**: High
**Complexity**: Simple

**Context**:
Complex configuration with nested structures.

**Solution**:
Use YAML for readability and maintainability.

**Examples**:
```yaml
# config/database.yml
database:
  host: localhost
  port: 5432
  name: trade_db
  user: trade_user
  # Password from environment variable
  password: ${DB_PASSWORD}
  
  pools:
    min_size: 5
    max_size: 20
    
  timeout:
    connection: 10
    query: 30
```

**Related Files**:
- CONFIGURATION_MANAGEMENT.md
- config/

**Related Skills**:
- config-helper

---

## Error Handling Patterns

### Contextual Error Messages
**Category**: error-handling
**Frequency**: High
**Complexity**: Simple

**Context**:
All error handling throughout the application.

**Solution**:
Include context in error messages for easier debugging.

**Examples**:
```python
# Good - Contextual error
try:
    result = fetch_exchange_rate(currency, date)
except DatabaseError as e:
    raise ValueError(
        f"Failed to fetch exchange rate for {currency} on {date}: {str(e)}"
    ) from e

# Bad - Generic error
try:
    result = fetch_exchange_rate(currency, date)
except Exception as e:
    raise ValueError("An error occurred")
```

**Related Files**:
- docs/knowledge/best-practices/code-conventions.md
- docs/core/TROUBLESHOOTING.md

---

### Specific Exception Types
**Category**: error-handling
**Frequency**: High
**Complexity**: Simple

**Context**:
All error handling throughout the application.

**Solution**:
Use specific exception types, not generic Exception.

**Examples**:
```python
# Good - Specific exceptions
try:
    result = database_query(query)
except psycopg2.OperationalError as e:
    # Handle database connection issues
    logger.error(f"Database connection failed: {e}")
    raise DatabaseConnectionError("Cannot connect to database") from e
except psycopg2.DataError as e:
    # Handle data issues
    logger.error(f"Data error in query: {e}")
    raise DataError("Invalid data in query") from e

# Bad - Generic exception
try:
    result = database_query(query)
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

**Related Files**:
- docs/knowledge/best-practices/code-conventions.md

---

## Future Patterns

*Add new patterns here as they are identified during development work.*

---

**Last Updated**: 2026-08-04