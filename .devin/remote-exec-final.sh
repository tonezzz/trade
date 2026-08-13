#!/bin/bash
set -e
exec ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o ServerAliveCountMax=3 tony@tony-dell.local "cd /home/tony/mcp-remote-exec && python3 mcp_server.py"
