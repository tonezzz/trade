"""
Service for data import business logic.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import pandas as pd

from src.services.base_service import BaseService
from src.importer import DataImporter
from src.validators import validate_csv_data, ValidationError


class DataImportService(BaseService):
    """Service for data import operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.importer = DataImporter(db)
    
    def import_exchange_rates(
        self,
        csv_path: str,
        source: str = "manual"
    ) -> Dict[str, Any]:
        """
        Import exchange rate data from CSV file.
        
        Args:
            csv_path: Path to CSV file
            source: Data source identifier
            
        Returns:
            Dictionary with import results
        """
        try:
            # Read and validate data
            df = pd.read_csv(csv_path)
            data_list = df.to_dict('records')
            validation_results = validate_csv_data('exchange_rates', data_list)
            
            if validation_results['invalid_rows'] > 0:
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'invalid_rows': validation_results['invalid_rows'],
                    'valid_rows': validation_results['valid_rows'],
                    'errors': validation_results['errors'][:5]  # First 5 errors
                }
            
            # Import data
            count = self.importer.import_exchange_rates(csv_path, source)
            
            return {
                'success': True,
                'records_imported': count,
                'valid_rows': validation_results['valid_rows'],
                'source': source
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': f'Validation error: {str(e)}'
            }
        except Exception as e:
            return self.handle_exception(e, f"Error importing exchange rates from {csv_path}")
    
    def import_dollar_index(
        self,
        csv_path: str,
        source: str = "manual"
    ) -> Dict[str, Any]:
        """
        Import Dollar Index data from CSV file.
        
        Args:
            csv_path: Path to CSV file
            source: Data source identifier
            
        Returns:
            Dictionary with import results
        """
        try:
            # Read and validate data
            df = pd.read_csv(csv_path)
            data_list = df.to_dict('records')
            validation_results = validate_csv_data('dollar_index', data_list)
            
            if validation_results['invalid_rows'] > 0:
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'invalid_rows': validation_results['invalid_rows'],
                    'valid_rows': validation_results['valid_rows'],
                    'errors': validation_results['errors'][:5]
                }
            
            # Import data
            count = self.importer.import_dollar_index(csv_path, source)
            
            return {
                'success': True,
                'records_imported': count,
                'valid_rows': validation_results['valid_rows'],
                'source': source
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': f'Validation error: {str(e)}'
            }
        except Exception as e:
            return self.handle_exception(e, f"Error importing Dollar Index from {csv_path}")
    
    def import_commodity_prices(
        self,
        csv_path: str,
        source: str = "manual"
    ) -> Dict[str, Any]:
        """
        Import commodity price data from CSV file.
        
        Args:
            csv_path: Path to CSV file
            source: Data source identifier
            
        Returns:
            Dictionary with import results
        """
        try:
            # Read and validate data
            df = pd.read_csv(csv_path)
            data_list = df.to_dict('records')
            validation_results = validate_csv_data('commodity_prices', data_list)
            
            if validation_results['invalid_rows'] > 0:
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'invalid_rows': validation_results['invalid_rows'],
                    'valid_rows': validation_results['valid_rows'],
                    'errors': validation_results['errors'][:5]
                }
            
            # Import data
            count = self.importer.import_commodity_prices(csv_path, source)
            
            return {
                'success': True,
                'records_imported': count,
                'valid_rows': validation_results['valid_rows'],
                'source': source
            }
            
        except ValidationError as e:
            return {
                'success': False,
                'error': f'Validation error: {str(e)}'
            }
        except Exception as e:
            return self.handle_exception(e, f"Error importing commodity prices from {csv_path}")
    
    def validate_csv_file(
        self,
        data_type: str,
        csv_path: str
    ) -> Dict[str, Any]:
        """
        Validate a CSV file without importing.
        
        Args:
            data_type: Type of data (exchange_rates, dollar_index, commodity_prices)
            csv_path: Path to CSV file
            
        Returns:
            Dictionary with validation results
        """
        try:
            df = pd.read_csv(csv_path)
            data_list = df.to_dict('records')
            validation_results = validate_csv_data(data_type, data_list)
            
            return {
                'success': True,
                'valid_rows': validation_results['valid_rows'],
                'invalid_rows': validation_results['invalid_rows'],
                'errors': validation_results['errors']
            }
            
        except Exception as e:
            return self.handle_exception(e, f"Error validating CSV file {csv_path}")
    
    def get_import_summary(self) -> Dict[str, Any]:
        """
        Get summary of imported data.
        
        Returns:
            Dictionary with import summary statistics
        """
        try:
            from src.models import ExchangeRate, DollarIndex, CommodityPrice
            
            # Count records in each table
            exchange_rate_count = self.db.query(ExchangeRate).count()
            dollar_index_count = self.db.query(DollarIndex).count()
            commodity_price_count = self.db.query(CommodityPrice).count()
            
            # Get date ranges
            exchange_rate_dates = self.db.query(
                ExchangeRate.date
            ).order_by(ExchangeRate.date).first()
            
            return {
                'exchange_rates': {
                    'count': exchange_rate_count,
                    'earliest_date': exchange_rate_dates[0] if exchange_rate_dates else None
                },
                'dollar_index': {
                    'count': dollar_index_count
                },
                'commodity_prices': {
                    'count': commodity_price_count
                },
                'total_records': exchange_rate_count + dollar_index_count + commodity_price_count
            }
            
        except Exception as e:
            return self.handle_exception(e, "Error getting import summary")
