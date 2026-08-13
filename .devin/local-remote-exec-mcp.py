#!/usr/bin/env python3
"""
Local MCP Server for Remote Execution on tony-dell
Runs locally but executes commands on tony-dell via SSH
"""

import json
import logging
import subprocess
import sys
from typing import Optional, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

def remote_exec(command: str, working_dir: Optional[str] = None) -> str:
    """Execute a command on tony-dell via SSH."""
    logger.info(f"Executing command on tony-dell: {command}")
    
    try:
        ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "tony@tony-dell.local"]
        
        if working_dir:
            ssh_cmd.append(f"cd {working_dir} && {command}")
        else:
            ssh_cmd.append(command)
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = f"Exit code: {result.returncode}\n"
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}"
        
        # Truncate output if too large
        if len(output) > 10485760:
            output = output[:10485760] + "\n... (output truncated)"
        
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 300 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def remote_read(file_path: str) -> str:
    """Read a file from tony-dell via SSH."""
    logger.info(f"Reading file from tony-dell: {file_path}")
    
    try:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "tony@tony-dell.local", f"cat {file_path}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error reading file: {result.stderr}"
        
        content = result.stdout
        
        # Truncate if too large
        if len(content) > 10485760:
            content = content[:10485760] + "\n... (content truncated)"
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def remote_write(file_path: str, content: str) -> str:
    """Write content to a file on tony-dell via SSH."""
    logger.info(f"Writing file to tony-dell: {file_path}")
    
    try:
        # Create parent directories if they don't exist
        subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "tony@tony-dell.local", f"mkdir -p $(dirname {file_path})"],
            capture_output=True,
            timeout=10
        )
        
        # Write content using cat
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "tony@tony-dell.local", f"cat > {file_path}"],
            input=content,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error writing file: {result.stderr}"
        
        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def remote_list(directory: str) -> str:
    """List contents of a directory on tony-dell via SSH."""
    logger.info(f"Listing directory on tony-dell: {directory}")
    
    try:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "tony@tony-dell.local", f"ls -la {directory}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error listing directory: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def get_status() -> str:
    """Get the status of tony-dell."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "tony@tony-dell.local", "hostname && uptime && df -h /home/tony"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error getting status: {result.stderr}"
        
        return result.stdout
    except Exception as e:
        return f"Error getting status: {str(e)}"

# MCP Protocol implementation
TOOLS = [
    {
        "name": "remote_exec",
        "description": "Execute a command on tony-dell",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "working_dir": {"type": "string"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "remote_read",
        "description": "Read a file from tony-dell",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "remote_write",
        "description": "Write content to a file on tony-dell",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "remote_list",
        "description": "List contents of a directory on tony-dell",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string"}
            },
            "required": ["directory"]
        }
    },
    {
        "name": "get_status",
        "description": "Get the status of tony-dell",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

TOOL_HANDLERS = {
    "remote_exec": remote_exec,
    "remote_read": remote_read,
    "remote_write": remote_write,
    "remote_list": remote_list,
    "get_status": get_status
}

def send_response(response: Any):
    """Send a JSON-RPC response to stdout."""
    print(json.dumps(response), flush=True)

def handle_request(request: dict):
    """Handle an incoming MCP request."""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    if method == "initialize":
        send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "remote-exec-tony-dell",
                    "version": "1.0.0"
                }
            }
        })
    elif method == "tools/list":
        send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": TOOLS
            }
        })
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        
        if tool_name in TOOL_HANDLERS:
            try:
                result = TOOL_HANDLERS[tool_name](**tool_args)
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                })
            except Exception as e:
                send_response({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32000,
                        "message": str(e)
                    }
                })
        else:
            send_response({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            })
    else:
        send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Unknown method: {method}"
            }
        })

def main():
    """Main MCP server loop."""
    logger.info("Starting local MCP server for remote execution on tony-dell")
    
    # Process requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            handle_request(request)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error handling request: {e}")

if __name__ == "__main__":
    main()
