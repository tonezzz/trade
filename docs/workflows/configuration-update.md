# Configuration Update Workflow

## Purpose
Standard procedure for updating infrastructure configuration using the SSOT approach.

## Prerequisites
- Access to `config/infrastructure.yml`
- SSH access to remote servers (if applicable)
- Python 3 with PyYAML installed
- Appropriate permissions to modify configuration

## Steps

### 1. Edit the SSOT
```bash
# Edit the infrastructure configuration
vim config/infrastructure.yml
```

Make your changes to the Single Source of Truth file.

### 2. Validate Changes
```bash
# Run validation to check for syntax and consistency
./scripts/validate-configs.sh
```

Review the validation output:
- ✅ If valid: Proceed to deployment
- ❌ If invalid: Fix issues and re-validate

### 3. Deploy to Runtime Configs

#### For Remote Server Configuration
```bash
# Deploy to remote server (tony-dell)
./scripts/deploy-mcp-config.sh
```

The script will:
- Generate the remote config from SSOT
- Backup existing config on remote server
- Deploy new config via SSH
- Prompt to restart the MCP service

#### For Local Configuration
```bash
# Generate local MCP configs
python3 scripts/generate-mcp-configs.py
```

The script will:
- Generate Devin CLI MCP configuration
- Merge with existing config (preserving unmanaged servers)
- Write to `~/.config/devin/mcp_config.json`

### 4. Verify Deployment
```bash
# Confirm everything is in sync
./scripts/validate-configs.sh
```

Ensure all configurations show as consistent.

### 5. Test Changes
- Test the affected functionality
- Verify services are operating correctly
- Check logs for any issues

## Verification

### Success Indicators
- Validation script shows no drift
- Services start without errors
- Functionality works as expected
- No error messages in logs

### Rollback Procedure
If issues occur:
```bash
# Restore from backup on remote server
ssh tony@192.168.1.42 'cp ~/mcp-remote-exec/config.yaml.backup.* ~/mcp-remote-exec/config.yaml'

# Restart the service
ssh tony@192.168.1.42 'systemctl --user restart mcp-remote-exec.service'

# For local config, regenerate from previous SSOT version
git checkout config/infrastructure.yml
python3 scripts/generate-mcp-configs.py
```

## Troubleshooting

### SSH Connection Fails
- Check network connectivity
- Verify SSH keys are configured
- Test manual SSH connection

### Validation Shows Drift
- Check if manual changes were made to runtime configs
- Re-run deployment scripts to sync
- Review drift details to understand what changed

### Service Won't Start After Config Change
- Check config syntax with `yamllint`
- Review service logs: `journalctl --user -u mcp-remote-exec.service`
- Restore from backup if needed

## Related Workflows
- [Service Deployment Workflow](service-deployment.md) - Deploying service updates
- [Troubleshooting Workflow](troubleshooting.md) - Systematic troubleshooting

## Related Documentation
- [Configuration Management Guide](../CONFIGURATION_MANAGEMENT.md)
- [Infrastructure Documentation](../core/DEPLOYMENT.md)
- [SSOT Configuration Pattern](../knowledge/architecture/ssot-configuration-pattern.md)

## Last Updated
2026-08-04

---

**Tags:** configuration, ssot, deployment, infrastructure
**Category:** infrastructure
**Complexity:** low
