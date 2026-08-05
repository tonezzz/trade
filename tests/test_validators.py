"""
Unit tests for data validators.
"""
import pytest
from datetime import date
from src.validators import (
    DataValidator, ValidationError,
    ExchangeRateValidator, DollarIndexValidator, CommodityPriceValidator,
    validate_csv_data
)


class TestDataValidator:
    """Test base DataValidator class."""
    
    def test_validate_date_valid(self):
        """Test valid date validation."""
        result = DataValidator.validate_date('2024-01-01')
        assert result == date(2024, 1, 1)
    
    def test_validate_date_invalid_format(self):
        """Test invalid date format."""
        with pytest.raises(ValidationError):
            DataValidator.validate_date('01-01-2024')
    
    def test_validate_date_empty(self):
        """Test empty date."""
        with pytest.raises(ValidationError):
            DataValidator.validate_date('')
    
    def test_validate_currency_code_valid(self):
        """Test valid currency code."""
        result = DataValidator.validate_currency_code('eur')
        assert result == 'EUR'
    
    def test_validate_currency_code_invalid_length(self):
        """Test invalid currency code length."""
        with pytest.raises(ValidationError):
            DataValidator.validate_currency_code('US')
    
    def test_validate_currency_code_invalid_characters(self):
        """Test invalid currency code characters."""
        with pytest.raises(ValidationError):
            DataValidator.validate_currency_code('E2R')
    
    def test_validate_currency_code_unknown(self):
        """Test unknown currency code."""
        with pytest.raises(ValidationError):
            DataValidator.validate_currency_code('XXX')
    
    def test_validate_price_valid(self):
        """Test valid price."""
        result = DataValidator.validate_price('100.50')
        assert result == 100.50
    
    def test_validate_price_below_minimum(self):
        """Test price below minimum."""
        with pytest.raises(ValidationError):
            DataValidator.validate_price('-10.0')
    
    def test_validate_price_invalid_format(self):
        """Test invalid price format."""
        with pytest.raises(ValidationError):
            DataValidator.validate_price('abc')
    
    def test_validate_commodity_valid(self):
        """Test valid commodity."""
        result = DataValidator.validate_commodity('gold')
        assert result == 'GOLD'
    
    def test_validate_commodity_invalid(self):
        """Test invalid commodity."""
        with pytest.raises(ValidationError):
            DataValidator.validate_commodity('bitcoin')
    
    def test_validate_unit_valid(self):
        """Test valid unit."""
        result = DataValidator.validate_unit('OZ')
        assert result == 'oz'
    
    def test_validate_unit_invalid(self):
        """Test invalid unit."""
        with pytest.raises(ValidationError):
            DataValidator.validate_unit('pound')
    
    def test_validate_unit_none(self):
        """Test None unit."""
        result = DataValidator.validate_unit(None)
        assert result is None
    
    def test_validate_symbol_valid(self):
        """Test valid symbol."""
        result = DataValidator.validate_symbol('xauusd')
        assert result == 'XAUUSD'
    
    def test_validate_symbol_invalid_format(self):
        """Test invalid symbol format."""
        with pytest.raises(ValidationError):
            DataValidator.validate_symbol('XAU-USD')
    
    def test_validate_symbol_none(self):
        """Test None symbol."""
        result = DataValidator.validate_symbol(None)
        assert result is None
    
    def test_validate_volume_valid(self):
        """Test valid volume."""
        result = DataValidator.validate_volume('1000000')
        assert result == 1000000.0
    
    def test_validate_volume_negative(self):
        """Test negative volume."""
        with pytest.raises(ValidationError):
            DataValidator.validate_volume('-100')
    
    def test_validate_volume_none(self):
        """Test None volume."""
        result = DataValidator.validate_volume(None)
        assert result is None


class TestExchangeRateValidator:
    """Test ExchangeRateValidator."""
    
    def test_validate_row_valid(self):
        """Test valid exchange rate row."""
        row = {
            'date': '2024-01-01',
            'quote_currency': 'EUR',
            'rate': '0.9150',
            'open_price': '0.9145',
            'high_price': '0.9160',
            'low_price': '0.9130',
            'close_price': '0.9155',
            'volume': '1000000'
        }
        is_valid, errors = ExchangeRateValidator.validate_row(row)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_row_missing_required_field(self):
        """Test row missing required field."""
        row = {
            'date': '2024-01-01',
            'quote_currency': 'EUR'
            # Missing 'rate'
        }
        is_valid, errors = ExchangeRateValidator.validate_row(row)
        assert not is_valid
        assert len(errors) > 0
        assert any('rate' in str(e) for e in errors)
    
    def test_validate_row_invalid_currency(self):
        """Test row with invalid currency."""
        row = {
            'date': '2024-01-01',
            'quote_currency': 'XXX',
            'rate': '0.9150'
        }
        is_valid, errors = ExchangeRateValidator.validate_row(row)
        assert not is_valid
        assert len(errors) > 0


class TestDollarIndexValidator:
    """Test DollarIndexValidator."""
    
    def test_validate_row_valid(self):
        """Test valid Dollar Index row."""
        row = {
            'date': '2024-01-01',
            'value': '101.5',
            'open_price': '101.3',
            'high_price': '101.8',
            'low_price': '101.2',
            'close_price': '101.6',
            'volume': '50000000'
        }
        is_valid, errors = DollarIndexValidator.validate_row(row)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_row_missing_value(self):
        """Test row missing value."""
        row = {
            'date': '2024-01-01'
            # Missing 'value'
        }
        is_valid, errors = DollarIndexValidator.validate_row(row)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_row_value_out_of_range(self):
        """Test row with value out of valid range."""
        row = {
            'date': '2024-01-01',
            'value': '250.0'  # Above max of 200.0
        }
        is_valid, errors = DollarIndexValidator.validate_row(row)
        assert not is_valid
        assert len(errors) > 0


class TestCommodityPriceValidator:
    """Test CommodityPriceValidator."""
    
    def test_validate_row_valid(self):
        """Test valid commodity price row."""
        row = {
            'date': '2024-01-01',
            'commodity': 'GOLD',
            'symbol': 'XAUUSD',
            'price': '2050.50',
            'unit': 'oz',
            'open_price': '2048.00',
            'high_price': '2055.00',
            'low_price': '2045.00',
            'close_price': '2052.00',
            'volume': '150000'
        }
        is_valid, errors = CommodityPriceValidator.validate_row(row)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_row_missing_commodity(self):
        """Test row missing commodity."""
        row = {
            'date': '2024-01-01',
            'price': '2050.50'
            # Missing 'commodity'
        }
        is_valid, errors = CommodityPriceValidator.validate_row(row)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_row_invalid_commodity(self):
        """Test row with invalid commodity."""
        row = {
            'date': '2024-01-01',
            'commodity': 'BITCOIN',
            'price': '50000.00'
        }
        is_valid, errors = CommodityPriceValidator.validate_row(row)
        assert not is_valid
        assert len(errors) > 0


class TestValidateCsvData:
    """Test validate_csv_data function."""
    
    def test_validate_csv_data_valid(self):
        """Test validation of valid CSV data."""
        data = [
            {
                'date': '2024-01-01',
                'quote_currency': 'EUR',
                'rate': '0.9150'
            },
            {
                'date': '2024-01-02',
                'quote_currency': 'GBP',
                'rate': '0.7850'
            }
        ]
        results = validate_csv_data('exchange_rates', data)
        
        assert results['total_rows'] == 2
        assert results['valid_rows'] == 2
        assert results['invalid_rows'] == 0
        assert len(results['errors']) == 0
    
    def test_validate_csv_data_mixed(self):
        """Test validation of mixed valid/invalid data."""
        data = [
            {
                'date': '2024-01-01',
                'quote_currency': 'EUR',
                'rate': '0.9150'
            },
            {
                'date': '2024-01-02',
                'quote_currency': 'XXX',  # Invalid
                'rate': '0.7850'
            }
        ]
        results = validate_csv_data('exchange_rates', data)
        
        assert results['total_rows'] == 2
        assert results['valid_rows'] == 1
        assert results['invalid_rows'] == 1
        assert len(results['errors']) == 1
    
    def test_validate_csv_data_invalid_type(self):
        """Test validation with invalid data type."""
        data = [{'date': '2024-01-01', 'rate': '0.9150'}]
        results = validate_csv_data('invalid_type', data)
        
        assert len(results['errors']) > 0
        assert 'Unknown data type' in str(results['errors'])