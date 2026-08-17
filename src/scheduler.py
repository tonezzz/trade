"""
Job scheduler for automated data download and import.
Handles scheduling, retry logic, and status tracking.
"""
import schedule
import time
import yaml
import logging
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logging_config import setup_logging, get_logger
from src.database import get_db
from src.importer import DataImporter
from src.notifications import NotificationManager, NotificationConfig, StatusLogger, load_notification_config_from_env
from src.models import CommodityPrice, ExchangeRate, DollarIndex
from src.data_sources import UnifiedDataDownloader
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class JobStatus(Enum):
    """Status of a scheduled job."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class JobResult:
    """Result of a job execution."""
    job_name: str
    status: JobStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    records_processed: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    traceback: Optional[str] = None


@dataclass
class JobConfig:
    """Configuration for a scheduled job."""
    name: str
    description: str
    type: str
    url: str
    schedule: str
    schedule_time: Optional[str] = None
    schedule_day: Optional[str] = None
    import_function: str = ""
    source: str = "automated"
    enabled: bool = True
    formatter: Optional[str] = None
    # Additional type-specific fields
    symbol: Optional[str] = None
    commodity: Optional[str] = None
    unit: Optional[str] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None


class RetryHandler:
    """Handles retry logic with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, initial_delay: int = 5):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.logger = get_logger(__name__)
    
    def should_retry(self, attempt: int) -> bool:
        """Determine if should retry based on attempt count."""
        return attempt < self.max_retries
    
    def get_delay(self, attempt: int) -> int:
        """Calculate delay with exponential backoff."""
        return self.initial_delay * (2 ** attempt)
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> tuple:
        """
        Execute function with retry logic.
        
        Returns:
            Tuple of (success: bool, result: any, error: str)
        """
        attempt = 0
        last_error = None
        
        while attempt <= self.max_retries:
            try:
                result = func(*args, **kwargs)
                return True, result, None
            except Exception as e:
                last_error = str(e)
                attempt += 1
                
                if self.should_retry(attempt):
                    delay = self.get_delay(attempt - 1)
                    self.logger.warning(
                        f"Attempt {attempt} failed. Retrying in {delay}s... "
                        f"Error: {last_error}"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"All {self.max_retries} retry attempts failed. "
                        f"Final error: {last_error}"
                    )
        
        return False, None, last_error


class JobScheduler:
    """Main scheduler for automated data download and import jobs."""
    
    def __init__(self, config_path: str = "config/ssot/ssot.data.yml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.retry_handler = RetryHandler(
            max_retries=self.config['settings'].get('max_retries', 3),
            initial_delay=self.config['settings'].get('retry_delay', 5)
        )
        self.jobs: Dict[str, JobConfig] = {}
        self.job_history: List[JobResult] = []
        
        # Load tolerance settings for intermittent availability
        self.tolerance_days = self.config['settings'].get('tolerance', {
            'thb': 2,
            'dxy': 30,
            'commodities': 90,
            'currencies': 7
        })
        
        # Initialize notification system
        notification_config = load_notification_config_from_env()
        # Override with config file settings if available
        if self.config['settings'].get('enable_notifications'):
            notification_config.enabled = True
            notification_config.email = self.config['settings'].get('notification_email')
        
        self.notification_manager = NotificationManager(notification_config)
        self.status_logger = StatusLogger(self.config['settings'].get('log_file', 'logs/automation.log').replace('.log', '_status.log'))
        
        # Initialize unified data downloader
        self.data_downloader = UnifiedDataDownloader(config_path)
        
        self._load_jobs()
    
    def _setup_logging(self):
        """Set up logging based on configuration."""
        log_file = self.config['settings'].get('log_file', 'logs/automation.log')
        log_level = self.config['settings'].get('log_level', 'INFO')
        
        # Create logs directory if it doesn't exist
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        return setup_logging(log_level=log_level, log_file=log_file)
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise
    
    def _load_jobs(self):
        """Load job configurations from config file."""
        data_sources = self.config.get('data_sources', {})
        
        for job_id, job_config in data_sources.items():
            if job_config.get('enabled', True):
                self.jobs[job_id] = JobConfig(
                    name=job_config.get('name', job_id),
                    description=job_config.get('description', ''),
                    type=job_config.get('type', ''),
                    url=job_config.get('url', ''),
                    schedule=job_config.get('schedule', 'daily'),
                    schedule_time=job_config.get('schedule_time'),
                    schedule_day=job_config.get('schedule_day'),
                    import_function=job_config.get('import_function', ''),
                    source=job_config.get('source', 'automated'),
                    enabled=job_config.get('enabled', True),
                    formatter=job_config.get('formatter'),
                    symbol=job_config.get('symbol'),
                    commodity=job_config.get('commodity'),
                    unit=job_config.get('unit'),
                    base_currency=job_config.get('base_currency'),
                    quote_currency=job_config.get('quote_currency')
                )
                self.logger.info(f"Loaded job: {job_id}")
    
    def _download_data(self, job: JobConfig, job_id: str) -> str:
        """Download data using unified data source system."""
        # Check for dry run mode
        if self.config['settings'].get('dry_run', False):
            self.logger.info(f"DRY RUN: Would download {job.name} using unified data source")
            return "dry_run_file.csv"
        
        # Use unified data downloader
        symbol = job.symbol or job.commodity or job.quote_currency
        if not symbol:
            self.logger.error(f"No symbol specified for job {job.name}")
            raise ValueError(f"No symbol specified for job {job.name}")
        
        self.logger.info(f"Downloading {job.name} (symbol: {symbol}) using unified data source")
        
        # Download data using unified downloader - use job_id instead of job.name
        result = self.data_downloader.download_data(job_id, symbol)
        
        if not result.success:
            raise Exception(f"Data download failed: {result.error}")
        
        # Save to file
        import_dir = self.config['settings'].get('import_dir', 'data/imported')
        os.makedirs(import_dir, exist_ok=True)
        
        # Sanitize job name to avoid directory creation from slashes
        safe_name = job.name.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        output_file = os.path.join(import_dir, f"{safe_name}_formatted.csv")
        
        if self.data_downloader.save_to_csv(result, output_file):
            self.logger.info(f"Saved to {output_file}")
            return output_file
        else:
            raise Exception("Failed to save downloaded data to CSV")
    
    def _format_data(self, job: JobConfig, input_file: str) -> str:
        """Format data using custom formatter if specified."""
        # Check for dry run mode
        if self.config['settings'].get('dry_run', False):
            self.logger.info(f"DRY RUN: Would format data for {job.name}")
            return "dry_run_formatted.csv"
        
        # Data is already formatted by unified downloader, just return the input file
        self.logger.info(f"Data already formatted by unified downloader for {job.name}")
        return input_file
        # Default: just copy the file
        shutil.copy(input_file, output_file)
        return output_file
    
    def _import_data(self, job: JobConfig, file_path: str) -> int:
        """Import data into database."""
        # Check for dry run mode
        if self.config['settings'].get('dry_run', False):
            self.logger.info(f"DRY RUN: Would import data for {job.name} using {job.import_function}")
            return 0  # Return 0 records in dry run mode
        
        session = next(get_db())
        importer = DataImporter(session)
        
        import_function_map = {
            'import_commodity_prices': importer.import_commodity_prices,
            'import_exchange_rates': importer.import_exchange_rates,
            'import_dollar_index': importer.import_dollar_index
        }
        
        import_func = import_function_map.get(job.import_function)
        if not import_func:
            raise ValueError(f"Unknown import function: {job.import_function}")
        
        try:
            count = import_func(file_path, source=job.source)
        except Exception as e:
            # If validation fails and skip_validation is enabled, try to continue
            if "validation" in str(e).lower() and self.config['settings'].get('skip_validation', False):
                self.logger.warning(f"Validation error but skip_validation is enabled: {e}")
                # Try to import without validation by directly using pandas
                import pandas as pd
                from src.models import CommodityPrice, ExchangeRate, DollarIndex
                
                df = pd.read_csv(file_path)
                count = 0
                
                for _, row in df.iterrows():
                    try:
                        if job.import_function == 'import_commodity_prices':
                            record = CommodityPrice(
                                date=pd.to_datetime(row['date']).date(),
                                commodity=row.get('commodity', '').upper(),
                                symbol=row.get('symbol', '').upper() if pd.notna(row.get('symbol')) else None,
                                price=float(row['price']),
                                unit=row.get('unit') if pd.notna(row.get('unit')) else None,
                                open_price=float(row['open_price']) if pd.notna(row.get('open_price')) else None,
                                high_price=float(row['high_price']) if pd.notna(row.get('high_price')) else None,
                                low_price=float(row['low_price']) if pd.notna(row.get('low_price')) else None,
                                close_price=float(row['close_price']) if pd.notna(row.get('close_price')) else None,
                                volume=float(row['volume']) if pd.notna(row.get('volume')) else None,
                                source=job.source
                            )
                        elif job.import_function == 'import_exchange_rates':
                            record = ExchangeRate(
                                date=pd.to_datetime(row['date']).date(),
                                base_currency='USD',
                                quote_currency=row.get('quote_currency', '').upper(),
                                rate=float(row['rate']),
                                open_price=float(row['open_price']) if pd.notna(row.get('open_price')) else None,
                                high_price=float(row['high_price']) if pd.notna(row.get('high_price')) else None,
                                low_price=float(row['low_price']) if pd.notna(row.get('low_price')) else None,
                                close_price=float(row['close_price']) if pd.notna(row.get('close_price')) else None,
                                volume=float(row['volume']) if pd.notna(row.get('volume')) else None,
                                source=job.source
                            )
                        elif job.import_function == 'import_dollar_index':
                            record = DollarIndex(
                                date=pd.to_datetime(row['date']).date(),
                                value=float(row['value']),
                                open_price=float(row['open_price']) if pd.notna(row.get('open_price')) else None,
                                high_price=float(row['high_price']) if pd.notna(row.get('high_price')) else None,
                                low_price=float(row['low_price']) if pd.notna(row.get('low_price')) else None,
                                close_price=float(row['close_price']) if pd.notna(row.get('close_price')) else None,
                                volume=float(row['volume']) if pd.notna(row.get('volume')) else None,
                                source=job.source
                            )
                        
                        session.add(record)
                        count += 1
                    except Exception as row_error:
                        self.logger.warning(f"Skipping row due to error: {row_error}")
                        continue
                
                session.commit()
                self.logger.info(f"Imported {count} records with validation skipped")
            else:
                raise  # Re-raise the exception if not a validation error or skip_validation is disabled
        
        session.close()
        return count
    
    def _execute_job(self, job_id: str) -> JobResult:
        """Execute a single job with retry logic."""
        job = self.jobs[job_id]
        result = JobResult(
            job_name=job.name,
            status=JobStatus.RUNNING,
            start_time=datetime.now()
        )
        
        self.logger.info(f"Starting job: {job.name}")
        self.status_logger.log_job_start(job.name)
        
        def job_task():
            # Download data
            downloaded_file = self._download_data(job, job_id)
            
            # Format data
            formatted_file = self._format_data(job, downloaded_file)
            
            # Import data
            record_count = self._import_data(job, formatted_file)
            
            return record_count
        
        # Execute with retry logic
        success, result_data, error = self.retry_handler.execute_with_retry(job_task)
        
        result.end_time = datetime.now()
        result.retry_count = self.retry_handler.max_retries  # Track retry attempts
        
        if success:
            result.status = JobStatus.SUCCESS
            result.records_processed = result_data
            self.logger.info(
                f"Job {job.name} completed successfully. "
                f"Processed {result_data} records."
            )
            self.status_logger.log_job_complete(job.name, "success", result_data)
            
            # Run data quality check after successful import
            try:
                quality_summary = self.run_data_quality_check()
                if quality_summary and quality_summary['failed_validations'] > 0:
                    self.logger.warning(
                        f"Data quality check found {quality_summary['failed_validations']} issues "
                        f"after importing {job.name}"
                    )
            except Exception as quality_error:
                self.logger.warning(f"Data quality check failed: {quality_error}")
        else:
            result.status = JobStatus.FAILED
            result.error_message = error
            result.traceback = traceback.format_exc()
            self.logger.error(f"Job {job.name} failed: {error}")
            self.status_logger.log_job_error(job.name, error)
            
            # Send error notification
            self.notification_manager.send_error_notification(
                job_name=job.name,
                error_message=error,
                traceback=result.traceback,
                retry_count=result.retry_count
            )
        
        self.job_history.append(result)
        return result
    
    def get_last_update(self, job_id: str) -> Optional[datetime]:
        """Get the last update date for a job's data."""
        job = self.jobs[job_id]
        session = next(get_db())
        
        try:
            if job.type == 'exchange_rate':
                # For exchange rates, get the latest date for the specific currency
                if job.quote_currency:
                    latest = session.query(ExchangeRate).filter(
                        ExchangeRate.quote_currency == job.quote_currency.upper()
                    ).order_by(ExchangeRate.date.desc()).first()
                    if latest:
                        return datetime.combine(latest.date, datetime.min.time())
            elif job.type == 'dollar_index':
                # For dollar index, get the latest date
                latest = session.query(DollarIndex).order_by(DollarIndex.date.desc()).first()
                if latest:
                    return datetime.combine(latest.date, datetime.min.time())
            elif job.type == 'commodity':
                # For commodities, get the latest date for the specific commodity
                if job.commodity:
                    latest = session.query(CommodityPrice).filter(
                        CommodityPrice.commodity == job.commodity.upper()
                    ).order_by(CommodityPrice.date.desc()).first()
                    if latest:
                        return datetime.combine(latest.date, datetime.min.time())
        finally:
            session.close()
        
        return None
    
    def should_run_job(self, job_id: str) -> bool:
        """Check if job should run based on data freshness."""
        job = self.jobs[job_id]
        if not job:
            return False
        
        # Determine tolerance from SSOT, with job, symbol, commodity, and quote-currency overrides
        tolerance = self.tolerance_days.get(job_id)
        if tolerance is None and job.symbol:
            tolerance = self.tolerance_days.get(job.symbol) or self.tolerance_days.get(job.symbol.lower())
        if tolerance is None and job.commodity:
            tolerance = self.tolerance_days.get(job.commodity) or self.tolerance_days.get(job.commodity.lower())
        if tolerance is None and job.quote_currency:
            tolerance = self.tolerance_days.get(job.quote_currency)
        if tolerance is None:
            # Fallback by type
            if job.type == 'exchange_rate':
                tolerance = self.tolerance_days.get('currencies', 7)
            elif job.type == 'dollar_index':
                tolerance = self.tolerance_days.get('dxy', 30)
            elif job.type == 'commodity':
                tolerance = self.tolerance_days.get('commodities', 90)
            else:
                tolerance = 7  # Default tolerance
        
        # Check if data is within tolerance (0 means "must be today")
        last_update = self.get_last_update(job_id)
        if last_update:
            days_since_update = (datetime.now() - last_update).days
            if days_since_update <= tolerance:
                self.logger.info(f"Skipping {job.name}: data is fresh ({days_since_update} days old, tolerance: {tolerance} days)")
                return False
        
        return True
    
    def schedule_job(self, job_id: str):
        """Schedule a job based on its configuration."""
        job = self.jobs[job_id]
        
        def job_wrapper():
            # Check if job should run based on data freshness
            if self.should_run_job(job_id):
                self._execute_job(job_id)
            else:
                self.logger.info(f"Job {job.name} skipped due to fresh data")
        
        # Schedule based on job configuration
        if job.schedule == 'daily':
            if job.schedule_time:
                schedule.every().day.at(job.schedule_time).do(job_wrapper)
            else:
                schedule.every().day.do(job_wrapper)
        elif job.schedule == 'weekly':
            if job.schedule_day and job.schedule_time:
                getattr(schedule.every(), job.schedule_day.lower()).at(job.schedule_time).do(job_wrapper)
            elif job.schedule_day:
                getattr(schedule.every(), job.schedule_day.lower()).do(job_wrapper)
            else:
                schedule.every().week.do(job_wrapper)
        elif job.schedule == 'hourly':
            schedule.every().hour.do(job_wrapper)
        elif job.schedule == 'interval':
            # Default to 1 hour if no interval specified
            schedule.every(1).hours.do(job_wrapper)
        
        self.logger.info(f"Scheduled job: {job.name} ({job.schedule})")
    
    def schedule_all_jobs(self):
        """Schedule all enabled jobs."""
        for job_id in self.jobs:
            self.schedule_job(job_id)
        self.logger.info(f"Scheduled {len(self.jobs)} jobs")
    
    def run_job_now(self, job_id: str) -> JobResult:
        """Run a job immediately (for testing or manual execution)."""
        return self._execute_job(job_id)
    
    def run_job_with_retry(self, job_id: str, max_retries: int = None) -> JobResult:
        """Run job with retry logic for network issues."""
        if max_retries is None:
            max_retries = self.config['settings'].get('max_retries', 3)
        
        original_max_retries = self.retry_handler.max_retries
        self.retry_handler.max_retries = max_retries
        
        try:
            result = self._execute_job(job_id)
            return result
        finally:
            self.retry_handler.max_retries = original_max_retries
    
    def run_catch_up_updates(self) -> Dict[str, JobResult]:
        """Run catch-up updates for all stale data sources."""
        self.logger.info("Starting catch-up updates for stale data")
        results = {}
        
        for job_id in self.jobs:
            if not self.should_run_job(job_id):
                # Data is fresh, skip
                continue
            
            self.logger.info(f"Running catch-up update for {job_id}")
            try:
                result = self.run_job_with_retry(job_id, max_retries=3)
                results[job_id] = result
                
                if result.status == JobStatus.SUCCESS:
                    self.logger.info(f"Catch-up successful for {job_id}: {result.records_processed} records")
                else:
                    self.logger.error(f"Catch-up failed for {job_id}: {result.error_message}")
            except Exception as e:
                self.logger.error(f"Catch-up error for {job_id}: {e}")
                results[job_id] = JobResult(
                    job_name=self.jobs[job_id].name,
                    status=JobStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error_message=str(e)
                )
        
        successful = sum(1 for r in results.values() if r.status == JobStatus.SUCCESS)
        failed = len(results) - successful
        
        self.logger.info(f"Catch-up updates completed: {successful} successful, {failed} failed")
        return results
    
    def run_all_jobs_now(self) -> List[JobResult]:
        """Run all jobs immediately (for testing)."""
        self.status_logger.log_automation_start()
        results = []
        for job_id in self.jobs:
            result = self.run_job_now(job_id)
            results.append(result)
        
        # Send summary notification
        successful = sum(1 for r in results if r.status == JobStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == JobStatus.FAILED)
        
        results_dict = [
            {
                'job_name': r.job_name,
                'status': r.status.value,
                'error_message': r.error_message,
                'records_processed': r.records_processed
            }
            for r in results
        ]
        
        self.notification_manager.send_summary_notification(
            total_jobs=len(results),
            successful=successful,
            failed=failed,
            results=results_dict
        )
        
        self.status_logger.log_automation_complete(len(results), successful, failed)
        
        return results
    
    def start_scheduler(self):
        """Start the scheduler loop."""
        self.logger.info("Starting scheduler...")
        self.schedule_all_jobs()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """Get the most recent result for a job."""
        for result in reversed(self.job_history):
            if result.job_name == self.jobs[job_id].name:
                return result
        return None
    
    def get_all_job_status(self) -> Dict[str, JobResult]:
        """Get the most recent result for all jobs."""
        status = {}
        for job_id in self.jobs:
            status[job_id] = self.get_job_status(job_id)
        return status
    
    def print_status_report(self):
        """Print a status report of all jobs."""
        print("\n" + "=" * 60)
        print("JOB STATUS REPORT")
        print("=" * 60)
        
        for job_id, job in self.jobs.items():
            result = self.get_job_status(job_id)
            print(f"\n{job.name} ({job_id})")
            print(f"  Schedule: {job.schedule}")
            if job.schedule_time:
                print(f"  Time: {job.schedule_time}")
            if job.schedule_day:
                print(f"  Day: {job.schedule_day}")
            
            if result:
                print(f"  Status: {result.status.value}")
                print(f"  Last Run: {result.start_time}")
                if result.status == JobStatus.SUCCESS:
                    print(f"  Records: {result.records_processed}")
                elif result.status == JobStatus.FAILED:
                    print(f"  Error: {result.error_message}")
            else:
                print("  Status: Never run")
        
        print("\n" + "=" * 60)
    
    def run_data_quality_check(self, tolerance_pct: float = 2.0, max_freshness_days: int = 2):
        """
        Run data quality validation after data import.
        
        Args:
            tolerance_pct: Acceptable percentage difference between DB and external sources
            max_freshness_days: Maximum acceptable data age in days
        """
        try:
            from scripts.data_quality_agent import DataQualityAgent
            
            self.logger.info("Running data quality validation...")
            
            agent = DataQualityAgent(
                tolerance_pct=tolerance_pct,
                max_freshness_days=max_freshness_days
            )
            
            summary = agent.run_full_validation()
            
            # Send notification if there are failures
            if summary['failed_validations'] > 0:
                self.notification_manager.send_notification(
                    subject=f"Data Quality Issues Detected - {summary['failed_validations']} failures",
                    message=f"Data quality validation found {summary['failed_validations']} issues out of {summary['total_validations']} validations. Success rate: {summary['success_rate']:.1f}%"
                )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Data quality check failed: {e}")
            return None


def main():
    """Main entry point for testing the scheduler."""
    scheduler = JobScheduler()
    scheduler.print_status_report()
    
    # Run all jobs once for testing
    print("\nRunning all jobs...")
    results = scheduler.run_all_jobs_now()
    
    print("\nResults:")
    for result in results:
        print(f"{result.job_name}: {result.status.value}")
        if result.status == JobStatus.SUCCESS:
            print(f"  Records processed: {result.records_processed}")
        elif result.status == JobStatus.FAILED:
            print(f"  Error: {result.error_message}")


if __name__ == '__main__':
    main()
