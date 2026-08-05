"""
Remote Access Agent - Overcome physical access barriers for remote system management.
Provides automated remote service management, troubleshooting, and deployment capabilities.
"""
import subprocess
import requests
import socket
import time
from typing import Dict, List, Optional, Tuple
import json


class RemoteAccessAgent:
    """Agent for managing remote systems without physical access."""
    
    def __init__(self, remote_host: str = "tony-dell", remote_user: str = "tony"):
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.trade_url = "http://tony-omen.local:8080/apps/trade/"
        self.api_url = "http://tony-omen.local:8080/apps/trade/api"
    
    def check_ssh_connection(self) -> bool:
        """Check if SSH connection to remote host is available."""
        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", f"{self.remote_user}@{self.remote_host}", "echo 'SSH OK'"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "SSH OK" in result.stdout:
                print(f"✅ SSH connection to {self.remote_host} successful")
                return True
            else:
                print(f"❌ SSH connection to {self.remote_host} failed")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ SSH connection to {self.remote_host} timed out")
            return False
        except Exception as e:
            print(f"❌ SSH connection error: {e}")
            return False
    
    def execute_remote_command(self, command: str) -> Tuple[bool, str]:
        """
        Execute a command on the remote host via SSH.
        
        Args:
            command: Command to execute remotely
            
        Returns:
            Tuple of (success, output)
        """
        try:
            full_command = f"ssh {self.remote_user}@{self.remote_host} '{command}'"
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def check_remote_service_status(self, service_name: str) -> Dict:
        """
        Check if a service is running on the remote host.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            Service status information
        """
        status = {
            "service": service_name,
            "running": False,
            "enabled": False,
            "error": None
        }
        
        try:
            # Check if service is running
            success, output = self.execute_remote_command(f"systemctl is-active {service_name}")
            if success and "active" in output.lower():
                status["running"] = True
            
            # Check if service is enabled
            success, output = self.execute_remote_command(f"systemctl is-enabled {service_name}")
            if success and "enabled" in output.lower():
                status["enabled"] = True
            
            print(f"✅ Service {service_name}: running={status['running']}, enabled={status['enabled']}")
            
        except Exception as e:
            status["error"] = str(e)
            print(f"❌ Error checking service {service_name}: {e}")
        
        return status
    
    def restart_remote_service(self, service_name: str) -> bool:
        """
        Restart a service on the remote host.
        
        Args:
            service_name: Name of the service to restart
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success, output = self.execute_remote_command(f"sudo systemctl restart {service_name}")
            
            if success:
                print(f"✅ Service {service_name} restarted successfully")
                return True
            else:
                print(f"❌ Failed to restart service {service_name}: {output}")
                return False
                
        except Exception as e:
            print(f"❌ Error restarting service {service_name}: {e}")
            return False
    
    def check_remote_docker_containers(self) -> List[Dict]:
        """
        Check Docker containers on the remote host.
        
        Returns:
            List of container information
        """
        containers = []
        
        try:
            success, output = self.execute_remote_command("docker ps --format json")
            
            if success and output:
                try:
                    container_data = json.loads(output)
                    for container in container_data:
                        containers.append({
                            "id": container.get("ID", "")[:12],
                            "name": container.get("Names", ""),
                            "status": container.get("Status", ""),
                            "ports": container.get("Ports", "")
                        })
                    
                    print(f"✅ Found {len(containers)} running containers")
                    
                except json.JSONDecodeError:
                    # Fallback to text format
                    success, output = self.execute_remote_command("docker ps")
                    if success:
                        lines = output.split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 4:
                                    containers.append({
                                        "id": parts[0][:12],
                                        "name": parts[-1],
                                        "status": parts[3],
                                        "ports": parts[4] if len(parts) > 4 else ""
                                    })
                        print(f"✅ Found {len(containers)} running containers")
            
        except Exception as e:
            print(f"❌ Error checking Docker containers: {e}")
        
        return containers
    
    def check_network_connectivity(self, host: str, port: int) -> bool:
        """
        Check network connectivity to a host and port.
        
        Args:
            host: Host to check
            port: Port to check
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} is accessible")
                return True
            else:
                print(f"❌ {host}:{port} is not accessible")
                return False
                
        except Exception as e:
            print(f"❌ Network check error: {e}")
            return False
    
    def check_trade_page_status(self) -> Dict:
        """
        Check the status of the trade page.
        
        Returns:
            Status information
        """
        status = {
            "url": self.trade_url,
            "accessible": False,
            "status_code": None,
            "error": None,
            "suggestions": []
        }
        
        try:
            response = requests.get(self.trade_url, timeout=10)
            status["status_code"] = response.status_code
            status["accessible"] = response.status_code == 200
            
            if response.status_code == 200:
                print(f"✅ Trade page accessible (status: {response.status_code})")
            else:
                print(f"⚠️ Trade page returned status: {response.status_code}")
                status["suggestions"].append("Check if the trade service is running")
                status["suggestions"].append("Verify the URL path is correct")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Trade page connection refused")
            status["error"] = "Connection refused"
            status["suggestions"].append("Check if the web server is running")
            status["suggestions"].append("Verify port 8080 is accessible")
            status["suggestions"].append("Check network connectivity to tony-omen.local")
            
        except requests.exceptions.Timeout:
            print(f"❌ Trade page request timed out")
            status["error"] = "Request timeout"
            status["suggestions"].append("Check if the web server is responding")
            status["suggestions"].append("Verify network connectivity")
            
        except Exception as e:
            print(f"❌ Trade page error: {e}")
            status["error"] = str(e)
        
        return status
    
    def check_api_status(self) -> Dict:
        """
        Check the status of the trade API.
        
        Returns:
            API status information
        """
        status = {
            "url": self.api_url,
            "accessible": False,
            "status_code": None,
            "error": None
        }
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            status["status_code"] = response.status_code
            status["accessible"] = response.status_code == 200
            
            if response.status_code == 200:
                print(f"✅ API health endpoint accessible")
                try:
                    health_data = response.json()
                    status["health_data"] = health_data
                    print(f"   Health: {health_data}")
                except:
                    pass
            else:
                print(f"⚠️ API returned status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ API connection refused")
            status["error"] = "Connection refused"
            
        except requests.exceptions.Timeout:
            print(f"❌ API request timed out")
            status["error"] = "Request timeout"
            
        except Exception as e:
            print(f"❌ API error: {e}")
            status["error"] = str(e)
        
        return status
    
    def diagnose_trade_page_issue(self) -> Dict:
        """
        Comprehensive diagnosis of trade page issues.
        
        Returns:
            Diagnosis results with recommendations
        """
        diagnosis = {
            "network_connectivity": {},
            "trade_page_status": {},
            "api_status": {},
            "remote_services": {},
            "recommendations": []
        }
        
        print("=" * 60)
        print("TRADE PAGE DIAGNOSIS")
        print("=" * 60)
        
        # Step 1: Check network connectivity
        print("\n🔍 Step 1: Checking network connectivity...")
        diagnosis["network_connectivity"]["tony_omen_8080"] = self.check_network_connectivity("tony-omen.local", 8080)
        diagnosis["network_connectivity"]["localhost_8080"] = self.check_network_connectivity("localhost", 8080)
        
        # Step 2: Check trade page status
        print("\n🔍 Step 2: Checking trade page status...")
        diagnosis["trade_page_status"] = self.check_trade_page_status()
        
        # Step 3: Check API status
        print("\n🔍 Step 3: Checking API status...")
        diagnosis["api_status"] = self.check_api_status()
        
        # Step 4: Check remote services (if SSH available)
        print("\n🔍 Step 4: Checking remote services...")
        if self.check_ssh_connection():
            diagnosis["remote_services"]["containers"] = self.check_remote_docker_containers()
            
            # Check for web-related containers
            web_containers = [c for c in diagnosis["remote_services"]["containers"] 
                            if "web" in c["name"].lower() or "caddy" in c["name"].lower()]
            
            if web_containers:
                print(f"Found {len(web_containers)} web-related containers:")
                for container in web_containers:
                    print(f"  - {container['name']}: {container['status']}")
            else:
                print("❌ No web-related containers found")
                diagnosis["recommendations"].append("Start the web server container")
        else:
            print("⚠️ SSH not available, skipping remote service checks")
            diagnosis["recommendations"].append("Check SSH connectivity to remote host")
        
        # Step 5: Generate recommendations
        print("\n🔍 Step 5: Generating recommendations...")
        
        if not diagnosis["network_connectivity"]["tony_omen_8080"]:
            diagnosis["recommendations"].append("Network connectivity to tony-omen.local:8080 failed")
            diagnosis["recommendations"].append("Check if tony-omen.local is accessible")
            diagnosis["recommendations"].append("Verify DNS resolution for tony-omen.local")
        
        if not diagnosis["trade_page_status"]["accessible"]:
            diagnosis["recommendations"].append("Trade page is not accessible")
            diagnosis["recommendations"].append("Check if the web server is running on port 8080")
            diagnosis["recommendations"].append("Verify the /apps/trade/ path exists in the web server")
        
        if not diagnosis["api_status"]["accessible"]:
            diagnosis["recommendations"].append("API is not accessible")
            diagnosis["recommendations"].append("Start the API server")
            diagnosis["recommendations"].append("Check API server logs for errors")
        
        return diagnosis
    
    def deploy_to_remote(self, local_path: str, remote_path: str) -> bool:
        """
        Deploy files to remote host via SCP.
        
        Args:
            local_path: Local file/directory path
            remote_path: Remote destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["scp", "-r", local_path, f"{self.remote_user}@{self.remote_host}:{remote_path}"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully deployed {local_path} to {remote_path}")
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def restart_trade_services(self) -> bool:
        """
        Restart trade-related services on remote host.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Restart web server
            print("Restarting web server...")
            if self.restart_remote_service("web"):
                time.sleep(2)
            
            # Restart API if needed
            print("Restarting API server...")
            if self.restart_remote_service("trade-api"):
                time.sleep(2)
            
            print("✅ Trade services restarted")
            return True
            
        except Exception as e:
            print(f"❌ Error restarting trade services: {e}")
            return False


def main():
    """Main function for testing the remote access agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Remote Access Agent for barrier-free system management")
    parser.add_argument("task", choices=["diagnose", "check-service", "restart-service", "check-containers", "deploy"])
    parser.add_argument("--service", help="Service name to check/restart")
    parser.add_argument("--local", help="Local path for deployment")
    parser.add_argument("--remote", help="Remote path for deployment")
    
    args = parser.parse_args()
    
    agent = RemoteAccessAgent()
    
    if args.task == "diagnose":
        diagnosis = agent.diagnose_trade_page_issue()
        
        print("\n" + "=" * 60)
        print("DIAGNOSIS RESULTS")
        print("=" * 60)
        print(f"Network Connectivity: {diagnosis['network_connectivity']}")
        print(f"Trade Page Status: {diagnosis['trade_page_status']}")
        print(f"API Status: {diagnosis['api_status']}")
        print(f"Remote Services: {diagnosis['remote_services']}")
        print(f"\nRecommendations:")
        for rec in diagnosis['recommendations']:
            print(f"  - {rec}")
    
    elif args.task == "check-service":
        if not args.service:
            print("❌ --service is required for check-service task")
            return
        
        status = agent.check_remote_service_status(args.service)
        print(f"Service Status: {status}")
    
    elif args.task == "restart-service":
        if not args.service:
            print("❌ --service is required for restart-service task")
            return
        
        if agent.restart_remote_service(args.service):
            print("✅ Service restarted successfully")
        else:
            print("❌ Service restart failed")
    
    elif args.task == "check-containers":
        containers = agent.check_remote_docker_containers()
        print(f"Found {len(containers)} containers:")
        for container in containers:
            print(f"  - {container['name']}: {container['status']}")
    
    elif args.task == "deploy":
        if not args.local or not args.remote:
            print("❌ --local and --remote are required for deploy task")
            return
        
        if agent.deploy_to_remote(args.local, args.remote):
            print("✅ Deployment successful")
        else:
            print("❌ Deployment failed")


if __name__ == "__main__":
    main()