"""
Startup script for FastAPI trading data API.
Supports development and production modes.
"""
import os
import sys
import signal
import argparse
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api import app


def load_config(config_path: str = None) -> dict:
    """Load API configuration from YAML file."""
    if config_path is None:
        config_path = project_root / "config" / "api.yml"
    
    if not Path(config_path).exists():
        print(f"Config file not found: {config_path}, using defaults")
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_server(mode: str = "production", config: dict = None):
    """
    Run the FastAPI server.
    
    Args:
        mode: 'development' or 'production'
        config: Configuration dictionary
    """
    if config is None:
        config = {}
    
    server_config = config.get('server', {})
    cors_config = config.get('cors', {})
    
    # Get server settings from config or environment variables
    host = os.getenv('API_HOST', server_config.get('host', '0.0.0.0'))
    port = int(os.getenv('API_PORT', server_config.get('port', 8000)))
    workers = int(os.getenv('API_WORKERS', server_config.get('workers', 1)))
    log_level = os.getenv('API_LOG_LEVEL', server_config.get('log_level', 'info'))
    
    # Development mode settings
    if mode == "development":
        reload = True
        workers = 1
        log_level = "debug"
        print("Running in DEVELOPMENT mode with auto-reload")
    else:
        reload = server_config.get('reload', False)
        print(f"Running in PRODUCTION mode with {workers} worker(s)")
    
    # Print configuration
    print(f"Starting FastAPI server on {host}:{port}")
    print(f"Log level: {log_level}")
    print(f"Workers: {workers}")
    print(f"Auto-reload: {reload}")
    print(f"Swagger UI: http://{host}:{port}/docs")
    print(f"ReDoc: http://{host}:{port}/redoc")
    print()
    
    # Configure uvicorn
    uvicorn_config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        workers=workers if not reload else None,
        reload=reload,
        log_level=log_level,
        access_log=True,
    )
    
    server = uvicorn.Server(uvicorn_config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        server.should_exit = True
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run server
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
    finally:
        print("Server shutdown complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Trading Data API server"
    )
    parser.add_argument(
        '--mode',
        choices=['development', 'production'],
        default='production',
        help='Server mode (default: production)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/api.yml)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='Override host'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Override port'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command-line arguments if provided
    if args.host:
        os.environ['API_HOST'] = args.host
    if args.port:
        os.environ['API_PORT'] = str(args.port)
    
    # Run server
    run_server(mode=args.mode, config=config)


if __name__ == "__main__":
    main()
