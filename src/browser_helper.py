"""
Browser automation helper for repetitive configuration tasks.
Uses playlive MCP server for web automation.
"""
import sys
import json
from typing import Dict, Optional, List


class BrowserHelper:
    """Helper class for browser automation tasks using playlive MCP server."""
    
    def __init__(self, mcp_server: str = "playlive.tony-dell"):
        self.mcp_server = mcp_server
        self.session_id: Optional[str] = None
    
    def create_session(self, target: str = "local", remote_url: Optional[str] = None) -> str:
        """Create a browser session."""
        from mcp_call_tool import mcp_call_tool
        
        result = mcp_call_tool(
            server_name=self.mcp_server,
            tool_name="playlive_create_playwright",
            arguments={
                "target": target,
                "remote_url": remote_url
            }
        )
        
        if result and "result" in result:
            self.session_id = result["result"]
            return self.session_id
        else:
            raise Exception("Failed to create browser session")
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if not self.session_id:
            raise Exception("No active session. Call create_session first.")
        
        from mcp_call_tool import mcp_call_tool
        
        result = mcp_call_tool(
            server_name=self.mcp_server,
            tool_name="playlive_navigate",
            arguments={
                "session_id": self.session_id,
                "url": url
            }
        )
        
        return result and "result" in result
    
    def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        if not self.session_id:
            raise Exception("No active session. Call create_session first.")
        
        from mcp_call_tool import mcp_call_tool
        
        result = mcp_call_tool(
            server_name=self.mcp_server,
            tool_name="playlive_eval",
            arguments={
                "session_id": self.session_id,
                "script": f"document.querySelector('{selector}').textContent"
            }
        )
        
        if result and "result" in result:
            return result["result"]
        return ""
    
    def get_all_text(self) -> str:
        """Get all text content of the page."""
        if not self.session_id:
            raise Exception("No active session. Call create_session first.")
        
        from mcp_call_tool import mcp_call_tool
        
        result = mcp_call_tool(
            server_name=self.mcp_server,
            tool_name="playlive_eval",
            arguments={
                "session_id": self.session_id,
                "script": "document.body.textContent"
            }
        )
        
        if result and "result" in result:
            return result["result"]
        return ""
    
    def find_password_in_page(self, keywords: List[str] = ["password", "pass", "postgres"]) -> Optional[str]:
        """Search page content for password-related information."""
        page_text = self.get_all_text().lower()
        
        for keyword in keywords:
            if keyword in page_text:
                # Try to extract the password value
                from mcp_call_tool import mcp_call_tool
                
                result = mcp_call_tool(
                    server_name=self.mcp_server,
                    tool_name="playlive_eval",
                    arguments={
                        "session_id": self.session_id,
                        "script": f"""
                            const text = document.body.textContent;
                            const regex = /{keyword}[\\s:=]+([\\w]+)/gi;
                            const matches = text.match(regex);
                            matches ? matches.join(', ') : 'not found';
                        """
                    }
                )
                
                if result and "result" in result:
                    return result["result"]
        
        return None
    
    def check_page_status(self, expected_content: Optional[str] = None) -> Dict:
        """Check if page is accessible and contains expected content."""
        status = {
            "accessible": False,
            "contains_expected": False,
            "page_text": "",
            "error": None
        }
        
        try:
            page_text = self.get_all_text()
            status["accessible"] = True
            status["page_text"] = page_text
            
            if expected_content and expected_content in page_text:
                status["contains_expected"] = True
                
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def close_session(self) -> bool:
        """Close the browser session."""
        if not self.session_id:
            return True
        
        from mcp_call_tool import mcp_call_tool
        
        result = mcp_call_tool(
            server_name=self.mcp_server,
            tool_name="playlive_close_session",
            arguments={
                "session_id": self.session_id
            }
        )
        
        self.session_id = None
        return result and "result" in result


def find_postgres_password(urls: List[str] = None) -> Optional[str]:
    """
    Try to find PostgreSQL password by checking multiple URLs.
    
    Args:
        urls: List of URLs to check (default: common admin URLs)
    
    Returns:
        Password if found, None otherwise
    """
    if urls is None:
        urls = [
            "http://playlive.local",
            "http://playlive.tony-dell",
            "http://localhost:8080",
            "http://tony-omen.local:8080"
        ]
    
    helper = BrowserHelper()
    
    for url in urls:
        try:
            print(f"Checking {url}...")
            helper.create_session()
            helper.navigate(url)
            
            # Check if page is accessible
            status = helper.check_page_status()
            if not status["accessible"]:
                print(f"  ❌ Not accessible")
                helper.close_session()
                continue
            
            print(f"  ✅ Accessible")
            
            # Try to find password
            password = helper.find_password_in_page()
            if password:
                print(f"  🔑 Found password info: {password}")
                helper.close_session()
                return password
            
            print(f"  ❌ No password found")
            helper.close_session()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            try:
                helper.close_session()
            except:
                pass
    
    return None


def verify_api_running(url: str = "http://localhost:8000") -> bool:
    """Verify if API server is running."""
    helper = BrowserHelper()
    
    try:
        helper.create_session()
        helper.navigate(url)
        
        status = helper.check_page_status(expected_content="FastAPI")
        helper.close_session()
        
        return status["accessible"]
        
    except Exception as e:
        print(f"Error verifying API: {e}")
        try:
            helper.close_session()
        except:
            pass
        return False


def main():
    """Main function for testing browser helper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Browser helper for configuration tasks")
    parser.add_argument("task", choices=["find-password", "verify-api", "check-url"])
    parser.add_argument("--url", help="URL to check")
    parser.add_argument("--urls", nargs="+", help="Multiple URLs to check")
    
    args = parser.parse_args()
    
    if args.task == "find-password":
        urls = args.urls if args.urls else None
        password = find_postgres_password(urls)
        if password:
            print(f"✅ Found password: {password}")
        else:
            print("❌ No password found")
    
    elif args.task == "verify-api":
        url = args.url or "http://localhost:8000"
        if verify_api_running(url):
            print(f"✅ API is running at {url}")
        else:
            print(f"❌ API is not running at {url}")
    
    elif args.task == "check-url":
        if not args.url:
            print("❌ --url is required for check-url task")
            return
        
        helper = BrowserHelper()
        try:
            helper.create_session()
            helper.navigate(args.url)
            status = helper.check_page_status()
            helper.close_session()
            
            print(f"URL: {args.url}")
            print(f"Accessible: {status['accessible']}")
            print(f"Error: {status['error']}")
            print(f"Page text preview: {status['page_text'][:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()