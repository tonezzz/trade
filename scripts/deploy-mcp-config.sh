#!/bin/bash

# deploy-mcp-config.sh
# ====================
# Deploys MCP server configuration from SSOT to remote server
#
# This script reads from config/infrastructure.yml (the SSOT) and
# generates/syncs the remote config.yaml on tony-dell.
#
# Usage: ./scripts/deploy-mcp-config.sh
#
# What it syncs:
# - Security settings (enable_command_whitelist, enable_path_validation, etc.)
# - Allowed directories for file operations
# - Server configuration (host, port, log_level)
# - Allowed commands whitelist
#
# Requirements:
# - Python 3 with PyYAML installed
# - SSH access to tony@192.168.1.42
#
# The script will:
# 1. Validate SSH connectivity
# 2. Generate config from SSOT
# 3. Backup existing remote config
# 4. Deploy new config
# 5. Prompt to restart MCP service

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/infrastructure.yml"

# Remote server details (from SSOT)
REMOTE_USER="tony"
REMOTE_HOST="192.168.1.42"
REMOTE_CONFIG_PATH="/home/tony/mcp-remote-exec/config.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python and PyYAML are available
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is not installed."
        exit 1
    fi
    if ! python3 -c "import yaml" &> /dev/null; then
        log_error "PyYAML is not installed. Install with: pip install pyyaml"
        exit 1
    fi
}

# Check if SSH connection works
check_ssh() {
    log_info "Checking SSH connection to $REMOTE_USER@$REMOTE_HOST..."
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$REMOTE_USER@$REMOTE_HOST" echo "SSH connection successful" &> /dev/null; then
        log_error "Cannot connect to $REMOTE_USER@$REMOTE_HOST via SSH"
        exit 1
    fi
    log_info "SSH connection successful"
}

# Generate remote config from SSOT
generate_remote_config() {
    log_info "Generating remote config from SSOT..."

    # Use Python to parse YAML and generate config
    python3 << 'PYTHON_SCRIPT'
import yaml
from datetime import datetime

config_file = "/home/tony/CascadeProjects/trade/config/infrastructure.yml"
output_file = "/tmp/mcp-remote-config.yaml"

with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Extract remote exec server config
remote_exec = config['mcp_servers']['remote_exec_tony_dell']

# Generate the remote config YAML
output = {
    'allowed_directories': remote_exec['allowed_directories'],
    'allowed_commands': remote_exec['allowed_commands'],
    'server': remote_exec['server'],
    'security': remote_exec['security']
}

# Write with header
with open(output_file, 'w') as f:
    f.write("# Remote Execution MCP Server Configuration\n")
    f.write("# Auto-generated from SSOT: config/infrastructure.yml\n")
    f.write(f"# Generated on: {datetime.now().isoformat()}\n\n")
    yaml.dump(output, f, default_flow_style=False, sort_keys=False)

print(f"Generated config saved to {output_file}")
PYTHON_SCRIPT

    log_info "Generated config saved to /tmp/mcp-remote-config.yaml"
}

# Deploy config to remote server
deploy_config() {
    log_info "Deploying config to $REMOTE_USER@$REMOTE_HOST:$REMOTE_CONFIG_PATH..."

    # Backup existing config
    ssh "$REMOTE_USER@$REMOTE_HOST" "cp $REMOTE_CONFIG_PATH ${REMOTE_CONFIG_PATH}.backup.$(date +%Y%m%d_%H%M%S)" || true

    # Copy new config
    scp /tmp/mcp-remote-config.yaml "$REMOTE_USER@$REMOTE_HOST:$REMOTE_CONFIG_PATH"

    log_info "Config deployed successfully"
    log_info "Backup created on remote server"
}

# Restart MCP server service
restart_service() {
    log_info "Restarting MCP server service on remote host..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "systemctl --user restart mcp-remote-exec.service" || {
        log_warn "Failed to restart service. You may need to restart it manually."
        log_info "Run: ssh $REMOTE_USER@$REMOTE_HOST 'systemctl --user restart mcp-remote-exec.service'"
    }
}

# Main execution
main() {
    log_info "Starting MCP config deployment from SSOT..."
    log_info "SSOT file: $CONFIG_FILE"

    # Check prerequisites
    check_python
    check_ssh

    # Check if SSOT file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "SSOT config file not found: $CONFIG_FILE"
        exit 1
    fi

    # Generate and deploy
    generate_remote_config
    deploy_config

    # Ask about restarting service
    echo ""
    read -p "Restart MCP server service on remote host? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restart_service
    else
        log_info "Skipping service restart. Remember to restart manually if needed."
    fi

    log_info "Deployment complete!"
}

# Run main function
main "$@"
