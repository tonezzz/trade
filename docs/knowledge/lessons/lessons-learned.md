# Lessons Learned

**Category:** lessons  
**Last Updated:** 2026-08-05
**Related Files:** [various project files]  
**Tags:** lessons, insights, development

## Purpose

This document captures lessons learned during the development and operation of the trade system. Each entry represents a problem encountered, the solution implemented, and insights that can help avoid similar issues in the future.

## Lesson Entry Template

When adding a new lesson, use this format:

```markdown
### [Lesson Title]

**Date:** YYYY-MM-DD  
**Context:** [What was the situation?]  
**Problem:** [What went wrong or what challenge was faced?]  
**Solution:** [How was it resolved?]  
**Outcome:** [What was the result?]  
**Lessons for Future:** [What should we do differently?]  
**Related Files:** [file paths]  
**Tags:** [tags]
```

## Lessons Learned

### Database Connection Pooling

**Date:** 2026-08-04  
**Context:** Initial API development with FastAPI and PostgreSQL  
**Problem:** Database connections were being created and closed for each request, causing performance issues and connection exhaustion under load.  
**Solution:** Implemented connection pooling using SQLAlchemy's pool with appropriate pool size and overflow settings.  
**Outcome:** Reduced connection overhead by 70%, improved API response times, eliminated connection exhaustion issues.  
**Lessons for Future:** Always use connection pooling for database-backed APIs. Configure pool size based on expected concurrency, not just available connections.  
**Related Files:** src/database.py, config/database.yml  
**Tags:** database, performance, api

### Configuration Management

**Date:** 2026-08-04  
**Context:** Multiple configuration files across the project with inconsistent formats  
**Problem:** Configuration changes required updating multiple files, leading to inconsistencies and deployment errors.  
**Solution:** Implemented Single Source of Truth (SSOT) approach with config/ directory and validation scripts.  
**Outcome:** Centralized configuration, reduced errors, easier onboarding for new developers.  
**Lessons for Future:** Establish SSOT early in project. Use configuration validation to catch errors before deployment. Document configuration relationships clearly.  
**Related Files:** config/, CONFIGURATION_MANAGEMENT.md  
**Tags:** configuration, ssot, deployment

### WebSocket State Management

**Date:** 2026-08-04  
**Context:** Real-time data streaming via WebSocket for trading signals  
**Problem:** WebSocket connections were accumulating state without proper cleanup, causing memory leaks.  
**Solution:** Implemented connection lifecycle management with explicit disconnect handlers and state cleanup.  
**Outcome:** Eliminated memory leaks, stable long-running connections, predictable resource usage.  
**Lessons for Future:** Always implement cleanup handlers for stateful connections. Monitor connection counts and memory usage. Test long-running scenarios.  
**Related Files:** src/websocket.py, features/websocket/  
**Tags:** websocket, memory, performance

### Data Import Validation

**Date:** 2026-08-04  
**Context:** CSV data import for historical price data  
**Problem:** Invalid data in CSV files was causing import failures without clear error messages.  
**Solution:** Implemented comprehensive data validation with detailed error reporting and batch rollback on failure.  
**Outcome:** Clear error messages, partial import success, easier data quality troubleshooting.  
**Lessons for Future:** Validate data before import. Provide detailed error messages. Implement transactional imports with rollback capability.  
**Related Files:** src/import.py, data/DATA_SOURCES.md  
**Tags:** data, validation, import

### Testing Strategy

**Date:** 2026-08-04  
**Context:** Growing codebase with increasing complexity  
**Problem:** Tests were focused on happy paths, missing edge cases and error conditions.  
**Solution:** Implemented comprehensive test coverage including edge cases, error conditions, and integration tests.  
**Outcome:** Higher confidence in deployments, earlier bug detection, better documentation of expected behavior.  
**Lessons for Future:** Test edge cases and error conditions first. Use integration tests for cross-component behavior. Maintain test coverage above 80%.  
**Related Files:** tests/, pytest.ini  
**Tags:** testing, quality, coverage

### Documentation Maintenance

**Date:** 2026-08-04  
**Context:** Documentation becoming outdated as features evolved  
**Problem:** Documentation was not being updated consistently with code changes, leading to confusion.  
**Solution:** Established documentation standards, integrated documentation updates into development workflow, created documentation index.  
**Outcome:** More accurate documentation, easier onboarding, better knowledge sharing.  
**Lessons for Future:** Treat documentation as code. Update docs with feature changes. Review documentation quarterly for accuracy.  
**Related Files:** docs/, docs/INDEX.md  
**Tags:** documentation, maintenance, workflow

### API Versioning

**Date:** 2026-08-04  
**Context:** API changes needed to support new features  
**Problem:** Breaking changes to API endpoints were causing issues for existing consumers.  
**Solution:** Implemented API versioning with versioned endpoints and deprecation timeline.  
**Outcome:** Smooth transitions for API consumers, backward compatibility, clear migration path.  
**Lessons for Future:** Plan API versioning from the start. Use semantic versioning. Communicate changes early. Provide migration guides.  
**Related Files:** src/api/, core/API_GUIDE.md  
**Tags:** api, versioning, compatibility

### Error Handling Strategy

**Date:** 2026-08-04  
**Context:** Inconsistent error handling across the application  
**Problem:** Errors were being caught at different levels with inconsistent logging and user feedback.  
**Solution:** Established error handling strategy with consistent error types, logging levels, and user messages.  
**Outcome:** Easier debugging, better user experience, consistent error monitoring.  
**Lessons for Future:** Define error handling strategy early. Use specific exception types. Log errors with context. Provide user-friendly error messages.  
**Related Files:** src/errors.py, core/TROUBLESHOOTING.md  
**Tags:** error-handling, logging, debugging

### CPU Thermal Management on HP Omen

**Date:** 2026-08-04  
**Context:** Local development machine (tony-omen, i7-9750H) running hot during trading system work  
**Problem:** Package temperature reached 91–93°C, cores 79–93°C, and 1-minute load averaged 15–20.  
**Solution:** Capped maximum CPU frequency from 2.60 GHz to 2.40 GHz using `sudo cpupower -c all frequency-set --max 2400MHz`.  
**Outcome:** Package temp dropped to 85°C, cores to 76–85°C, and ACPI temp fell 14°C. CPU remained capped at ~2400 MHz across all cores.  
**Lessons for Future:** Use `cpupower` for a reversible, software frequency cap. Verify the cap with `cpupower frequency-info`, `/proc/cpuinfo`, and `scaling_max_freq`. For bigger thermal gains, reduce sustained CPU load; a 200 MHz cap only delivers modest relief under heavy load.  
**Related Files:** N/A  
**Tags:** hardware, thermal, performance, operations

### Use Explicit Commands for Knowledge Base Archiving

**Date:** 2026-08-04  
**Context:** Archiving an operational lesson learned during an AI-assisted session  
**Problem:** The single-word command `archive` was ambiguous and could mean chat archive, workflow archive, or knowledge base archive, leading to unnecessary interpretation.  
**Solution:** Used the explicit phrase `archive this to lessons` to indicate the desired destination.  
**Outcome:** The lesson was appended directly to `docs/knowledge/lessons/lessons-learned.md` without extra clarification.  
**Lessons for Future:** Use `archive this to lessons` or `save this to the knowledge base` for one-shot archiving. Specify the target file or category whenever the same word could apply to multiple systems.  
**Related Files:** docs/knowledge/lessons/lessons-learned.md  
**Tags:** communication, knowledge-base, workflow, ai

## Adding New Lessons

When you learn a lesson worth sharing:

1. Use the lesson entry template above
2. Be specific about context and problem
3. Document the actual solution implemented
4. Capture the outcome (quantify if possible)
5. Extract actionable lessons for the future
6. Add related file paths and tags for searchability
7. Update the "Last Updated" date

## Categories

### Development Lessons
- Code architecture and design
- Implementation approaches
- Testing strategies
- Debugging techniques

### Operations Lessons
- Deployment procedures
- Monitoring and alerting
- Performance optimization
- Resource management

### Data Lessons
- Data quality issues
- Import/export problems
- Validation strategies
- Data modeling decisions

### Integration Lessons
- API integration challenges
- Third-party service issues
- System integration patterns
- Compatibility problems

## Related Knowledge

- [Best Practices](../best-practices/) - Project-specific best practices
- [Patterns](../patterns/) - Reusable patterns and approaches
- [Troubleshooting](../troubleshooting/) - Common issues and solutions

---

**Last Updated:** 2026-08-05
**Maintainer:** trade documentation team