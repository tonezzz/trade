"""
Data sources configuration management.
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from pydantic import BaseModel, Field
import yaml
import os


class DataSourcesConfig(BaseModel):
    """Data sources configuration."""
    
    # Global settings
    download_dir: str = "data/archive"
    import_dir: str = "data/imported"
    max_retries: int = 3
    retry_delay: int = 5
    dry_run: bool = False
    log_file: str = "logs/automation.log"
    enable_notifications: bool = False
    notification_email: str = ""
    skip_validation: bool = True
    
    # Data quality settings
    data_quality_enabled: bool = True
    data_quality_tolerance_pct: float = 2.0
    data_quality_max_freshness_days: int = 2
    data_quality_min_completeness_pct: float = 90.0
    data_quality_alert_threshold: int = 3
    
    # Tolerance settings
    tolerance_thb: int = 2
    tolerance_dxy: int = 30
    tolerance_commodities: int = 90
    tolerance_currencies: int = 7
    
    # Catch-up settings
    catch_up_enabled: bool = True
    catch_up_on_startup: bool = True
    catch_up_max_gap_days: int = 30
    catch_up_check_interval_hours: int = 6
    
    # Rate limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 60
    
    # Data validation
    validate_price_ranges: bool = True
    validate_date_sequences: bool = True
    min_data_points: int = 1000
    max_gap_days: int = 7
    require_ohlc: bool = False
    
    # Data sources (will be populated from YAML)
    data_sources: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> 'DataSourcesConfig':
        """
        Load data sources configuration from YAML file.
        
        Args:
            config_path: Path to config file (default: config/ssot/ssot.data.yml)
            
        Returns:
            DataSourcesConfig instance
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'data_sources.yml'
            )
        
        default_config = cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if config_data:
                # Update global settings
                if 'settings' in config_data:
                    settings = config_data['settings']
                    default_config.download_dir = settings.get('download_dir', default_config.download_dir)
                    default_config.import_dir = settings.get('import_dir', default_config.import_dir)
                    default_config.max_retries = settings.get('max_retries', default_config.max_retries)
                    default_config.retry_delay = settings.get('retry_delay', default_config.retry_delay)
                    default_config.dry_run = settings.get('dry_run', default_config.dry_run)
                    default_config.log_file = settings.get('log_file', default_config.log_file)
                    default_config.enable_notifications = settings.get('enable_notifications', default_config.enable_notifications)
                    default_config.notification_email = settings.get('notification_email', default_config.notification_email)
                    default_config.skip_validation = settings.get('skip_validation', default_config.skip_validation)
                    
                    # Data quality settings
                    if 'data_quality' in settings:
                        dq = settings['data_quality']
                        default_config.data_quality_enabled = dq.get('enabled', default_config.data_quality_enabled)
                        default_config.data_quality_tolerance_pct = dq.get('tolerance_pct', default_config.data_quality_tolerance_pct)
                        default_config.data_quality_max_freshness_days = dq.get('max_freshness_days', default_config.data_quality_max_freshness_days)
                        default_config.data_quality_min_completeness_pct = dq.get('min_completeness_pct', default_config.data_quality_min_completeness_pct)
                        default_config.data_quality_alert_threshold = dq.get('alert_threshold', default_config.data_quality_alert_threshold)
                    
                    # Tolerance settings
                    if 'tolerance' in settings:
                        tolerance = settings['tolerance']
                        default_config.tolerance_thb = tolerance.get('thb', default_config.tolerance_thb)
                        default_config.tolerance_dxy = tolerance.get('dxy', default_config.tolerance_dxy)
                        default_config.tolerance_commodities = tolerance.get('commodities', default_config.tolerance_commodities)
                        default_config.tolerance_currencies = tolerance.get('currencies', default_config.tolerance_currencies)
                    
                    # Catch-up settings
                    if 'catch_up' in settings:
                        catch_up = settings['catch_up']
                        default_config.catch_up_enabled = catch_up.get('enabled', default_config.catch_up_enabled)
                        default_config.catch_up_on_startup = catch_up.get('on_startup', default_config.catch_up_on_startup)
                        default_config.catch_up_max_gap_days = catch_up.get('max_gap_days', default_config.catch_up_max_gap_days)
                        default_config.catch_up_check_interval_hours = catch_up.get('check_interval_hours', default_config.catch_up_check_interval_hours)
                    
                    # Rate limiting
                    default_config.rate_limit_requests = settings.get('rate_limit_requests', default_config.rate_limit_requests)
                    default_config.rate_limit_period = settings.get('rate_limit_period', default_config.rate_limit_period)
                    
                    # Data validation
                    default_config.validate_price_ranges = settings.get('validate_price_ranges', default_config.validate_price_ranges)
                    default_config.validate_date_sequences = settings.get('validate_date_sequences', default_config.validate_date_sequences)
                    default_config.min_data_points = settings.get('min_data_points', default_config.min_data_points)
                    default_config.max_gap_days = settings.get('max_gap_days', default_config.max_gap_days)
                    default_config.require_ohlc = settings.get('require_ohlc', default_config.require_ohlc)
                
                # Store data sources
                if 'data_sources' in config_data:
                    default_config.data_sources = config_data['data_sources']
        
        except Exception as e:
            print(f"Warning: Failed to load data sources config from {config_path}: {e}")
            print("Using default data sources configuration")
        
        return default_config
    
    def get_enabled_data_sources(self) -> List[str]:
        """Get list of enabled data source IDs."""
        return [
            source_id for source_id, config in self.data_sources.items()
            if config.get('enabled', True)
        ]
    
    def get_data_source_config(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific data source."""
        return self.data_sources.get(source_id)


class DataSourceCatalog:
    """Read-only catalog helper for config/ssot/ssot.datasource-catalog.yml."""
    
    _catalog: Optional[Dict[str, Any]] = None
    
    @classmethod
    def _load(cls) -> Dict[str, Any]:
        """Load (and cache) the datasource catalog."""
        if cls._catalog is not None:
            return cls._catalog
        
        project_root = Path(__file__).resolve().parents[2]
        catalog_path = project_root / 'config' / 'ssot' / 'ssot.datasource-catalog.yml'
        
        try:
            with open(catalog_path, 'r') as f:
                cls._catalog = yaml.safe_load(f) or {}
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to load datasource catalog {catalog_path}: {e}")
            cls._catalog = {}
        
        return cls._catalog
    
    @classmethod
    def get_validation_endpoint(cls, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a validation source endpoint by catalog key or name."""
        catalog = cls._load()
        for key, source in catalog.get('validation_sources', {}).items():
            if key == name or source.get('name') == name:
                return source.get('endpoint', default)
        return default
    
    @classmethod
    def get_operational_endpoint(cls, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get an operational source endpoint by catalog key."""
        catalog = cls._load()
        source = catalog.get('operational_sources', {}).get(name)
        if source and isinstance(source, dict):
            return source.get('endpoint', default)
        return default
    
    @classmethod
    def get_policy(cls, category: str, key: str, default: Any = None) -> Any:
        """Get a value from data_source_policy (e.g. get_policy('dxy', 'series_id'))."""
        catalog = cls._load()
        return catalog.get('data_source_policy', {}).get(category, {}).get(key, default)
