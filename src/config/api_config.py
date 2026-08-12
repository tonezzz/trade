"""
API configuration management.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
import yaml
import os


class APIConfig(BaseModel):
    """API server configuration."""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 9000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"
    
    # CORS settings
    cors_enabled: bool = True
    allow_origins: List[str] = Field(default_factory=lambda: ["http://localhost:8080"])
    allow_credentials: bool = True
    allow_methods: List[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allow_headers: List[str] = Field(default_factory=lambda: ["Content-Type", "Authorization"])
    
    # Rate limiting
    rate_limiting_enabled: bool = False
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # API documentation
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Response settings
    default_limit: int = 1000
    max_limit: int = 10000
    include_metadata: bool = True
    
    # Cache settings
    cache_enabled: bool = False
    cache_ttl: int = 300  # 5 minutes
    
    # WebSocket settings
    websocket_enabled: bool = True
    websocket_polling_interval: int = 5
    websocket_max_connections: int = 100
    websocket_heartbeat_interval: int = 30
    
    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> 'APIConfig':
        """
        Load API configuration from YAML file.
        
        Args:
            config_path: Path to config file (default: config/api.yml)
            
        Returns:
            APIConfig instance
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'api.yml'
            )
        
        default_config = cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if config_data:
                # Update server settings
                if 'server' in config_data:
                    server = config_data['server']
                    default_config.host = server.get('host', default_config.host)
                    default_config.port = server.get('port', default_config.port)
                    default_config.workers = server.get('workers', default_config.workers)
                    default_config.reload = server.get('reload', default_config.reload)
                    default_config.log_level = server.get('log_level', default_config.log_level)
                
                # Update CORS settings
                if 'cors' in config_data:
                    cors = config_data['cors']
                    default_config.cors_enabled = cors.get('enabled', default_config.cors_enabled)
                    default_config.allow_origins = cors.get('allow_origins', default_config.allow_origins)
                    default_config.allow_credentials = cors.get('allow_credentials', default_config.allow_credentials)
                    default_config.allow_methods = cors.get('allow_methods', default_config.allow_methods)
                    default_config.allow_headers = cors.get('allow_headers', default_config.allow_headers)
                
                # Update rate limiting
                if 'rate_limiting' in config_data:
                    rate_limit = config_data['rate_limiting']
                    default_config.rate_limiting_enabled = rate_limit.get('enabled', default_config.rate_limiting_enabled)
                    default_config.requests_per_minute = rate_limit.get('requests_per_minute', default_config.requests_per_minute)
                    default_config.requests_per_hour = rate_limit.get('requests_per_hour', default_config.requests_per_hour)
                
                # Update docs settings
                if 'docs' in config_data:
                    docs = config_data['docs']
                    default_config.docs_enabled = docs.get('enabled', default_config.docs_enabled)
                    default_config.docs_url = docs.get('docs_url', default_config.docs_url)
                    default_config.redoc_url = docs.get('redoc_url', default_config.redoc_url)
                    default_config.openapi_url = docs.get('openapi_url', default_config.openapi_url)
                
                # Update response settings
                if 'response' in config_data:
                    response = config_data['response']
                    default_config.default_limit = response.get('default_limit', default_config.default_limit)
                    default_config.max_limit = response.get('max_limit', default_config.max_limit)
                    default_config.include_metadata = response.get('include_metadata', default_config.include_metadata)
                
                # Update WebSocket settings
                if 'websocket' in config_data:
                    websocket = config_data['websocket']
                    default_config.websocket_enabled = websocket.get('enabled', default_config.websocket_enabled)
                    if 'polling' in websocket:
                        default_config.websocket_polling_interval = websocket['polling'].get('exchange_rate_interval', default_config.websocket_polling_interval)
                    if 'performance' in websocket:
                        default_config.websocket_heartbeat_interval = websocket['performance'].get('heartbeat_interval', default_config.websocket_heartbeat_interval)
        
        except Exception as e:
            print(f"Warning: Failed to load API config from {config_path}: {e}")
            print("Using default API configuration")
        
        return default_config
