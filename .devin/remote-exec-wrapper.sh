#!/bin/bash
# Wrapper script to run MCP server on tony-dell via SSH
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 tony@192.168.1.42 "cd /home/tony/mcp-remote-exec && python3 mcp_server.py"
