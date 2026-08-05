#!/usr/bin/env python3
"""
generate-mcp-configs.py
======================
Generates Devin CLI MCP client configuration from SSOT

This script reads from config/infrastructure.yml (the SSOT) and
generates the appropriate sections for ~/.config/devin/mcp_config.json.

Usage: python3 scripts/generate-mcp-configs.py

What it generates:
- remote-exec-tony-dell: Remote execution server config
- playlive.tony-dell: Browser automation server config
- mcp-gpu: GPU compute server config

The script preserves existing non-managed servers (github, mcp-llama, etc.)
and only updates the servers defined in the SSOT.

Requirements:
- Python 3 with PyYAML installed

Managed servers (from SSOT):
- remote-exec-tony-dell
- playlive.tony-dell
- mcp-gpu

Unmanaged servers (preserved):
- github, mcp-llama, playlive.local, postgres, yomi
"""

import yaml
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SSOT_CONFIG = PROJECT_ROOT / "config" / "infrastructure.yml"
OUTPUT_CONFIG = Path.home() / ".config" / "devin" / "mcp_config.json"


def load_ssot():
    """Load the SSOT infrastructure configuration"""
    if not SSOT_CONFIG.exists():
        print(f"Error: SSOT config not found at {SSOT_CONFIG}")
        sys.exit(1)

    with open(SSOT_CONFIG, 'r') as f:
        return yaml.safe_load(f)


def load_existing_mcp_config():
    """Load existing MCP config if it exists"""
    if OUTPUT_CONFIG.exists():
        with open(OUTPUT_CONFIG, 'r') as f:
            return json.load(f)
    return {"mcpServers": {}}


def generate_remote_exec_config(ssot):
    """Generate remote-exec-tony-dell server config from SSOT"""
    remote_exec = ssot['mcp_servers']['remote_exec_tony_dell']

    return {
        "command": "/bin/bash",
        "args": [
            remote_exec['client']['wrapper_script']
        ]
    }


def generate_playlive_config(ssot):
    """Generate playlive.tony-dell server config from SSOT"""
    playlive = ssot['mcp_servers']['playlive_tony_dell']

    return {
        "command": "/usr/bin/python3",
        "args": [
            "/home/tony/CascadeProjects/chaba-omen/mcp/mcp-playlive/playlive-server.py"
        ],
        "disabled": not playlive['enabled'],
        "env": {
            "PLAYLIVE_URL": playlive['endpoint']
        }
    }


def generate_gpu_config(ssot):
    """Generate mcp-gpu server config from SSOT"""
    gpu = ssot['mcp_servers']['mcp_gpu']

    return {
        "command": "/usr/bin/python3",
        "args": [
            "/home/tony/CascadeProjects/chaba-omen/mcp/mcp-gpu/server.py"
        ],
        "env": {
            "IMAGEN_URL": gpu['environment']['IMAGEN_URL'],
            "LLAMA_URL": gpu['environment']['LLAMA_URL']
        }
    }


def merge_configs(existing_config, generated_configs):
    """Merge generated configs with existing, preserving non-generated entries"""
    # Servers that are managed by this script
    managed_servers = {
        "remote-exec-tony-dell",
        "playlive.tony-dell",
        "mcp-gpu"
    }

    # Remove managed servers from existing config
    for server in managed_servers:
        if server in existing_config['mcpServers']:
            del existing_config['mcpServers'][server]

    # Add generated configs
    for server_name, server_config in generated_configs.items():
        existing_config['mcpServers'][server_name] = server_config

    return existing_config


def write_config(config, output_path):
    """Write the merged config to file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
        f.write('\n')  # Add trailing newline


def main():
    print("=" * 60)
    print("MCP Config Generator")
    print("=" * 60)
    print(f"SSOT: {SSOT_CONFIG}")
    print(f"Output: {OUTPUT_CONFIG}")
    print()

    # Load SSOT
    print("Loading SSOT configuration...")
    ssot = load_ssot()
    print("✓ SSOT loaded successfully")

    # Load existing config
    print("Loading existing MCP config...")
    existing_config = load_existing_mcp_config()
    print(f"✓ Existing config loaded ({len(existing_config['mcpServers'])} servers)")

    # Generate configs from SSOT
    print("Generating configs from SSOT...")
    generated_configs = {
        "remote-exec-tony-dell": generate_remote_exec_config(ssot),
        "playlive.tony-dell": generate_playlive_config(ssot),
        "mcp-gpu": generate_gpu_config(ssot)
    }
    print(f"✓ Generated {len(generated_configs)} server configs")

    # Merge configs
    print("Merging with existing config...")
    merged_config = merge_configs(existing_config, generated_configs)
    print(f"✓ Merged config contains {len(merged_config['mcpServers'])} servers")

    # Write output
    print("Writing output config...")
    write_config(merged_config, OUTPUT_CONFIG)
    print(f"✓ Config written to {OUTPUT_CONFIG}")

    print()
    print("=" * 60)
    print("Generation complete!")
    print("=" * 60)
    print()
    print("Managed servers (from SSOT):")
    for server in generated_configs:
        print(f"  - {server}")
    print()
    print("Unmanaged servers (preserved):")
    managed_servers = {"remote-exec-tony-dell", "playlive.tony-dell", "mcp-gpu"}
    for server in existing_config['mcpServers']:
        if server not in managed_servers:
            print(f"  - {server}")


if __name__ == "__main__":
    main()
