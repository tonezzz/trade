#!/bin/bash

# validate-configs.sh
# ===================
# Validates consistency between SSOT and runtime configurations
#
# This script checks for configuration drift and reports inconsistencies
# between the SSOT (config/infrastructure.yml) and runtime configs.
#
# Usage: ./scripts/validate-configs.sh
#
# What it validates:
# - SSOT file structure (required keys and sections)
# - Remote server config (on tony-dell) against SSOT
# - Local MCP config (Devin CLI) against SSOT
#
# It checks:
# - Allowed directories match
# - Allowed commands match
# - Server configuration matches
# - Security settings match
# - MCP server endpoints and environment variables match
#
# Requirements:
# - Python 3 with PyYAML installed
# - SSH access to tony@192.168.1.42
#
# Exit codes:
# - 0: All configurations are in sync
# - 1: Issues found (check output for details)
#
# When to run:
# - Before deploying changes to production
# - After manual configuration changes
# - As part of CI/CD pipeline
# - Periodically to detect configuration drift

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SSOT_CONFIG="$PROJECT_ROOT/config/infrastructure.yml"

# Runtime config paths
REMOTE_USER="tony"
REMOTE_HOST="192.168.1.42"
REMOTE_CONFIG_PATH="/home/tony/mcp-remote-exec/config.yaml"
LOCAL_MCP_CONFIG="$HOME/.config/devin/mcp_config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_section() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Validation counters
ISSUES_FOUND=0
WARNINGS_FOUND=0

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

# Validate remote config against SSOT
validate_remote_config() {
    log_section "Validating Remote Config (tony-dell)"

    # Fetch remote config
    local remote_config=$(ssh "$REMOTE_USER@$REMOTE_HOST" "cat $REMOTE_CONFIG_PATH")

    # Use Python to compare configs
    python3 << PYTHON_SCRIPT
import yaml
import json
import sys

# Load SSOT
with open("$SSOT_CONFIG", 'r') as f:
    ssot = yaml.safe_load(f)

remote_exec_ssot = ssot['mcp_servers']['remote_exec_tony_dell']

# Parse remote config
remote_config_str = """$remote_config"""
remote_config = yaml.safe_load(remote_config_str)

# Compare allowed directories
ssot_dirs = set(remote_exec_ssot['allowed_directories'])
remote_dirs = set(remote_config['allowed_directories'])

if ssot_dirs != remote_dirs:
    print("❌ Allowed directories mismatch")
    print(f"   SSOT: {sorted(ssot_dirs)}")
    print(f"   Remote: {sorted(remote_dirs)}")
    print(f"   Missing in remote: {ssot_dirs - remote_dirs}")
    print(f"   Extra in remote: {remote_dirs - ssot_dirs}")
    sys.exit(1)
else:
    print("✓ Allowed directories match")

# Compare allowed commands
ssot_cmds = set(remote_exec_ssot['allowed_commands'])
remote_cmds = set(remote_config['allowed_commands'])

if ssot_cmds != remote_cmds:
    print("❌ Allowed commands mismatch")
    print(f"   SSOT count: {len(ssot_cmds)}, Remote count: {len(remote_cmds)}")
    print(f"   Missing in remote: {ssot_cmds - remote_cmds}")
    print(f"   Extra in remote: {remote_cmds - ssot_cmds}")
    sys.exit(1)
else:
    print("✓ Allowed commands match")

# Compare server config
ssot_server = remote_exec_ssot['server']
remote_server = remote_config['server']

if ssot_server != remote_server:
    print("❌ Server config mismatch")
    print(f"   SSOT: {ssot_server}")
    print(f"   Remote: {remote_server}")
    sys.exit(1)
else:
    print("✓ Server config matches")

# Compare security settings
ssot_security = remote_exec_ssot['security']
remote_security = remote_config['security']

if ssot_security != remote_security:
    print("❌ Security settings mismatch")
    print(f"   SSOT: {ssot_security}")
    print(f"   Remote: {remote_security}")
    sys.exit(1)
else:
    print("✓ Security settings match")

print("\n✓ Remote config is in sync with SSOT")
PYTHON_SCRIPT

    if [ $? -ne 0 ]; then
        ((ISSUES_FOUND++))
        log_warn "Remote config has drifted from SSOT"
        log_info "Run: ./scripts/deploy-mcp-config.sh to sync"
    else
        log_info "Remote config is in sync with SSOT"
    fi
}

# Validate local MCP config against SSOT
validate_local_mcp_config() {
    log_section "Validating Local MCP Config (Devin CLI)"

    if [ ! -f "$LOCAL_MCP_CONFIG" ]; then
        log_error "Local MCP config not found: $LOCAL_MCP_CONFIG"
        ((ISSUES_FOUND++))
        return
    fi

    # Use Python to compare configs
    python3 << PYTHON_SCRIPT
import yaml
import json
import sys

# Load SSOT
with open("$SSOT_CONFIG", 'r') as f:
    ssot = yaml.safe_load(f)

# Load local MCP config
with open("$LOCAL_MCP_CONFIG", 'r') as f:
    local_config = json.load(f)

# Check managed servers
managed_servers = {
    "remote-exec-tony-dell": "remote_exec_tony_dell",
    "playlive.tony-dell": "playlive_tony_dell",
    "mcp-gpu": "mcp_gpu"
}

all_match = True

for local_name, ssot_name in managed_servers.items():
    if local_name not in local_config['mcpServers']:
        print(f"❌ Server '{local_name}' not found in local config")
        all_match = False
        continue

    local_server = local_config['mcpServers'][local_name]
    ssot_server = ssot['mcp_servers'][ssot_name]

    # Check if enabled status matches
    ssot_enabled = ssot_server.get('enabled', True)
    local_disabled = local_server.get('disabled', False)

    if ssot_enabled and local_disabled:
        print(f"❌ Server '{local_name}' is enabled in SSOT but disabled in local config")
        all_match = False
    elif not ssot_enabled and not local_disabled:
        print(f"❌ Server '{local_name}' is disabled in SSOT but enabled in local config")
        all_match = False
    else:
        print(f"✓ Server '{local_name}' enabled status matches")

    # Check endpoint for playlive
    if ssot_name == "playlive_tony_dell":
        ssot_endpoint = ssot_server.get('endpoint')
        local_endpoint = local_server.get('env', {}).get('PLAYLIVE_URL')
        if ssot_endpoint != local_endpoint:
            print(f"❌ Server '{local_name}' endpoint mismatch")
            print(f"   SSOT: {ssot_endpoint}")
            print(f"   Local: {local_endpoint}")
            all_match = False
        else:
            print(f"✓ Server '{local_name}' endpoint matches")

    # Check environment variables for mcp-gpu
    if ssot_name == "mcp_gpu":
        ssot_env = ssot_server.get('environment', {})
        local_env = local_server.get('env', {})

        for key, value in ssot_env.items():
            if local_env.get(key) != value:
                print(f"❌ Server '{local_name}' env var '{key}' mismatch")
                print(f"   SSOT: {value}")
                print(f"   Local: {local_env.get(key)}")
                all_match = False
            else:
                print(f"✓ Server '{local_name}' env var '{key}' matches")

if all_match:
    print("\n✓ Local MCP config is in sync with SSOT")
else:
    sys.exit(1)
PYTHON_SCRIPT

    if [ $? -ne 0 ]; then
        ((ISSUES_FOUND++))
        log_warn "Local MCP config has drifted from SSOT"
        log_info "Run: python3 scripts/generate-mcp-configs.py to sync"
    else
        log_info "Local MCP config is in sync with SSOT"
    fi
}

# Validate SSOT file structure
validate_ssot_structure() {
    log_section "Validating SSOT Structure"

    python3 << PYTHON_SCRIPT
import yaml
import sys

with open("$SSOT_CONFIG", 'r') as f:
    ssot = yaml.safe_load(f)

required_keys = ['settings', 'machines', 'mcp_servers', 'network', 'monitoring', 'backup']
missing_keys = []

for key in required_keys:
    if key not in ssot:
        missing_keys.append(key)

if missing_keys:
    print(f"❌ SSOT missing required keys: {missing_keys}")
    sys.exit(1)
else:
    print("✓ SSOT has all required top-level keys")

# Check required MCP servers
required_servers = ['remote_exec_tony_dell', 'playlive_tony_dell', 'mcp_gpu']
missing_servers = []

for server in required_servers:
    if server not in ssot['mcp_servers']:
        missing_servers.append(server)

if missing_servers:
    print(f"❌ SSOT missing required MCP servers: {missing_servers}")
    sys.exit(1)
else:
    print("✓ SSOT has all required MCP servers")

# Check remote_exec_tony_dell has required sections
remote_exec = ssot['mcp_servers']['remote_exec_tony_dell']
required_sections = ['server', 'security', 'allowed_directories', 'allowed_commands', 'client']
missing_sections = []

for section in required_sections:
    if section not in remote_exec:
        missing_sections.append(section)

if missing_sections:
    print(f"❌ remote_exec_tony_dell missing required sections: {missing_sections}")
    sys.exit(1)
else:
    print("✓ remote_exec_tony_dell has all required sections")

print("\n✓ SSOT structure is valid")
PYTHON_SCRIPT

    if [ $? -ne 0 ]; then
        ((ISSUES_FOUND++))
        log_error "SSOT structure validation failed"
    else
        log_info "SSOT structure is valid"
    fi
}

# Print summary
print_summary() {
    log_section "Validation Summary"

    if [ $ISSUES_FOUND -eq 0 ]; then
        log_info "✓ All configurations are in sync with SSOT"
        log_info "No issues found"
        return 0
    else
        log_error "✗ Found $ISSUES_FOUND issue(s) that need attention"
        log_info "Run the suggested commands to sync configurations"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting configuration validation..."
    log_info "SSOT: $SSOT_CONFIG"
    echo ""

    # Check prerequisites
    check_python
    check_ssh
    echo ""

    # Validate SSOT structure
    validate_ssot_structure
    echo ""

    # Validate remote config
    validate_remote_config
    echo ""

    # Validate local MCP config
    validate_local_mcp_config
    echo ""

    # Print summary
    print_summary
}

# Run main function
main "$@"
