# Patterns

**Category:** patterns  
**Last Updated:** 2026-08-05
**Related Files:** [various project files]  
**Tags:** patterns, architecture, design, anti-patterns

## Purpose

This document captures architectural patterns, design patterns, and anti-patterns used in the trade system. These patterns represent proven approaches to common problems and serve as a guide for consistent implementation.

## Architectural Patterns

### Layered Architecture

**Pattern Description**
The system follows a classic layered architecture with clear separation of concerns:

```
┌─────────────────────────────────┐
│   Presentation Layer (API/UI)   │
├─────────────────────────────────┤
│   Business Logic Layer         │
├─────────────────────────────────┤
│   Data Access Layer            │
├─────────────────────────────────┤
│   Database Layer               │
└─────────────────────────────────┘
```

**Implementation**
- API Layer: FastAPI endpoints in `src/api/`
- Business Logic: Signal generation, backtesting in `src/models/`
- Data Access: Database operations in `src/database.py`
- Database: PostgreSQL with optimized schema

**Benefits**
- Clear separation of concerns
- Easy to test individual layers
- Can replace layers independently
- Follows single responsibility principle

**When to Use**
- Building new features
- Refactoring existing code
- Designing system architecture

### Event-Driven Architecture

**Pattern Description**
Components communicate through events for loose coupling and real-time updates:

```
┌─────────────┐    Event    ┌─────────────┐
│   Producer  │ ──────────> │  Consumer   │
└─────────────┘             └─────────────┘
       │                           │
       └─────────> Event Bus <────┘
```

**Implementation**
- WebSocket for real-time data streaming
- Signal generation triggers events
- UI components subscribe to relevant events
- Event handlers in `src/websocket.py`

**Benefits**
- Loose coupling between components
- Real-time updates
- Easy to add new consumers
- Scalable event distribution

**When to Use**
- Real-time data requirements
- Multiple consumers for same data
- Decoupled component communication

### Configuration-Driven Architecture

**Pattern Description**
System behavior is controlled through configuration rather than code changes:

```
┌─────────────┐    Config    ┌─────────────┐
│   Config    │ ──────────> │  System     │
│   Files     │             │  Behavior   │
└─────────────┘             └─────────────┘
```

**Implementation**
- Single Source of Truth in `config/`
- YAML configuration files
- Validation scripts for config integrity
- Environment-specific overrides

**Benefits**
- No code changes for behavior changes
- Easy to test different configurations
- Version-controlled configuration
- Clear configuration relationships

**When to Use**
- System behavior needs flexibility
- Multiple deployment environments
- Non-technical users need control

## Design Patterns

### Repository Pattern

**Pattern Description**
Mediates between the domain and data mapping layers, acting like an in-memory domain object collection.

**Implementation**
```python
class SignalRepository:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_by_id(self, signal_id: int) -> Signal:
        return self.db.query(Signal).filter(Signal.id == signal_id).first()
    
    def get_all(self, filters: dict) -> List[Signal]:
        query = self.db.query(Signal)
        # Apply filters
        return query.all()
```

**Benefits**
- Centralized data access logic
- Easy to mock for testing
- Consistent data access patterns
- Can switch data sources

**When to Use**
- Complex data access logic
- Need to test business logic independently
- Multiple data sources possible

### Factory Pattern

**Pattern Description**
Creates objects without specifying the exact class of object that will be created.

**Implementation**
```python
class SignalFactory:
    @staticmethod
    def create_signal(signal_type: str, params: dict) -> Signal:
        if signal_type == "rsi":
            return RSISignal(**params)
        elif signal_type == "macd":
            return MACDSignal(**params)
        else:
            raise ValueError(f"Unknown signal type: {signal_type}")
```

**Benefits**
- Loose coupling between code and objects
- Easy to add new signal types
- Centralized object creation logic
- Consistent object initialization

**When to Use**
- Multiple similar object types
- Runtime object creation decisions
- Need to hide object creation complexity

### Strategy Pattern

**Pattern Description**
Defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Implementation**
```python
class BacktestStrategy(ABC):
    @abstractmethod
    def execute(self, data: pd.DataFrame) -> BacktestResult:
        pass

class SimpleBacktest(BacktestStrategy):
    def execute(self, data: pd.DataFrame) -> BacktestResult:
        # Simple backtest logic
        pass

class WalkForwardBacktest(BacktestStrategy):
    def execute(self, data: pd.DataFrame) -> BacktestResult:
        # Walk-forward logic
        pass
```

**Benefits**
- Easy to add new algorithms
- Runtime algorithm selection
- Separates algorithm from context
- Testable in isolation

**When to Use**
- Multiple algorithms for same task
- Runtime algorithm selection
- Need to vary algorithm independently

### Observer Pattern

**Pattern Description**
Defines a one-to-many dependency so that when one object changes state, all dependents are notified.

**Implementation**
```python
class SignalObserver(ABC):
    @abstractmethod
    def on_signal(self, signal: Signal):
        pass

class WebSocketObserver(SignalObserver):
    def on_signal(self, signal: Signal):
        # Broadcast to WebSocket clients
        pass

class DatabaseObserver(SignalObserver):
    def on_signal(self, signal: Signal):
        # Store in database
        pass
```

**Benefits**
- Loose coupling between subject and observers
- Dynamic observer registration
- Easy to add new observers
- Broadcast communication

**When to Use**
- One-to-many relationships
- Need to notify multiple components
- Dynamic subscription management

### Dependency Injection

**Pattern Description**
Supplies dependencies to a class rather than the class creating them itself.

**Implementation**
```python
class SignalService:
    def __init__(
        self,
        signal_repo: SignalRepository,
        notification_service: NotificationService
    ):
        self.signal_repo = signal_repo
        self.notification_service = notification_service
    
    def generate_signal(self, params: dict) -> Signal:
        signal = self.signal_repo.create(params)
        self.notification_service.notify(signal)
        return signal
```

**Benefits**
- Easier testing (can inject mocks)
- Loose coupling between components
- Clear dependencies
- Flexible configuration

**When to Use**
- Classes with external dependencies
- Need to test in isolation
- Want to swap implementations

## Anti-Patterns to Avoid

### God Object

**Description**
A class that knows too much or does too much.

**Example to Avoid**
```python
# Bad: Single class doing everything
class TradeSystem:
    def generate_signals(self): ...
    def store_data(self): ...
    def serve_api(self): ...
    def send_notifications(self): ...
    def calculate_backtests(self): ...
```

**Solution**
Split into focused classes with single responsibilities.

### Shotgun Surgery

**Description**
Every time you make a change, you have to make many small changes to many different classes.

**Example to Avoid**
```python
# Bad: Scattered related logic
class API:
    def validate_rsi(self): ...
    
class Database:
    def validate_rsi(self): ...
    
class UI:
    def validate_rsi(self): ...
```

**Solution**
Consolidate related logic in a single place, use composition.

### Magic Numbers

**Description**
Using unnamed numerical constants in code.

**Example to Avoid**
```python
# Bad: Magic numbers
if rsi > 70:
    return "overbought"
```

**Solution**
Use named constants with clear meaning.

```python
# Good: Named constants
RSI_OVERBOUGHT_THRESHOLD = 70
if rsi > RSI_OVERBOUGHT_THRESHOLD:
    return "overbought"
```

### Premature Optimization

**Description**
Optimizing code before measuring performance.

**Example to Avoid**
```python
# Bad: Complex optimization without profiling
def complex_optimization(data):
    # Unnecessarily complex implementation
    ...
```

**Solution**
Profile first, optimize hot paths only, keep code simple.

### Error Swallowing

**Description**
Catching exceptions and not handling them properly.

**Example to Avoid**
```python
# Bad: Swallowing errors
try:
    risky_operation()
except:
    pass  # Silent failure
```

**Solution**
Handle errors appropriately or let them propagate.

```python
# Good: Proper error handling
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### Tight Coupling

**Description**
Components that depend heavily on each other's implementation details.

**Example to Avoid**
```python
# Bad: Tight coupling
class Service:
    def __init__(self):
        self.db = PostgreSQLDatabase(host="localhost", port=5432)
```

**Solution**
Use interfaces and dependency injection.

```python
# Good: Loose coupling
class Service:
    def __init__(self, db: DatabaseInterface):
        self.db = db
```

## Pattern Selection Guide

### When to Use Architectural Patterns

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| Layered | Clear separation needed, team familiar | Simple CRUD, rapid prototyping |
| Event-Driven | Real-time needs, loose coupling | Simple request/response |
| Config-Driven | Behavior flexibility needed | Fixed behavior, simple config |

### When to Use Design Patterns

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| Repository | Complex data access, testing needed | Simple CRUD, single data source |
| Factory | Multiple similar types, runtime creation | Single type, simple creation |
| Strategy | Multiple algorithms, runtime selection | Single algorithm, fixed behavior |
| Observer | One-to-many notifications | Simple one-to-one |
| DI | External dependencies, testing needed | No dependencies, simple classes |

## Adding New Patterns

When you identify a reusable pattern:

1. Document the pattern with context
2. Provide implementation example
3. List benefits and use cases
4. Add related patterns
5. Include anti-patterns if relevant
6. Update this document

## Related Knowledge

- [API Patterns](api-patterns.md) - Specific API patterns
- [Best Practices](../best-practices/best-practices.md) - Project best practices
- [Lessons Learned](../lessons/lessons-learned.md) - Insights from development
- [Architecture](../../core/ARCHITECTURE.md) - System architecture

---

**Last Updated:** 2026-08-05
**Maintainer:** trade documentation team