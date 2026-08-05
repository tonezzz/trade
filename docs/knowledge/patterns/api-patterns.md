# API Patterns

**Category:** patterns  
**Last Updated:** 2026-08-05
**Related Files:** src/api/, core/API_GUIDE.md  
**Tags:** api, fastapi, rest, patterns

## Context

This document captures reusable API patterns used throughout the trade system.

## Patterns

### 1. Standard Response Format

All API endpoints follow a consistent response structure:

```python
{
    "status": "success|error",
    "data": {...},  # On success
    "error": {...}  # On error
}
```

### 2. Pagination Pattern

List endpoints use cursor-based pagination:

```python
{
    "items": [...],
    "next_cursor": "string",
    "has_more": boolean
}
```

### 3. Error Handling Pattern

Errors include context and actionable information:

```python
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "details": {...},
        "suggestion": "How to fix"
    }
}
```

## When to Use

Use these patterns when:
- Creating new API endpoints
- Modifying existing endpoint responses
- Designing error handling

## Related Knowledge

- [API Guide](../../core/API_GUIDE.md) - Complete API reference
- [Best Practices: API Design](../best-practices/api-design.md)

---

**Last Updated:** 2026-08-05