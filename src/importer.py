"""
CSV import functionality for manual data import.
"""
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from src.models import ExchangeRate, DollarIndex, CommodityPrice
from src.database import get_db
from src.validators import (
    ExchangeRateValidator, DollarIndexValidator, CommodityPriceValidator,
    validate_csv_data, ValidationError
)


class DataImporter:
    """Import data from CSV files into the database."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def import_exchange_rates(self, csv_path: str, source: str = "manual") -> int:
        """
        Import exchange rate data from CSV file.
        
        Expected CSV columns:
        - date (YYYY-MM-DD)
        - quote_currency (e.g., EUR, GBP, JPY)
        - rate (required)
        - open_price (optional)
        - high_price (optional)
        - low_price (optional)
        - close_price (optional)
        - volume (optional)
        
        Args:
            csv_path: Path to CSV file
            source: Data source identifier
            
        Returns:
            Number of records imported
        """
        df = pd.read_csv(csv_path)
        
        # Determine the quote currency and skip already-stored dates to avoid duplicates
        existing_dates = set()
        if 'quote_currency' in df.columns and not df['quote_currency'].dropna().empty:
            quote_currency = str(df['quote_currency'].dropna().iloc[0]).upper()
            existing_records = self.session.query(ExchangeRate.date).filter(
                ExchangeRate.quote_currency == quote_currency
            ).all()
            existing_dates = {r[0] for r in existing_records}
        
        # Validate data before import
        data_list = df.to_dict('records')
        validation_results = validate_csv_data('exchange_rates', data_list)
        
        if validation_results['invalid_rows'] > 0:
            print(f"Validation failed: {validation_results['invalid_rows']} invalid rows")
            for error in validation_results['errors'][:5]:  # Show first 5 errors
                print(f"  Row {error['row']}: {error['errors']}")
            if validation_results['invalid_rows'] > 5:
                print(f"  ... and {validation_results['invalid_rows'] - 5} more errors")
            raise ValidationError("Data validation failed. Please fix errors before importing.")
        
        print(f"Validation passed: {validation_results['valid_rows']} valid rows")
        
        count = 0
        for _, row in df.iterrows():
            try:
                row_date = pd.to_datetime(row['date']).date()
                if row_date in existing_dates:
                    continue
                
                # Use validated data
                exchange_rate = ExchangeRate(
                    date=pd.to_datetime(row['date']).date(),
                    base_currency='USD',
                    quote_currency=row['quote_currency'].upper(),
                    rate=float(row['rate']),
                    open_price=float(row['open_price']) if pd.notna(row.get('open_price')) else None,
                    high_price=float(row['high_price']) if pd.notna(row.get('high_price')) else None,
                    low_price=float(row['low_price']) if pd.notna(row.get('low_price')) else None,
                    close_price=float(row['close_price']) if pd.notna(row.get('close_price')) else None,
                    volume=float(row['volume']) if pd.notna(row.get('volume')) else None,
                    source=source
                )
                self.session.add(exchange_rate)
                count += 1
            except Exception as e:
                print(f"Error importing row {count + 1}: {e}")
                continue
        
        self.session.commit()
        print(f"Imported {count} exchange rate records.")
        return count
    
    def import_dollar_index(self, csv_path: str, source: str = "manual") -> int:
        """
        Import Dollar Index (DXY) data from CSV file.
        
        Expected CSV columns:
        - date (YYYY-MM-DD)
        - value (required)
        - open_price (optional)
        - high_price (optional)
        - low_price (optional)
        - close_price (optional)
        - volume (optional)
        
        Args:
            csv_path: Path to CSV file
            source: Data source identifier
            
        Returns:
            Number of records imported
        """
        df = pd.read_csv(csv_path)
        
        # Validate data before import
        data_list = df.to_dict('records')
        validation_results = validate_csv_data('dollar_index', data_list)
        
        if validation_results['invalid_rows'] > 0:
            print(f"Validation failed: {validation_results['invalid_rows']} invalid rows")
            for error in validation_results['errors'][:5]:
                print(f"  Row {error['row']}: {error['errors']}")
            if validation_results['invalid_rows'] > 5:
                print(f"  ... and {validation_results['invalid_rows'] - 5} more errors")
            raise ValidationError("Data validation failed. Please fix errors before importing.")
        
        print(f"Validation passed: {validation_results['valid_rows']} valid rows")
        
        count = 0
        for _, row in df.iterrows():
            try:
                dollar_index = DollarIndex(
                    date=pd.to_datetime(row['date']).date(),
                    value=float(row['value']),
                    open_price=float(row['open_price']) if pd.notna(row.get('open_price')) else None,
                    high_price=float(row['high_price']) if pd.notna(row.get('high_price')) else None,
                    low_price=float(row['low_price']) if pd.notna(row.get('low_price')) else None,
                    close_price=float(row['close_price']) if pd.notna(row.get('close_price')) else None,
                    volume=float(row['volume']) if pd.notna(row.get('volume')) else None,
                    source=source
                )
                self.session.add(dollar_index)
                count += 1
            except Exception as e:
                print(f"Error importing row {count + 1}: {e}")
                continue
        
        self.session.commit()
        print(f"Imported {count} dollar index records.")
        return count
    
    def import_commodity_prices(self, csv_path: str, source: str = "manual") -> int:
        """
        Import commodity price data from CSV file.
        
        Expected CSV columns:
        - date (YYYY-MM-DD)
        - commodity (e.g., GOLD, SILVER, OIL)
        - symbol (e.g., XAUUSD, USOIL)
        - price (required)
        - unit (e.g., oz, barrel)
        - open_price (optional)
        - high_price (optional)
        - low_price (optional)
        - close_price (optional)
        - volume (optional)
        
        Args:
            csv_path: Path to CSV file
            source: Data source identifier
            
        Returns:
            Number of records imported
        """
        df = pd.read_csv(csv_path)
        
        # Validate data before import
        data_list = df.to_dict('records')
        validation_results = validate_csv_data('commodity_prices', data_list)
        
        if validation_results['invalid_rows'] > 0:
            print(f"Validation failed: {validation_results['invalid_rows']} invalid rows")
            for error in validation_results['errors'][:5]:
                print(f"  Row {error['row']}: {error['errors']}")
            if validation_results['invalid_rows'] > 5:
                print(f"  ... and {validation_results['invalid_rows'] - 5} more errors")
            raise ValidationError("Data validation failed. Please fix errors before importing.")
        
        print(f"Validation passed: {validation_results['valid_rows']} valid rows")
        
        count = 0
        for _, row in df.iterrows():
            try:
                commodity_price = CommodityPrice(
                    date=pd.to_datetime(row['date']).date(),
                    commodity=row['commodity'].upper(),
                    symbol=row.get('symbol', '').upper() if pd.notna(row.get('symbol')) else None,
                    price=float(row['price']),
                    unit=row.get('unit') if pd.notna(row.get('unit')) else None,
                    open_price=float(row['open_price']) if pd.notna(row.get('open_price')) else None,
                    high_price=float(row['high_price']) if pd.notna(row.get('high_price')) else None,
                    low_price=float(row['low_price']) if pd.notna(row.get('low_price')) else None,
                    close_price=float(row['close_price']) if pd.notna(row.get('close_price')) else None,
                    volume=float(row['volume']) if pd.notna(row.get('volume')) else None,
                    source=source
                )
                self.session.add(commodity_price)
                count += 1
            except Exception as e:
                print(f"Error importing row {count + 1}: {e}")
                continue
        
        self.session.commit()
        print(f"Imported {count} commodity price records.")
        return count


def import_data(data_type: str, csv_path: str, source: str = "manual") -> int:
    """
    Convenience function to import data by type.
    
    Args:
        data_type: Type of data ('exchange_rates', 'dollar_index', 'commodity_prices')
        csv_path: Path to CSV file
        source: Data source identifier
        
    Returns:
        Number of records imported
    """
    db_session = next(get_db())
    importer = DataImporter(db_session)
    
    if data_type == 'exchange_rates':
        return importer.import_exchange_rates(csv_path, source)
    elif data_type == 'dollar_index':
        return importer.import_dollar_index(csv_path, source)
    elif data_type == 'commodity_prices':
        return importer.import_commodity_prices(csv_path, source)
    else:
        raise ValueError(f"Unknown data type: {data_type}")
