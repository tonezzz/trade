"""
Application settings using Pydantic for type-safe configuration.
"""
from typing import Optional, List
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings
    SettingsConfigDict = None
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Trading Data API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    db_type: str = "postgresql"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "dollar_prices"
    db_user: str = "postgres"
    db_password: str = "password"
    
    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 9000
    api_workers: int = 1
    api_reload: bool = False
    api_log_level: str = "info"
    
    # CORS
    cors_enabled: bool = True
    cors_origins: List[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # Data Quality
    data_quality_enabled: bool = True
    data_quality_tolerance_pct: float = 2.0
    data_quality_max_freshness_days: int = 2
    
    # Automation
    automation_enabled: bool = True
    automation_dry_run: bool = False
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    metal_prices_api_key: Optional[str] = None
    gold_api_key: Optional[str] = None
    
    # Additional environment variables (for compatibility)
    quality_tolerance: Optional[str] = None
    quality_freshness_days: Optional[str] = None
    quality_completeness_pct: Optional[str] = None
    
    if SettingsConfigDict:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
            extra = "ignore"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    
    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings()
    return _settings
