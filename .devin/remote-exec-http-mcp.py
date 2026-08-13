#!/usr/bin/env python3
"""
HTTP to MCP protocol translator for remote-exec server
Translates MCP stdio protocol to HTTP requests to tony-dell
"""

import json
import sys
import urllib.request
import urllib.error

BASE_URL = "http://tony-dell.local:8080"

def send_http_request(endpoint, data=None):
    """Send HTTP request to remote server."""
    try:
        if data:
            request_data = json.dumps(data).encode()
        else:
            request_data = json.dumps({}).encode()
        
        req = urllib.request.Request(
            f"{BASE_URL}{endpoint}",
            data=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {e}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main MCP protocol loop."""
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "remote-exec-tony-dell", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                tools_result = send_http_request("/tools/list")
                if "error" in tools_result:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32000, "message": tools_result["error"]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": tools_result
                    }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = send_http_request(f"/tools/call/{tool_name}", tool_args)
                if "error" in result:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32000, "message": result["error"]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                }
            
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {e}"}}), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}}), flush=True)

if __name__ == "__main__":
    main()
