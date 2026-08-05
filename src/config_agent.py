"""
Configuration Agent - Automates repetitive configuration and credential tasks.
Combines Docker inspection with browser verification using playlive MCP server.
"""
import subprocess
import json
import re
from typing import Dict, Optional, List


class ConfigAgent:
    """Agent for handling repetitive configuration and credential tasks."""
    
    def __init__(self):
        self.playlive_server = "playlive.tony-dell"
    
    def get_docker_postgres_password(self, container_name: str = "postgres") -> Optional[str]:
        """
        Extract PostgreSQL password from Docker container environment variables.
        
        Args:
            container_name: Name of the PostgreSQL container
            
        Returns:
            Password if found, None otherwise
        """
        try:
            # Get container environment variables
            result = subprocess.run(
                ["docker", "inspect", container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Container {container_name} not found")
                return None
            
            inspect_data = json.loads(result.stdout)
            env_vars = inspect_data[0]["Config"]["Env"]
            
            # Find POSTGRES_PASSWORD
            for env_var in env_vars:
                if env_var.startswith("POSTGRES_PASSWORD="):
                    password = env_var.split("=", 1)[1]
                    print(f"✅ Found POSTGRES_PASSWORD: {password}")
                    return password
            
            print("❌ POSTGRES_PASSWORD not found in container environment")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting password: {e}")
            return None
    
    def get_all_docker_env_vars(self, container_name: str = "postgres") -> Dict[str, str]:
        """
        Get all environment variables from a Docker container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Dictionary of environment variables
        """
        try:
            result = subprocess.run(
                ["docker", "inspect", container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {}
            
            inspect_data = json.loads(result.stdout)
            env_vars = inspect_data[0]["Config"]["Env"]
            
            env_dict = {}
            for env_var in env_vars:
                if "=" in env_var:
                    key, value = env_var.split("=", 1)
                    env_dict[key] = value
            
            return env_dict
            
        except Exception as e:
            print(f"❌ Error getting environment variables: {e}")
            return {}
    
    def test_database_connection(self, host: str = "localhost", port: str = "5432", 
                                database: str = "trade", user: str = "chaba", 
                                password: str = "") -> bool:
        """
        Test database connection with given credentials.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            import psycopg2
            
            conn_string = f"host={host} port={port} dbname={database} user={user}"
            if password:
                conn_string += f" password={password}"
            
            conn = psycopg2.connect(conn_string)
            conn.close()
            
            print(f"✅ Database connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def verify_env_file(self, env_path: str = ".env") -> Dict[str, str]:
        """
        Verify .env file configuration and return current values.
        
        Args:
            env_path: Path to .env file
            
        Returns:
            Dictionary of current environment variables
        """
        env_vars = {}
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
            
            print(f"✅ Found {len(env_vars)} environment variables in {env_path}")
            return env_vars
            
        except FileNotFoundError:
            print(f"❌ {env_path} not found")
            return {}
        except Exception as e:
            print(f"❌ Error reading {env_path}: {e}")
            return {}
    
    def suggest_env_update(self, current_env: Dict[str, str], 
                         docker_password: Optional[str] = None) -> List[str]:
        """
        Suggest updates to .env file based on Docker configuration.
        
        Args:
            current_env: Current environment variables
            docker_password: Password from Docker container
            
        Returns:
            List of suggested updates
        """
        suggestions = []
        
        # Check database configuration
        db_name = current_env.get("DB_NAME", "")
        db_user = current_env.get("DB_USER", "")
        db_password = current_env.get("DB_PASSWORD", "")
        
        if db_name != "trade":
            suggestions.append(f"DB_NAME should be 'trade' (currently: {db_name})")
        
        if db_user != "chaba":
            suggestions.append(f"DB_USER should be 'chaba' (currently: {db_user})")
        
        if docker_password and db_password != docker_password:
            suggestions.append(f"DB_PASSWORD should be '{docker_password}' (currently: {db_password})")
        
        return suggestions
    
    def check_service_status(self, service_name: str, container_name: str = None) -> Dict:
        """
        Check if a service is running via Docker.
        
        Args:
            service_name: Name of the service
            container_name: Optional container name to check
            
        Returns:
            Status information
        """
        status = {
            "running": False,
            "container_name": None,
            "status": None,
            "error": None
        }
        
        try:
            if container_name:
                result = subprocess.run(
                    ["docker", "inspect", "--format='{{.State.Status}}'", container_name],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    status["running"] = result.stdout.strip() == "running"
                    status["container_name"] = container_name
                    status["status"] = result.stdout.strip()
                else:
                    status["error"] = f"Container {container_name} not found"
            else:
                # Try to find container by name pattern
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True
                )
                
                containers = result.stdout.strip().split('\n')
                matching = [c for c in containers if service_name.lower() in c.lower()]
                
                if matching:
                    status["running"] = True
                    status["container_name"] = matching[0]
                else:
                    status["error"] = f"No container found matching {service_name}"
                    
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def verify_web_service(self, url: str) -> Dict:
        """
        Verify if a web service is accessible using playlive browser automation.
        
        Args:
            url: URL to check
            
        Returns:
            Status information
        """
        status = {
            "accessible": False,
            "status_code": None,
            "error": None
        }
        
        try:
            from mcp_call_tool import mcp_call_tool
            
            # Create browser session
            session_result = mcp_call_tool(
                server_name=self.playlive_server,
                tool_name="playlive_create_chrome_live",
                arguments={"target": "remote"}
            )
            
            if not session_result or "session_id" not in session_result:
                status["error"] = "Failed to create browser session"
                return status
            
            session_id = session_result["session_id"]
            
            # Navigate to URL
            nav_result = mcp_call_tool(
                server_name=self.playlive_server,
                tool_name="playlive_navigate",
                arguments={"session_id": session_id, "url": url}
            )
            
            # Close session
            mcp_call_tool(
                server_name=self.playlive_server,
                tool_name="playlive_close_session",
                arguments={"session_id": session_id}
            )
            
            if nav_result and nav_result.get("ok"):
                status["accessible"] = True
            else:
                status["error"] = nav_result.get("error", "Navigation failed")
                
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def diagnose_database_issue(self) -> Dict:
        """
        Comprehensive diagnosis of database configuration issues.
        
        Returns:
            Diagnosis results with recommendations
        """
        diagnosis = {
            "docker_password": None,
            "env_config": {},
            "connection_test": False,
            "recommendations": []
        }
        
        # Step 1: Get Docker password
        print("🔍 Step 1: Checking Docker container for PostgreSQL password...")
        diagnosis["docker_password"] = self.get_docker_postgres_password()
        
        # Step 2: Check current .env configuration
        print("\n🔍 Step 2: Checking .env file configuration...")
        diagnosis["env_config"] = self.verify_env_file()
        
        # Step 3: Test connection with Docker password
        if diagnosis["docker_password"]:
            print("\n🔍 Step 3: Testing connection with Docker password...")
            diagnosis["connection_test"] = self.test_database_connection(
                password=diagnosis["docker_password"]
            )
        
        # Step 4: Generate recommendations
        print("\n🔍 Step 4: Generating recommendations...")
        diagnosis["recommendations"] = self.suggest_env_update(
            diagnosis["env_config"],
            diagnosis["docker_password"]
        )
        
        return diagnosis
    
    def auto_fix_env_file(self, env_path: str = ".env", docker_password: Optional[str] = None) -> bool:
        """
        Automatically fix .env file with correct configuration.
        
        Args:
            env_path: Path to .env file
            docker_password: Password from Docker container
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read current .env
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update configuration
            updated_lines = []
            for line in lines:
                if line.startswith("DB_NAME="):
                    updated_lines.append("DB_NAME=trade\n")
                elif line.startswith("DB_USER="):
                    updated_lines.append("DB_USER=chaba\n")
                elif line.startswith("DB_PASSWORD=") and docker_password:
                    updated_lines.append(f"DB_PASSWORD={docker_password}\n")
                else:
                    updated_lines.append(line)
            
            # Write updated .env
            with open(env_path, 'w') as f:
                f.writelines(updated_lines)
            
            print(f"✅ Updated {env_path} with correct configuration")
            return True
            
        except Exception as e:
            print(f"❌ Error updating {env_path}: {e}")
            return False


def main():
    """Main function for testing the configuration agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuration Agent for repetitive tasks")
    parser.add_argument("task", choices=["diagnose", "fix-env", "test-connection", "check-service"])
    parser.add_argument("--container", default="postgres", help="Docker container name")
    parser.add_argument("--url", help="URL to check for web service")
    
    args = parser.parse_args()
    
    agent = ConfigAgent()
    
    if args.task == "diagnose":
        print("=" * 60)
        print("DATABASE CONFIGURATION DIAGNOSIS")
        print("=" * 60)
        diagnosis = agent.diagnose_database_issue()
        
        print("\n" + "=" * 60)
        print("DIAGNOSIS RESULTS")
        print("=" * 60)
        print(f"Docker Password: {diagnosis['docker_password']}")
        print(f"Current .env: {diagnosis['env_config']}")
        print(f"Connection Test: {diagnosis['connection_test']}")
        print(f"\nRecommendations:")
        for rec in diagnosis['recommendations']:
            print(f"  - {rec}")
    
    elif args.task == "fix-env":
        password = agent.get_docker_postgres_password(args.container)
        if password:
            if agent.auto_fix_env_file(docker_password=password):
                print("✅ .env file updated successfully")
            else:
                print("❌ Failed to update .env file")
        else:
            print("❌ Could not find Docker password")
    
    elif args.task == "test-connection":
        password = agent.get_docker_postgres_password(args.container)
        if password:
            if agent.test_database_connection(password=password):
                print("✅ Connection successful")
            else:
                print("❌ Connection failed")
        else:
            print("❌ Could not find Docker password")
    
    elif args.task == "check-service":
        if args.url:
            status = agent.verify_web_service(args.url)
            print(f"URL: {args.url}")
            print(f"Accessible: {status['accessible']}")
            print(f"Error: {status['error']}")
        else:
            print("❌ --url is required for check-service task")


if __name__ == "__main__":
    main()