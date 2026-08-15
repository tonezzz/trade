"""
Unified data downloader using the modular data source system.
"""
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import csv
import os
from pathlib import Path

from src.data_sources.base_source import DataSourceConfig, DataSourceResult, DataSourceType
from src.data_sources.registry import get_registry, register_default_sources
from src.data_sources import (
    AlphaVantageSource, FREDSource, ECBSource, 
    MetalPricesSource, MintedMetalSource, OpenExchangeRatesSource
)
import logging


class UnifiedDataDownloader:
    """Unified data downloader using modular data sources."""
    
    def __init__(self, config_path: str = "config/ssot/ssot.data.yml"):
        """
        Initialize the unified downloader.
        
        Args:
            config_path: Path to data sources configuration file
        """
        self.config_path = config_path
        self.registry = get_registry()
        self.logger = logging.getLogger(__name__)
        
        # Register default data sources
        register_default_sources()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize data sources from config
        self._initialize_sources()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load data sources configuration from YAML file."""
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return {}
    
    def _initialize_sources(self):
        """Initialize data sources from configuration."""
        data_sources = self.config.get('data_sources', {})
        
        for source_id, source_config in data_sources.items():
            if not source_config.get('enabled', True):
                self.logger.info(f"Skipping disabled source: {source_id}")
                continue
            
            # Determine source type and create appropriate data source
            source_type = source_config.get('type')
            source_name = source_config.get('name', source_id)
            
            try:
                # Create configuration
                ds_config = DataSourceConfig(
                    name=source_name,
                    source_type=self._map_source_type(source_type),
                    enabled=True,
                    api_key=self._get_api_key(source_id),
                    base_url=source_config.get('url'),
                    timeout=self.config.get('settings', {}).get('rate_limit_period', 60),
                    max_retries=self.config.get('settings', {}).get('max_retries', 3),
                    retry_delay=self.config.get('settings', {}).get('retry_delay', 5)
                )
                
                # Create appropriate data source instance
                source_instance = self._create_source_instance(source_type, ds_config)
                
                if source_instance:
                    self.registry.add_source(source_id, source_instance)
                    self.logger.info(f"Initialized data source: {source_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize source {source_id}: {e}")
    
    def _map_source_type(self, source_type: str) -> DataSourceType:
        """Map configuration type to DataSourceType enum."""
        type_mapping = {
            'exchange_rate': DataSourceType.EXCHANGE_RATE,
            'commodity': DataSourceType.COMMODITY,
            'dollar_index': DataSourceType.DOLLAR_INDEX
        }
        return type_mapping.get(source_type, DataSourceType.COMMODITY)
    
    def _get_api_key(self, source_id: str) -> Optional[str]:
        """Get API key for a data source from environment or config."""
        import os
        
        # For Alpha Vantage sources, use the common ALPHA_VANTAGE_API_KEY
        # Check if this is an Alpha Vantage source by looking at the config
        data_sources = self.config.get('data_sources', {})
        source_config = data_sources.get(source_id, {})
        source_type = source_config.get('type')
        
        if source_type == 'commodity':
            # Alpha Vantage uses a single API key for all commodities
            api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if api_key:
                return api_key
        
        # Try environment variable first (source-specific)
        env_key = f"{source_id.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        
        if not api_key:
            # Try config file
            api_key = source_config.get('api_key')
        
        return api_key
    
    def _create_source_instance(self, source_type: str, config: DataSourceConfig):
        """Create appropriate data source instance based on type."""
        # This is a simplified version - in production, you'd map based on source config
        if source_type == 'commodity':
            # Check if this is a precious metal that needs Minted Metal API
            if config.name and 'Gold' in config.name:
                return MintedMetalSource(config)
            elif config.name and 'Silver' in config.name:
                return MintedMetalSource(config)
            else:
                return AlphaVantageSource(config)
        elif source_type == 'exchange_rate':
            # Could be FRED or ECB based on source
            return FREDSource(config)
        elif source_type == 'dollar_index':
            return FREDSource(config)
        else:
            return None
    
    def download_data(
        self,
        source_id: str,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> DataSourceResult:
        """
        Download data from a specific source.
        
        Args:
            source_id: ID of the data source
            symbol: Symbol to fetch data for
            start_date: Start date for data range
            end_date: End date for data range
            **kwargs: Additional parameters
            
        Returns:
            DataSourceResult with downloaded data
        """
        source = self.registry.get_source(source_id)
        
        if not source:
            return DataSourceResult(
                success=False,
                error=f"Data source not found: {source_id}",
                source=source_id
            )
        
        return source.fetch_data(symbol, start_date, end_date, **kwargs)
    
    def download_all_enabled(self, source_type: Optional[str] = None) -> Dict[str, DataSourceResult]:
        """
        Download data from all enabled sources.
        
        Args:
            source_type: Optional filter by source type
            
        Returns:
            Dictionary mapping source IDs to results
        """
        results = {}
        data_sources = self.config.get('data_sources', {})
        
        for source_id, source_config in data_sources.items():
            if not source_config.get('enabled', True):
                continue
            
            if source_type and source_config.get('type') != source_type:
                continue
            
            # Get symbol from config
            symbol = source_config.get('symbol') or source_config.get('commodity')
            if not symbol:
                self.logger.warning(f"No symbol specified for {source_id}, skipping")
                continue
            
            # Download data
            result = self.download_data(source_id, symbol)
            results[source_id] = result
        
        return results
    
    def save_to_csv(self, result: DataSourceResult, output_file: str) -> bool:
        """
        Save data result to CSV file.
        
        Args:
            result: DataSourceResult with data
            output_file: Path to output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        if not result.success or not result.data:
            self.logger.error(f"Cannot save failed result to {output_file}")
            return False
        
        try:
            # Create output directory if needed
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write CSV
            with open(output_file, 'w', newline='') as f:
                if result.data:
                    writer = csv.DictWriter(f, fieldnames=result.data[0].keys())
                    writer.writeheader()
                    writer.writerows(result.data)
            
            self.logger.info(f"Saved {len(result.data)} records to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save to {output_file}: {e}")
            return False
    
    def format_for_import(self, result: DataSourceResult, data_type: str) -> List[Dict[str, Any]]:
        """
        Format data result for database import.
        
        Args:
            result: DataSourceResult with data
            data_type: Type of data (exchange_rate, commodity, dollar_index)
            
        Returns:
            Formatted data ready for import
        """
        if not result.success or not result.data:
            return []
        
        # Get the source that produced this result
        source = self.registry.get_source(result.source)
        if source:
            return source.format_data_for_import(result.data)
        
        return result.data
