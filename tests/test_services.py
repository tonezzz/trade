"""
Unit tests for service layer.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import date
from src.services.base_service import BaseService
from src.services.commodity_service import CommodityService


class TestBaseService:
    """Test BaseService class."""
    
    def test_base_service_initialization(self):
        """Test base service initialization."""
        mock_db = Mock()
        service = BaseService(mock_db)
        assert service.db == mock_db
    
    def test_base_service_validate_date_range(self):
        """Test date range validation."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        result = service.validate_date_range(start_date, end_date)
        
        assert result == (start_date, end_date)
    
    def test_base_service_validate_date_range_invalid(self):
        """Test invalid date range validation."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        start_date = date(2024, 1, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(ValueError):
            service.validate_date_range(start_date, end_date)
    
    def test_base_service_parse_period(self):
        """Test period parsing."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        result = service.parse_period('1d')
        assert len(result) == 2
        assert result[0] == result[1]  # Same day for 1d
    
    def test_base_service_parse_period_invalid(self):
        """Test invalid period parsing."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        with pytest.raises(ValueError):
            service.parse_period('invalid')
    
    def test_base_service_apply_pagination(self):
        """Test pagination application."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        data = [{'id': i} for i in range(10)]
        result = service.apply_pagination(data, limit=5, offset=0)
        
        assert len(result['data']) == 5
        assert result['count'] == 10
        assert result['has_more'] is True
    
    def test_base_service_handle_exception(self):
        """Test exception handling."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        exception = ValueError("Test error")
        result = service.handle_exception(exception, "Test context")
        
        assert 'error' in result
        assert 'Test error' in result['error']
        assert 'error_type' in result


class TestCommodityService:
    """Test CommodityService class."""
    
    def test_commodity_service_initialization(self):
        """Test commodity service initialization."""
        mock_db = Mock()
        service = CommodityService(mock_db)
        assert service.db == mock_db
        assert hasattr(service, 'queries')
        assert hasattr(service, 'analysis')
    
    @patch('src.services.commodity_service.PriceQueries')
    def test_commodity_service_get_commodity_prices(self, mock_queries):
        """Test getting commodity prices."""
        mock_db = Mock()
        mock_df = Mock()
        mock_df.empty = False
        mock_df.to_dict.return_value = [{'id': 1, 'price': 2000.0}]
        mock_queries.return_value.get_commodity_prices.return_value = mock_df
        
        service = CommodityService(mock_db)
        result = service.get_commodity_prices(commodity='GOLD')
        
        assert 'data' in result
        assert 'count' in result
        assert result['commodity'] == 'GOLD'
    
    @patch('src.services.commodity_service.PriceQueries')
    def test_commodity_service_get_latest_commodity_price(self, mock_queries):
        """Test getting latest commodity price."""
        mock_db = Mock()
        mock_latest = Mock()
        mock_latest.date = date(2024, 1, 1)
        mock_latest.commodity = 'GOLD'
        mock_latest.symbol = 'XAUUSD'
        mock_latest.price = 2000.0
        mock_latest.unit = 'oz'
        mock_latest.open_price = 1995.0
        mock_latest.high_price = 2010.0
        mock_latest.low_price = 1990.0
        mock_latest.close_price = 2000.0
        mock_latest.volume = 1000
        mock_latest.source = 'test'
        
        mock_queries.return_value.get_latest_commodity_price.return_value = mock_latest
        
        service = CommodityService(mock_db)
        result = service.get_latest_commodity_price(commodity='GOLD')
        
        assert result is not None
        assert result['commodity'] == 'GOLD'
        assert result['price'] == 2000.0
    
    @patch('src.services.commodity_service.PriceAnalysis')
    def test_commodity_service_get_available_commodities(self, mock_analysis):
        """Test getting available commodities."""
        mock_db = Mock()
        mock_analysis.return_value.get_available_commodities.return_value = ['GOLD', 'SILVER']
        
        service = CommodityService(mock_db)
        result = service.get_available_commodities()
        
        assert result == ['GOLD', 'SILVER']


class TestServiceIntegration:
    """Integration tests for service layer."""
    
    def test_service_db_integration(self):
        """Test service and database session integration."""
        mock_db = Mock()
        service = BaseService(mock_db)
        
        assert service.db == mock_db
        assert hasattr(service, 'logger')
