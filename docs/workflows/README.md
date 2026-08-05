# Workflows Archive

This directory contains archived workflow documentation and procedures. Workflows are step-by-step processes for accomplishing specific tasks in the trade system.

## Purpose

The workflows archive serves as a knowledge base for:
- Complex multi-step procedures
- Cross-system operational workflows
- Deployment and maintenance processes
- Troubleshooting procedures
- Development workflows

## Workflow Categories

### Development Workflows
- Feature development processes
- Code review procedures
- Testing workflows
- Documentation updates

### Operations Workflows
- Deployment procedures
- System maintenance
- Backup and recovery
- Monitoring and alerting

### Infrastructure Workflows
- Configuration management
- Service management
- Multi-machine operations
- MCP server management

### Data Workflows
- Data import procedures
- Data validation processes
- Data quality checks
- Historical data management

## Workflow Template

When creating a new workflow, use this template:

```markdown
# Workflow Name

## Purpose
Brief description of what this workflow accomplishes.

## Prerequisites
- Required tools, access, or permissions
- Pre-conditions that must be met
- Dependencies on other workflows

## Steps
1. Step one description
   - Detailed instructions
   - Commands to run
   - Expected outcomes

2. Step two description
   - Detailed instructions
   - Commands to run
   - Expected outcomes

## Verification
How to verify the workflow completed successfully.

## Troubleshooting
Common issues and their solutions.

## Related Workflows
Links to related workflows or documentation.

---

**Last Updated:** YYYY-MM-DD  
**Maintainer:** [Name]
```

## Adding New Workflows

1. Create a new markdown file in the appropriate category
2. Use the workflow template
3. Update this index with a link to the new workflow
4. Follow naming convention: `CATEGORY-workflow-name.md`

## Workflow Maintenance

- Review workflows quarterly for accuracy
- Update when procedures change
- Archive outdated workflows to docs-archive/
- Maintain cross-references between related workflows

## Index

### Development Workflows
- *No development workflows archived yet*

### Operations Workflows
- *No operations workflows archived yet*

### Infrastructure Workflows
- **[Configuration Update Workflow](configuration-update.md)** - Standard procedure for updating infrastructure configuration using SSOT

### Data Workflows
- *No data workflows archived yet*

---

**Last Updated: 2026-08-04
**Maintainer:** trade documentation team
