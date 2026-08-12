"""
Data source registry for managing available data sources.
"""
from typing import Dict, List, Optional, Type
from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceType
import logging


class DataSourceRegistry:
    """Registry for managing available data sources."""
    
    def __init__(self):
        """Initialize the data source registry."""
        self._sources: Dict[str, BaseDataSource] = {}
        self._source_classes: Dict[str, Type[BaseDataSource]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_source_class(self, name: str, source_class: Type[BaseDataSource]):
        """
        Register a data source class.
        
        Args:
            name: Name for the data source
            source_class: Class that inherits from BaseDataSource
        """
        self._source_classes[name] = source_class
        self.logger.info(f"Registered data source class: {name}")
    
    def create_source(self, name: str, config: DataSourceConfig) -> BaseDataSource:
        """
        Create a data source instance from registered class.
        
        Args:
            name: Name of the data source
            config: Configuration for the data source
            
        Returns:
            Data source instance
            
        Raises:
            ValueError: If source class not found
        """
        if name not in self._source_classes:
            raise ValueError(f"Data source class not found: {name}")
        
        source_class = self._source_classes[name]
        return source_class(config)
    
    def add_source(self, name: str, source: BaseDataSource):
        """
        Add a data source instance to the registry.
        
        Args:
            name: Name for the data source
            source: Data source instance
        """
        self._sources[name] = source
        self.logger.info(f"Added data source instance: {name}")
    
    def get_source(self, name: str) -> Optional[BaseDataSource]:
        """
        Get a data source by name.
        
        Args:
            name: Name of the data source
            
        Returns:
            Data source instance or None
        """
        return self._sources.get(name)
    
    def get_sources_by_type(self, source_type: DataSourceType) -> List[BaseDataSource]:
        """
        Get all data sources of a specific type.
        
        Args:
            source_type: Type of data source
            
        Returns:
            List of data source instances
        """
        return [
            source for source in self._sources.values()
            if source.config.source_type == source_type
        ]
    
    def list_sources(self) -> List[str]:
        """
        List all registered data source names.
        
        Returns:
            List of data source names
        """
        return list(self._sources.keys())
    
    def list_source_classes(self) -> List[str]:
        """
        List all registered data source class names.
        
        Returns:
            List of data source class names
        """
        return list(self._source_classes.keys())
    
    def remove_source(self, name: str) -> bool:
        """
        Remove a data source from the registry.
        
        Args:
            name: Name of the data source
            
        Returns:
            True if removed, False if not found
        """
        if name in self._sources:
            del self._sources[name]
            self.logger.info(f"Removed data source: {name}")
            return True
        return False
    
    def clear(self):
        """Clear all data sources from the registry."""
        self._sources.clear()
        self.logger.info("Cleared all data sources from registry")


# Global registry instance
_global_registry: Optional[DataSourceRegistry] = None


def get_registry() -> DataSourceRegistry:
    """
    Get the global data source registry instance.
    
    Returns:
        Global DataSourceRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = DataSourceRegistry()
    return _global_registry


def register_default_sources():
    """Register default data source classes."""
    registry = get_registry()
    
    # Import and register data source classes
    from src.data_sources.alpha_vantage_source import AlphaVantageSource
    from src.data_sources.fred_source import FREDSource
    from src.data_sources.ecb_source import ECBSource
    from src.data_sources.metal_prices_source import MetalPricesSource
    from src.data_sources.minted_metal_source import MintedMetalSource
    from src.data_sources.open_exchange_rates_source import OpenExchangeRatesSource
    
    registry.register_source_class("alpha_vantage", AlphaVantageSource)
    registry.register_source_class("fred", FREDSource)
    registry.register_source_class("ecb", ECBSource)
    registry.register_source_class("metal_prices", MetalPricesSource)
    registry.register_source_class("minted_metal", MintedMetalSource)
    registry.register_source_class("open_exchange_rates", OpenExchangeRatesSource)
