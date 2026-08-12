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
    db_type: str = Field(default="postgresql", env="DB_TYPE")
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="dollar_prices", env="DB_NAME")
    db_user: str = Field(default="postgres", env="DB_USER")
    db_password: str = Field(default="password", env="DB_PASSWORD")
    
    # API Server
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=9000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    api_reload: bool = Field(default=False, env="API_RELOAD")
    api_log_level: str = Field(default="info", env="API_LOG_LEVEL")
    
    # CORS
    cors_enabled: bool = Field(default=True, env="CORS_ENABLED")
    cors_origins: List[str] = Field(
        default=["http://localhost:8080", "http://127.0.0.1:8080"],
        env="CORS_ORIGINS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Data Quality
    data_quality_enabled: bool = Field(default=True, env="DATA_QUALITY_ENABLED")
    data_quality_tolerance_pct: float = Field(default=2.0, env="DATA_QUALITY_TOLERANCE_PCT")
    data_quality_max_freshness_days: int = Field(default=2, env="DATA_QUALITY_MAX_FRESHNESS_DAYS")
    
    # Automation
    automation_enabled: bool = Field(default=True, env="AUTOMATION_ENABLED")
    automation_dry_run: bool = Field(default=False, env="AUTOMATION_DRY_RUN")
    
    # External APIs
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    fred_api_key: Optional[str] = Field(default=None, env="FRED_API_KEY")
    metal_prices_api_key: Optional[str] = Field(default=None, env="METAL_PRICES_API_KEY")
    gold_api_key: Optional[str] = Field(default=None, env="GOLD_API_KEY")
    
    # Additional environment variables (for compatibility)
    quality_tolerance: Optional[str] = Field(default=None, env="DATA_QUALITY_TOLERANCE_PCT")
    quality_freshness_days: Optional[str] = Field(default=None, env="DATA_QUALITY_MAX_FRESHNESS_DAYS")
    quality_completeness_pct: Optional[str] = Field(default=None, env="DATA_QUALITY_MIN_COMPLETENESS_PCT")
    
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
