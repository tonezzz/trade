"""
Unit tests for database models.
"""
import pytest
from datetime import date
from src.models import ExchangeRate, DollarIndex, CommodityPrice, Base


class TestExchangeRate:
    """Test ExchangeRate model."""
    
    def test_exchange_rate_creation(self):
        """Test creating an ExchangeRate instance."""
        rate = ExchangeRate(
            date=date(2024, 1, 1),
            base_currency='USD',
            quote_currency='EUR',
            rate=0.9150,
            open_price=0.9145,
            high_price=0.9160,
            low_price=0.9130,
            close_price=0.9155,
            volume=1000000,
            source='test'
        )
        
        assert rate.date == date(2024, 1, 1)
        assert rate.base_currency == 'USD'
        assert rate.quote_currency == 'EUR'
        assert rate.rate == 0.9150
        assert rate.source == 'test'
    
    def test_exchange_rate_required_fields(self):
        """Test that required fields can be set."""
        # SQLAlchemy models don't enforce required fields at Python level
        # They're enforced at database level on insert
        rate = ExchangeRate(
            date=date(2024, 1, 1),
            quote_currency='EUR',
            rate=0.9150
        )
        assert rate.date == date(2024, 1, 1)
        assert rate.quote_currency == 'EUR'
        assert rate.rate == 0.9150
    
    def test_exchange_rate_repr(self):
        """Test string representation."""
        rate = ExchangeRate(
            date=date(2024, 1, 1),
            quote_currency='EUR',
            rate=0.9150
        )
        repr_str = repr(rate)
        assert 'EUR' in repr_str
        assert '0.915' in repr_str


class TestDollarIndex:
    """Test DollarIndex model."""
    
    def test_dollar_index_creation(self):
        """Test creating a DollarIndex instance."""
        dxy = DollarIndex(
            date=date(2024, 1, 1),
            value=101.5,
            open_price=101.3,
            high_price=101.8,
            low_price=101.2,
            close_price=101.6,
            volume=50000000,
            source='test'
        )
        
        assert dxy.date == date(2024, 1, 1)
        assert dxy.value == 101.5
        assert dxy.source == 'test'
    
    def test_dollar_index_required_fields(self):
        """Test that required fields can be set."""
        # SQLAlchemy models don't enforce required fields at Python level
        # They're enforced at database level on insert
        dxy = DollarIndex(
            date=date(2024, 1, 1),
            value=101.5
        )
        assert dxy.date == date(2024, 1, 1)
        assert dxy.value == 101.5
    
    def test_dollar_index_repr(self):
        """Test string representation."""
        dxy = DollarIndex(
            date=date(2024, 1, 1),
            value=101.5
        )
        repr_str = repr(dxy)
        assert '101.5' in repr_str


class TestCommodityPrice:
    """Test CommodityPrice model."""
    
    def test_commodity_price_creation(self):
        """Test creating a CommodityPrice instance."""
        commodity = CommodityPrice(
            date=date(2024, 1, 1),
            commodity='GOLD',
            symbol='XAUUSD',
            price=2050.50,
            unit='oz',
            open_price=2048.00,
            high_price=2055.00,
            low_price=2045.00,
            close_price=2052.00,
            volume=150000,
            source='test'
        )
        
        assert commodity.date == date(2024, 1, 1)
        assert commodity.commodity == 'GOLD'
        assert commodity.symbol == 'XAUUSD'
        assert commodity.price == 2050.50
        assert commodity.unit == 'oz'
    
    def test_commodity_price_required_fields(self):
        """Test that required fields can be set."""
        # SQLAlchemy models don't enforce required fields at Python level
        # They're enforced at database level on insert
        commodity = CommodityPrice(
            date=date(2024, 1, 1),
            commodity='GOLD',
            price=2050.50
        )
        assert commodity.date == date(2024, 1, 1)
        assert commodity.commodity == 'GOLD'
        assert commodity.price == 2050.50
    
    def test_commodity_price_repr(self):
        """Test string representation."""
        commodity = CommodityPrice(
            date=date(2024, 1, 1),
            commodity='GOLD',
            price=2050.50
        )
        repr_str = repr(commodity)
        assert 'GOLD' in repr_str
        assert '2050.5' in repr_str


class TestBase:
    """Test Base model."""
    
    def test_base_metadata(self):
        """Test that Base has proper metadata."""
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None