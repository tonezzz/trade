# SSOT Configuration Pattern

## Problem
Managing configuration across multiple environments and services often leads to configuration drift, inconsistencies, and maintenance challenges.

## Context
The trade project uses multiple machines (tony-omen, tony-dell) and services with various configuration needs. Historically, configuration was managed separately in different locations, making it difficult to ensure consistency.

## Solution
Implement a Single Source of Truth (SSOT) pattern for configuration management:
- **SSOT File**: `config/infrastructure.yml` serves as the authoritative source
- **Runtime Configs**: Generated from SSOT via automation scripts
- **Validation**: Scripts to check consistency between SSOT and runtime configs
- **Deployment**: Automated sync from SSOT to all runtime environments

## Implementation

### SSOT Structure
```yaml
mcp_servers:
  remote_exec_tony_dell:
    endpoint: "http://192.168.1.42:3000"
    allowed_commands: [...]
    security: {...}
```

### Automation Scripts
- `deploy-mcp-config.sh` - Deploys SSOT to remote servers
- `generate-mcp-configs.py` - Generates local configs from SSOT
- `validate-configs.sh` - Validates consistency across all configs

### Workflow
1. Edit SSOT file
2. Validate changes
3. Deploy to runtime configs
4. Verify deployment

## Rationale
- **Consistency**: Single source prevents configuration drift
- **Documentation**: SSOT serves as documentation
- **Automation**: Reduces manual errors
- **Traceability**: All changes tracked in one place
- **Validation**: Automated checks ensure correctness

## Alternatives Considered
- **Environment variables**: Harder to document and validate
- **Multiple config files**: Leads to drift and inconsistencies
- **Configuration management tools**: Overkill for this scale

## Related Knowledge
- [Configuration Management Guide](../CONFIGURATION_MANAGEMENT.md)
- [Infrastructure Documentation](core/DEPLOYMENT.md)
- [Scripts Documentation](../scripts/README.md)

## References
- [Configuration Management Best Practices](knowledge/best-practices/README.md)

---

**Tags:** configuration, ssot, infrastructure, automation, patterns
**Category:** architecture
**Complexity:** medium
**Last Updated:** 2026-08-04
