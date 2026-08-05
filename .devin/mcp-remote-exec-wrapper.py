#!/usr/bin/env python3
"""
Wrapper script to run MCP server on tony-dell via SSH
Proxies stdio communication between local MCP client and remote server
"""

import subprocess
import sys
import threading
import queue
import json

def main():
    # Start SSH process to run remote MCP server
    ssh_process = subprocess.Popen(
        [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=60",
            "tony@192.168.1.42",
            "cd /home/tony/mcp-remote-exec && python3 mcp_server.py"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Create queues for communication
    stdin_queue = queue.Queue()
    stdout_queue = queue.Queue()
    
    def read_from_remote():
        """Read from remote stdout and put in queue"""
        for line in ssh_process.stdout:
            stdout_queue.put(line)
    
    def write_to_remote():
        """Write from queue to remote stdin"""
        while True:
            line = stdin_queue.get()
            if line is None:  # Sentinel to stop
                break
            ssh_process.stdin.write(line)
            ssh_process.stdin.flush()
    
    def read_from_local():
        """Read from local stdin and put in queue"""
        for line in sys.stdin:
            stdin_queue.put(line)
    
    def write_to_local():
        """Write from queue to local stdout"""
        while True:
            line = stdout_queue.get()
            if line is None:  # Sentinel to stop
                break
            sys.stdout.write(line)
            sys.stdout.flush()
    
    # Start threads
    threads = [
        threading.Thread(target=read_from_remote, daemon=True),
        threading.Thread(target=write_to_remote, daemon=True),
        threading.Thread(target=read_from_local, daemon=True),
        threading.Thread(target=write_to_local, daemon=True)
    ]
    
    for thread in threads:
        thread.start()
    
    # Wait for SSH process to finish
    ssh_process.wait()
    
    # Clean up
    stdin_queue.put(None)
    stdout_queue.put(None)
    
    for thread in threads:
        thread.join(timeout=1)

if __name__ == "__main__":
    main()
