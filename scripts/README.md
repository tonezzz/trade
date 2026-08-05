# Scripts

This directory contains various automation and management scripts for the trade project.

## Database Setup Scripts

### setup_database.py

Interactive database setup wizard for automated database initialization and configuration.

**What it does:**
- Guides users through database configuration (PostgreSQL or SQLite)
- Collects database connection parameters interactively
- Tests database connection before proceeding
- Creates database if it doesn't exist (PostgreSQL only)
- Initializes database schema with all required tables
- Saves configuration to `.env` file
- Verifies setup was successful

**Usage:**
```bash
# Via CLI (recommended)
python3 cli.py setup

# Or directly
python3 scripts/setup_database.py
```

**Features:**
- Interactive wizard with clear prompts
- Connection testing before database creation
- Automatic environment file generation
- Schema verification
- Error handling with helpful messages
- Support for both PostgreSQL and SQLite

**When to use:**
- First-time project setup
- When setting up a new development environment
- When database configuration needs to be changed
- When reinitializing the database schema

**Requirements:**
- Python 3 with SQLAlchemy and psycopg2 (for PostgreSQL)
- PostgreSQL server running (if using PostgreSQL)
- Database user with CREATE DATABASE privileges (PostgreSQL)

## Infrastructure Configuration Scripts

Scripts for managing infrastructure configuration synchronization between the Single Source of Truth (SSOT) and runtime configurations.

## Overview

The infrastructure configuration is managed with a **Single Source of Truth (SSOT)** approach:

- **SSOT**: `config/infrastructure.yml` - Documentation and authoritative source for all infrastructure settings
- **Runtime configs**: Actual configuration files used by services (deployed from SSOT)

## Configuration Files

### SSOT (Single Source of Truth)
- **Location**: `/home/tony/CascadeProjects/trade/config/infrastructure.yml`
- **Purpose**: Authoritative documentation and source for all infrastructure configuration
- **Contains**: Machine definitions, MCP server configs, network settings, security settings, monitoring, etc.

### Runtime Configurations
- **Remote server config**: `/home/tony/mcp-remote-exec/config.yaml` (on tony-dell)
  - Used by the MCP remote execution server
- **Devin CLI MCP config**: `~/.config/devin/mcp_config.json`
  - Used by Devin CLI to connect to MCP servers

## Scripts

### 1. deploy-mcp-config.sh

Deploys MCP server configuration from SSOT to the remote server (tony-dell).

**What it does:**
- Reads configuration from `config/infrastructure.yml`
- Generates the remote server config file
- Backs up the existing config on the remote server
- Deploys the new config via SSH
- Optionally restarts the MCP server service

**Usage:**
```bash
./scripts/deploy-mcp-config.sh
```

**Requirements:**
- Python 3 with PyYAML installed
- SSH access to tony@192.168.1.42
- The script will prompt to restart the MCP service

**When to run:**
- After making changes to `mcp_servers.remote_exec_tony_dell` in infrastructure.yml
- When security settings, allowed directories, or command whitelist need updating

### 2. generate-mcp-configs.py

Generates Devin CLI MCP client configuration from SSOT.

**What it does:**
- Reads configuration from `config/infrastructure.yml`
- Generates MCP server configurations for Devin CLI
- Merges with existing config, preserving non-managed servers
- Writes to `~/.config/devin/mcp_config.json`

**Managed servers (from SSOT):**
- `remote-exec-tony-dell`
- `playlive.tony-dell`
- `mcp-gpu`

**Unmanaged servers (preserved):**
- `github`, `mcp-llama`, `playlive.local`, `postgres`, `yomi`

**Usage:**
```bash
python3 scripts/generate-mcp-configs.py
```

**Requirements:**
- Python 3 with PyYAML installed

**When to run:**
- After making changes to MCP server configurations in infrastructure.yml
- When adding new MCP servers to the SSOT
- When updating endpoints or environment variables

### 3. validate-configs.sh

Validates consistency between SSOT and runtime configurations.

**What it does:**
- Checks SSOT file structure for completeness
- Compares remote server config against SSOT
- Compares local MCP config against SSOT
- Reports any drift or inconsistencies
- Provides actionable feedback

**Usage:**
```bash
./scripts/validate-configs.sh
```

**Requirements:**
- Python 3 with PyYAML installed
- SSH access to tony@192.168.1.42

**When to run:**
- Before deploying changes to production
- After manual configuration changes
- As part of CI/CD pipeline
- Periodically to detect configuration drift

## Workflow

### Making Configuration Changes

1. **Edit the SSOT**
   ```bash
   # Edit infrastructure.yml
   vim config/infrastructure.yml
   ```

2. **Validate changes**
   ```bash
   # Check that your changes are valid
   ./scripts/validate-configs.sh
   ```

3. **Deploy to runtime configs**
   ```bash
   # Update remote server config
   ./scripts/deploy-mcp-config.sh

   # Update local MCP config
   python3 scripts/generate-mcp-configs.py
   ```

4. **Verify deployment**
   ```bash
   # Confirm everything is in sync
   ./scripts/validate-configs.sh
   ```

### Typical Change Scenarios

#### Adding a new allowed command
1. Add command to `mcp_servers.remote_exec_tony_dell.allowed_commands` in infrastructure.yml
2. Run `./scripts/deploy-mcp-config.sh`
3. Restart MCP service when prompted

#### Updating MCP server endpoint
1. Update endpoint in `mcp_servers.playlive_tony_dell.endpoint` in infrastructure.yml
2. Run `python3 scripts/generate-mcp-configs.py`
3. Restart Devin CLI to pick up changes

#### Changing security settings
1. Update `mcp_servers.remote_exec_tony_dell.security` in infrastructure.yml
2. Run `./scripts/deploy-mcp-config.sh`
3. Restart MCP service when prompted

#### Adding a new MCP server
1. Add server definition to `mcp_servers` in infrastructure.yml
2. Update generate-mcp-configs.py to include the new server
3. Run `python3 scripts/generate-mcp-configs.py`
4. Test the new server connection

## Best Practices

1. **Always edit the SSOT first** - Never directly edit runtime configs
2. **Validate before deploying** - Run validate-configs.sh to catch issues early
3. **Test in development** - Make changes in development environment first
4. **Backup before major changes** - The deploy script creates backups automatically
5. **Document changes** - Add comments in infrastructure.yml explaining why changes were made
6. **Run validation periodically** - Detect configuration drift before it causes issues

## Troubleshooting

### SSH connection fails
- Check that you can manually SSH to tony@192.168.1.42
- Verify SSH keys are set up correctly
- Check network connectivity

### Python/PyYAML not found
```bash
# Install PyYAML
pip install pyyaml
```

### Validation shows drift
- Run the appropriate deployment script to sync
- Check if someone made manual changes to runtime configs
- Review the drift details to understand what changed

### MCP service won't start after config change
- Check the config syntax with `yamllint` or similar
- Review the service logs: `ssh tony@192.168.1.42 'journalctl --user -u mcp-remote-exec.service'`
- Restore from backup if needed

## CHANGELOG Management Scripts

Scripts for automating CHANGELOG.md maintenance and version releases.

### 1. update-changelog.sh

Quick helper script to add entries to CHANGELOG.md.

**What it does:**
- Adds entries to the [Unreleased] section
- Automatically creates subsections if they don't exist
- Validates change types

**Usage:**
```bash
./scripts/update-changelog.sh <type> <description>
```

**Change types:** added, changed, deprecated, removed, fixed, security

**Example:**
```bash
./scripts/update-changelog.sh added "New feature for user authentication"
./scripts/update-changelog.sh fixed "Fixed database connection timeout issue"
```

**When to use:**
- Quick additions to the changelog during development
- Simple one-off entries
- When you don't need advanced changelog management

### 2. changelog-manager.py

Advanced changelog management with validation and version releases.

**What it does:**
- Add entries to changelog with validation
- Release new versions from [Unreleased] entries
- Validate changelog format and structure
- Support for complex changelog operations

**Usage:**
```bash
# Add an entry
python3 scripts/changelog-manager.py add added "New feature description"

# Release a new version
python3 scripts/changelog-manager.py release 1.2.3

# Validate changelog format
python3 scripts/changelog-manager.py validate
```

**When to use:**
- When preparing for a release
- When you need to validate changelog format
- For complex changelog management operations
- When releasing new versions

## CHANGELOG Workflow

### During Development
1. Use `update-changelog.sh` for quick entries:
   ```bash
   ./scripts/update-changelog.sh added "Feature you just implemented"
   ```

2. Or use `changelog-manager.py` for more control:
   ```bash
   python3 scripts/changelog-manager.py add added "Feature description"
   ```

### Preparing for Release
1. Validate the changelog:
   ```bash
   python3 scripts/changelog-manager.py validate
   ```

2. Review [Unreleased] entries for completeness

3. Release the version:
   ```bash
   python3 scripts/changelog-manager.py release 1.2.3
   ```

4. Commit the changes:
   ```bash
   git add CHANGELOG.md
   git commit -m "Release version 1.2.3"
   git tag v1.2.3
   ```

## Best Practices

1. **Update changelog as you work** - Don't wait until release time
2. **Be descriptive** - Include enough detail for users to understand changes
3. **Use appropriate types** - Choose the right change type for each entry
4. **Validate before release** - Ensure format is correct
5. **Keep entries user-focused** - Describe impact on users, not implementation details

## File Structure

```
/home/tony/CascadeProjects/trade/
├── config/
│   └── infrastructure.yml          # SSOT (edit this)
├── scripts/
│   ├── deploy-mcp-config.sh        # Deploy to remote server
│   ├── generate-mcp-configs.py     # Generate Devin CLI config
│   ├── validate-configs.sh         # Validate consistency
│   ├── update-changelog.sh         # Quick changelog updates
│   ├── changelog-manager.py        # Advanced changelog management
│   └── README.md                   # This file
└── .devin/
    └── remote-exec-wrapper.sh      # Wrapper script
```

## Remote Server Structure

```
tony@192.168.1.42:/home/tony/
└── mcp-remote-exec/
    ├── config.yaml                 # Runtime config (auto-generated)
    ├── config.yaml.backup.*        # Backups
    ├── mcp_server.py
    ├── http_server.py
    └── ...
```

## Support

For issues or questions about these scripts:
1. Check the troubleshooting section above
2. Review script comments for detailed behavior
3. Run with verbose output if needed (edit scripts to enable debug mode)
