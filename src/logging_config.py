"""
Logging configuration for the application.
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class DataImportLogger:
    """Specialized logger for data import operations."""
    
    def __init__(self, name: str = 'data_import'):
        self.logger = get_logger(name)
        self.import_stats = {
            'total_rows': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_import_start(self, data_type: str, source: str):
        """Log the start of an import operation."""
        self.logger.info(f"Starting import: {data_type} from {source}")
        self.import_stats = {
            'total_rows': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_import_success(self, count: int):
        """Log successful import."""
        self.import_stats['successful'] = count
        self.logger.info(f"Import successful: {count} records imported")
    
    def log_import_error(self, error: str, row_data: dict = None):
        """Log import error."""
        self.import_stats['failed'] += 1
        self.import_stats['errors'].append({
            'error': error,
            'row_data': row_data
        })
        self.logger.error(f"Import error: {error}")
        if row_data:
            self.logger.debug(f"Row data: {row_data}")
    
    def log_import_complete(self):
        """Log import completion with statistics."""
        self.logger.info(
            f"Import complete - "
            f"Total: {self.import_stats['total_rows']}, "
            f"Success: {self.import_stats['successful']}, "
            f"Failed: {self.import_stats['failed']}"
        )
        if self.import_stats['errors']:
            self.logger.warning(f"Errors encountered: {len(self.import_stats['errors'])}")
    
    def get_import_stats(self) -> dict:
        """Get import statistics."""
        return self.import_stats.copy()


class DatabaseLogger:
    """Specialized logger for database operations."""
    
    def __init__(self, name: str = 'database'):
        self.logger = get_logger(name)
    
    def log_query(self, query: str, params: dict = None):
        """Log database query."""
        self.logger.debug(f"Executing query: {query}")
        if params:
            self.logger.debug(f"Query parameters: {params}")
    
    def log_query_error(self, query: str, error: str):
        """Log query error."""
        self.logger.error(f"Query failed: {query}")
        self.logger.error(f"Error: {error}")
    
    def log_connection_error(self, error: str):
        """Log connection error."""
        self.logger.error(f"Database connection error: {error}")
    
    def log_transaction_start(self):
        """Log transaction start."""
        self.logger.debug("Starting database transaction")
    
    def log_transaction_commit(self):
        """Log transaction commit."""
        self.logger.debug("Transaction committed")
    
    def log_transaction_rollback(self):
        """Log transaction rollback."""
        self.logger.warning("Transaction rolled back")


# Set up default logging when module is imported
setup_logging(log_level='INFO')