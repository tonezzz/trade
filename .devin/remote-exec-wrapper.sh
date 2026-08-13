#!/bin/bash
# Wrapper script to run MCP server on tony-dell via SSH
exec ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o ServerAliveCountMax=3 tony@tony-dell.local "cd /home/tony/mcp-remote-exec && python3 mcp_server.py"
