# Code Conventions

**Category:** best-practices  
**Last Updated:** 2026-08-05
**Related Files:** src/, AGENTS.md  
**Tags:** conventions, style, python

## Context

Project-specific code conventions that go beyond standard PEP 8 guidelines.

## Conventions

### 1. Database Queries

- Always use parameterized queries to prevent SQL injection
- Include query timeout settings
- Log slow queries (>1s) for performance monitoring

### 2. Error Handling

- Don't over-wrap in try/catch - handle at appropriate boundaries
- Include context in error messages
- Use specific exception types, not generic Exception

### 3. Configuration

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate configuration at startup

### 4. Testing

- Write failing tests first for bug fixes
- Test edge cases and error conditions
- Keep tests independent and fast

## When to Use

Follow these conventions when:
- Writing new code
- Refactoring existing code
- Reviewing pull requests

## Related Knowledge

- [AGENTS.md](../../AGENTS.md) - Sub-agent usage conventions
- [Global Rules](~/.codeium/windsurf/memories/global_rules.md) - General development guidelines

---

**Last Updated:** 2026-08-05