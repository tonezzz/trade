#!/usr/bin/env python3
"""
Wrapper script to run MCP server on tony-dell via SSH
Proxies stdio communication between local MCP client and remote server
"""

import subprocess
import sys
import json

def main():
    # Start SSH process to run remote MCP server
    ssh_process = subprocess.Popen(
        [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=60",
            "-o", "ServerAliveCountMax=3",
            "tony@tony-dell.local",
            "cd /home/tony/mcp-remote-exec && python3 mcp_server.py"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Proxy stdin to SSH process
    def stdin_to_ssh():
        for line in sys.stdin:
            ssh_process.stdin.write(line)
            ssh_process.stdin.flush()
    
    # Proxy SSH stdout to stdout
    def ssh_to_stdout():
        for line in ssh_process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
    
    # Start threads for bidirectional communication
    import threading
    stdin_thread = threading.Thread(target=stdin_to_ssh, daemon=True)
    stdout_thread = threading.Thread(target=ssh_to_stdout, daemon=True)
    
    stdin_thread.start()
    stdout_thread.start()
    
    # Wait for SSH process to finish
    ssh_process.wait()
    
    # Join threads
    stdin_thread.join(timeout=1)
    stdout_thread.join(timeout=1)

if __name__ == "__main__":
    main()
