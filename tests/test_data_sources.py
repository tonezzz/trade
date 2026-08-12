"""
Unit tests for data source module.
"""
import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from src.data_sources.base_source import BaseDataSource, DataSourceConfig, DataSourceType
from src.data_sources.minted_metal_source import MintedMetalSource
from src.data_sources.registry import DataSourceRegistry


class TestBaseDataSource:
    """Test BaseDataSource class."""
    
    def test_base_source_initialization(self):
        """Test base source initialization."""
        config = DataSourceConfig(
            name='test_source',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)  # Use concrete implementation
        assert source.config.name == 'test_source'
        assert source.config.enabled == True
    
    def test_base_source_validate_config(self):
        """Test configuration validation."""
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        assert source.config.name == 'test'
    
    def test_base_source_fetch_data_not_implemented(self):
        """Test that abstract methods need implementation."""
        config = DataSourceConfig(
            name='test_source',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        # Can't instantiate abstract class directly
        with pytest.raises(TypeError):
            BaseDataSource(config)


class TestMintedMetalSource:
    """Test MintedMetalSource class."""
    
    def test_minted_metal_initialization(self):
        """Test Minted Metal source initialization."""
        config = DataSourceConfig(
            name='gold',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        assert source.config.name == 'gold'
        assert source.config.enabled == True
    
    def test_minted_metal_normalize_symbol_gold(self):
        """Test symbol normalization for gold."""
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        assert source.normalize_symbol('GOLD') == 'gold'
        assert source.normalize_symbol('XAU') == 'gold'
        assert source.normalize_symbol('gold') == 'gold'
    
    def test_minted_metal_normalize_symbol_silver(self):
        """Test symbol normalization for silver."""
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        assert source.normalize_symbol('SILVER') == 'silver'
        assert source.normalize_symbol('XAG') == 'silver'
        assert source.normalize_symbol('silver') == 'silver'
    
    def test_minted_metal_normalize_symbol_unsupported(self):
        """Test symbol normalization for unsupported metals."""
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        # Unsupported symbols just get lowercased, no error raised
        result = source.normalize_symbol('BITCOIN')
        assert result == 'bitcoin'
    
    def test_minted_metal_validate_symbol(self):
        """Test symbol validation."""
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        
        # Valid symbols
        assert source.validate_symbol('gold') is True
        assert source.validate_symbol('silver') is True
        assert source.validate_symbol('platinum') is True
        
        # Invalid symbols
        assert source.validate_symbol('bitcoin') is False
        assert source.validate_symbol('unsupported') is False
    
    @patch('requests.get')
    def test_minted_metal_fetch_data_success(self, mock_get):
        """Test successful data fetch from Minted Metal API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'metals': {
                'gold': {
                    'price': 4324.45,
                    'currency': 'USD',
                    'unit': 'troy ounce'
                }
            }
        }
        mock_get.return_value = mock_response
        
        config = DataSourceConfig(
            name='gold',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        result = source.fetch_data('GOLD')
        
        assert result.success is True
        assert result.data is not None
        assert len(result.data) > 0
        assert result.metadata['symbol'] == 'gold'
    
    @patch('requests.get')
    def test_minted_metal_fetch_data_failure(self, mock_get):
        """Test data fetch failure from Minted Metal API."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        config = DataSourceConfig(
            name='gold',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        result = source.fetch_data('GOLD')
        
        assert result.success is False
        assert result.error is not None


class TestDataSourceRegistry:
    """Test DataSourceRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = DataSourceRegistry()
        assert len(registry._sources) == 0
        assert len(registry._source_classes) == 0
    
    def test_registry_register_source_class(self):
        """Test registering a data source class."""
        registry = DataSourceRegistry()
        registry.register_source_class('test_source', MintedMetalSource)
        assert 'test_source' in registry._source_classes
    
    def test_registry_create_source(self):
        """Test creating a source from registered class."""
        registry = DataSourceRegistry()
        registry.register_source_class('test_source', MintedMetalSource)
        
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = registry.create_source('test_source', config)
        assert isinstance(source, MintedMetalSource)
    
    def test_registry_create_nonexistent_source(self):
        """Test creating a non-existent source."""
        registry = DataSourceRegistry()
        config = DataSourceConfig(
            name='test',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        with pytest.raises(ValueError):
            registry.create_source('nonexistent', config)
    
    def test_registry_list_source_classes(self):
        """Test listing all registered source classes."""
        registry = DataSourceRegistry()
        registry.register_source_class('source1', MintedMetalSource)
        registry.register_source_class('source2', MintedMetalSource)
        sources = registry.list_source_classes()
        assert 'source1' in sources
        assert 'source2' in sources


class TestDataSourceIntegration:
    """Integration tests for data sources."""
    
    def test_minted_metal_symbol_normalization_integration(self):
        """Test Minted Metal symbol normalization in real context."""
        config = DataSourceConfig(
            name='gold',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source = MintedMetalSource(config)
        
        # Test various input formats
        assert source.normalize_symbol('GOLD') == 'gold'
        assert source.normalize_symbol('XAU') == 'gold'
        assert source.normalize_symbol('gold') == 'gold'
        
        # Test silver
        config_silver = DataSourceConfig(
            name='silver',
            source_type=DataSourceType.COMMODITY,
            enabled=True
        )
        source_silver = MintedMetalSource(config_silver)
        assert source_silver.normalize_symbol('SILVER') == 'silver'
        assert source_silver.normalize_symbol('XAG') == 'silver'
