"""
Data validation module for ensuring data quality.
"""
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from decimal import Decimal, InvalidOperation
import re


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DataValidator:
    """Validates data before import into database."""
    
    # Valid currency codes (ISO 4217)
    VALID_CURRENCIES = {
        'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 
        'SEK', 'NOK', 'DKK', 'SGD', 'HKD', 'MXN', 'TRY', 'ZAR',
        'CZK', 'HUF', 'PLN', 'RUB', 'INR', 'CNY', 'KRW', 'BRL',
        'THB', 'MYR', 'IDR', 'PHP', 'VND'
    }
    
    # Valid commodity names
    VALID_COMMODITIES = {
        'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM',
        'OIL', 'WTI', 'BRENT', 'NATURAL_GAS',
        'COPPER', 'ALUMINUM', 'ZINC', 'NICKEL', 'LEAD'
    }
    
    # Valid units
    VALID_UNITS = {
        'oz', 'gram', 'kg', 'lb', 'barrel', 'gallon', 'liter', 'ton',
        'metric_ton', 'bushel', 'share', 'contract'
    }
    
    @staticmethod
    def validate_date(date_str: str) -> date:
        """
        Validate and convert date string to date object.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            date object
            
        Raises:
            ValidationError: If date format is invalid
        """
        if not date_str:
            raise ValidationError("Date cannot be empty")
        
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    @staticmethod
    def validate_currency_code(currency: str) -> str:
        """
        Validate currency code.
        
        Args:
            currency: Currency code (e.g., EUR, GBP)
            
        Returns:
            Uppercase currency code
            
        Raises:
            ValidationError: If currency code is invalid
        """
        if not currency:
            raise ValidationError("Currency code cannot be empty")
        
        currency_upper = currency.upper()
        if len(currency_upper) != 3:
            raise ValidationError(f"Currency code must be 3 characters: {currency}")
        
        if not re.match(r'^[A-Z]{3}$', currency_upper):
            raise ValidationError(f"Currency code must contain only letters: {currency}")
        
        if currency_upper not in DataValidator.VALID_CURRENCIES:
            raise ValidationError(f"Unknown currency code: {currency}")
        
        return currency_upper
    
    @staticmethod
    def validate_price(price_str: str, min_value: float = 0.0, max_value: float = 1000000.0) -> float:
        """
        Validate and convert price string to float.
        
        Args:
            price_str: Price as string
            min_value: Minimum acceptable value
            max_value: Maximum acceptable value
            
        Returns:
            Price as float
            
        Raises:
            ValidationError: If price is invalid
        """
        if not price_str:
            raise ValidationError("Price cannot be empty")
        
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid price format: {price_str}")
        
        if price < min_value:
            raise ValidationError(f"Price {price} is below minimum {min_value}")
        
        if price > max_value:
            raise ValidationError(f"Price {price} is above maximum {max_value}")
        
        return price
    
    @staticmethod
    def validate_commodity(commodity: str) -> str:
        """
        Validate commodity name.
        
        Args:
            commodity: Commodity name
            
        Returns:
            Uppercase commodity name
            
        Raises:
            ValidationError: If commodity is invalid
        """
        if not commodity:
            raise ValidationError("Commodity cannot be empty")
        
        commodity_upper = commodity.upper()
        if commodity_upper not in DataValidator.VALID_COMMODITIES:
            raise ValidationError(f"Unknown commodity: {commodity}")
        
        return commodity_upper
    
    @staticmethod
    def validate_unit(unit: Optional[str]) -> Optional[str]:
        """
        Validate unit of measurement.
        
        Args:
            unit: Unit string (optional)
            
        Returns:
            Lowercase unit string or None
            
        Raises:
            ValidationError: If unit is invalid
        """
        if not unit:
            return None
        
        unit_lower = unit.lower()
        if unit_lower not in DataValidator.VALID_UNITS:
            raise ValidationError(f"Unknown unit: {unit}")
        
        return unit_lower
    
    @staticmethod
    def validate_symbol(symbol: Optional[str]) -> Optional[str]:
        """
        Validate trading symbol.
        
        Args:
            symbol: Trading symbol (optional)
            
        Returns:
            Uppercase symbol string or None
            
        Raises:
            ValidationError: If symbol format is invalid
        """
        if not symbol:
            return None
        
        symbol_upper = symbol.upper()
        if not re.match(r'^[A-Z0-9]{1,20}$', symbol_upper):
            raise ValidationError(f"Invalid symbol format: {symbol}")
        
        return symbol_upper
    
    @staticmethod
    def validate_volume(volume_str: Optional[str]) -> Optional[float]:
        """
        Validate trading volume.
        
        Args:
            volume_str: Volume as string (optional)
            
        Returns:
            Volume as float or None
            
        Raises:
            ValidationError: If volume is invalid
        """
        if not volume_str:
            return None
        
        try:
            volume = float(volume_str)
            if volume < 0:
                raise ValidationError(f"Volume cannot be negative: {volume}")
            return volume
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid volume format: {volume_str}")


class ExchangeRateValidator(DataValidator):
    """Validator for exchange rate data."""
    
    @staticmethod
    def validate_row(row: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single exchange rate row.
        
        Args:
            row: Dictionary containing row data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Validate required fields
            if 'date' not in row:
                errors.append("Missing required field: date")
            else:
                ExchangeRateValidator.validate_date(row['date'])
            
            if 'quote_currency' not in row:
                errors.append("Missing required field: quote_currency")
            else:
                ExchangeRateValidator.validate_currency_code(row['quote_currency'])
            
            if 'rate' not in row:
                errors.append("Missing required field: rate")
            else:
                ExchangeRateValidator.validate_price(row['rate'], min_value=0.0001, max_value=10000.0)
            
            # Validate optional fields
            if 'open_price' in row and row['open_price']:
                ExchangeRateValidator.validate_price(row['open_price'])
            
            if 'high_price' in row and row['high_price']:
                ExchangeRateValidator.validate_price(row['high_price'])
            
            if 'low_price' in row and row['low_price']:
                ExchangeRateValidator.validate_price(row['low_price'])
            
            if 'close_price' in row and row['close_price']:
                ExchangeRateValidator.validate_price(row['close_price'])
            
            if 'volume' in row and row['volume']:
                ExchangeRateValidator.validate_volume(row['volume'])
            
        except ValidationError as e:
            errors.append(str(e))
        
        return (len(errors) == 0, errors)


class DollarIndexValidator(DataValidator):
    """Validator for Dollar Index data."""
    
    @staticmethod
    def validate_row(row: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single Dollar Index row.
        
        Args:
            row: Dictionary containing row data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Validate required fields
            if 'date' not in row:
                errors.append("Missing required field: date")
            else:
                DollarIndexValidator.validate_date(row['date'])
            
            if 'value' not in row:
                errors.append("Missing required field: value")
            else:
                DollarIndexValidator.validate_price(row['value'], min_value=50.0, max_value=200.0)
            
            # Validate optional fields
            if 'open_price' in row and row['open_price']:
                DollarIndexValidator.validate_price(row['open_price'], min_value=50.0, max_value=200.0)
            
            if 'high_price' in row and row['high_price']:
                DollarIndexValidator.validate_price(row['high_price'], min_value=50.0, max_value=200.0)
            
            if 'low_price' in row and row['low_price']:
                DollarIndexValidator.validate_price(row['low_price'], min_value=50.0, max_value=200.0)
            
            if 'close_price' in row and row['close_price']:
                DollarIndexValidator.validate_price(row['close_price'], min_value=50.0, max_value=200.0)
            
            if 'volume' in row and row['volume']:
                DollarIndexValidator.validate_volume(row['volume'])
            
        except ValidationError as e:
            errors.append(str(e))
        
        return (len(errors) == 0, errors)


class CommodityPriceValidator(DataValidator):
    """Validator for commodity price data."""
    
    @staticmethod
    def validate_row(row: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single commodity price row.
        
        Args:
            row: Dictionary containing row data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Validate required fields
            if 'date' not in row:
                errors.append("Missing required field: date")
            else:
                CommodityPriceValidator.validate_date(row['date'])
            
            if 'commodity' not in row:
                errors.append("Missing required field: commodity")
            else:
                CommodityPriceValidator.validate_commodity(row['commodity'])
            
            if 'price' not in row:
                errors.append("Missing required field: price")
            else:
                CommodityPriceValidator.validate_price(row['price'], min_value=0.01, max_value=100000.0)
            
            # Validate optional fields
            if 'symbol' in row and row['symbol']:
                CommodityPriceValidator.validate_symbol(row['symbol'])
            
            if 'unit' in row and row['unit']:
                CommodityPriceValidator.validate_unit(row['unit'])
            
            if 'open_price' in row and row['open_price']:
                CommodityPriceValidator.validate_price(row['open_price'])
            
            if 'high_price' in row and row['high_price']:
                CommodityPriceValidator.validate_price(row['high_price'])
            
            if 'low_price' in row and row['low_price']:
                CommodityPriceValidator.validate_price(row['low_price'])
            
            if 'close_price' in row and row['close_price']:
                CommodityPriceValidator.validate_price(row['close_price'])
            
            if 'volume' in row and row['volume']:
                CommodityPriceValidator.validate_volume(row['volume'])
            
        except ValidationError as e:
            errors.append(str(e))
        
        return (len(errors) == 0, errors)


def validate_csv_data(data_type: str, data: List[Dict]) -> Dict:
    """
    Validate entire CSV dataset.
    
    Args:
        data_type: Type of data ('exchange_rates', 'dollar_index', 'commodity_prices')
        data: List of dictionaries containing row data
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'total_rows': len(data),
        'valid_rows': 0,
        'invalid_rows': 0,
        'errors': []
    }
    
    validators = {
        'exchange_rates': ExchangeRateValidator,
        'dollar_index': DollarIndexValidator,
        'commodity_prices': CommodityPriceValidator
    }
    
    if data_type not in validators:
        results['errors'].append(f"Unknown data type: {data_type}")
        return results
    
    validator = validators[data_type]
    
    for i, row in enumerate(data, 1):
        is_valid, errors = validator.validate_row(row)
        
        if is_valid:
            results['valid_rows'] += 1
        else:
            results['invalid_rows'] += 1
            results['errors'].append({
                'row': i,
                'errors': errors,
                'data': row
            })
    
    return results