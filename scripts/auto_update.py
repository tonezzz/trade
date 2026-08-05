#!/usr/bin/env python3
"""
Main automation script for scheduled data download and import.
This script loads configuration and runs scheduled jobs automatically.
"""
import sys
import os
import argparse
import signal
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import JobScheduler, JobStatus
from src.logging_config import setup_logging, get_logger


class AutomationController:
    """Controller for the automation system."""
    
    def __init__(self, config_path: str = "config/data_sources.yml", dry_run: bool = False):
        self.config_path = config_path
        self.dry_run = dry_run
        self.scheduler = None
        self.logger = None
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def initialize(self):
        """Initialize the automation system."""
        try:
            self.logger = get_logger(__name__)
            self.logger.info("Initializing automation system...")
            
            # Load scheduler
            self.scheduler = JobScheduler(config_path=self.config_path)
            
            # Override dry run setting if specified
            if self.dry_run:
                self.scheduler.config['settings']['dry_run'] = True
                self.logger.info("Dry run mode enabled - no actual downloads/imports will occur")
            
            self.logger.info("Automation system initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing automation system: {e}")
            return False
    
    def run_once(self, job_id: str = None):
        """Run jobs once (for testing or manual execution)."""
        if not self.scheduler:
            print("Scheduler not initialized. Call initialize() first.")
            return False
        
        try:
            if job_id:
                self.logger.info(f"Running single job: {job_id}")
                result = self.scheduler.run_job_now(job_id)
                self._print_job_result(result)
                return result.status == JobStatus.SUCCESS
            else:
                self.logger.info("Running all jobs once...")
                results = self.scheduler.run_all_jobs_now()
                self._print_results_summary(results)
                
                # Check if all jobs succeeded
                all_success = all(r.status == JobStatus.SUCCESS for r in results)
                return all_success
                
        except Exception as e:
            self.logger.error(f"Error running jobs: {e}")
            return False
    
    def run_scheduled(self):
        """Run the scheduler in continuous mode."""
        if not self.scheduler:
            print("Scheduler not initialized. Call initialize() first.")
            return False
        
        try:
            self.logger.info("Starting scheduled automation...")
            self.running = True
            
            # Print initial status
            self.scheduler.print_status_report()
            
            # Start the scheduler loop
            self.scheduler.start_scheduler()
            
        except Exception as e:
            self.logger.error(f"Error in scheduled mode: {e}")
            return False
    
    def show_status(self):
        """Show current status of all jobs."""
        if not self.scheduler:
            print("Scheduler not initialized. Call initialize() first.")
            return
        
        self.scheduler.print_status_report()
    
    def _print_job_result(self, result):
        """Print result of a single job."""
        print(f"\n{'=' * 60}")
        print(f"Job: {result.job_name}")
        print(f"Status: {result.status.value}")
        print(f"Start Time: {result.start_time}")
        print(f"End Time: {result.end_time}")
        
        if result.status == JobStatus.SUCCESS:
            print(f"Records Processed: {result.records_processed}")
            print("✅ Job completed successfully")
        elif result.status == JobStatus.FAILED:
            print(f"Error: {result.error_message}")
            print("❌ Job failed")
        
        print(f"{'=' * 60}\n")
    
    def _print_results_summary(self, results):
        """Print summary of all job results."""
        print(f"\n{'=' * 60}")
        print("AUTOMATION RUN SUMMARY")
        print(f"{'=' * 60}")
        
        success_count = sum(1 for r in results if r.status == JobStatus.SUCCESS)
        failed_count = sum(1 for r in results if r.status == JobStatus.FAILED)
        total_records = sum(r.records_processed for r in results)
        
        print(f"Total Jobs: {len(results)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"Total Records: {total_records}")
        
        print("\nDetailed Results:")
        for result in results:
            status_symbol = "✅" if result.status == JobStatus.SUCCESS else "❌"
            print(f"  {status_symbol} {result.job_name}: {result.status.value}")
            if result.status == JobStatus.SUCCESS:
                print(f"      Records: {result.records_processed}")
            elif result.status == JobStatus.FAILED:
                print(f"      Error: {result.error_message}")
        
        print(f"{'=' * 60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated data download and import system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all jobs once (for testing)
  python scripts/auto_update.py --run-once
  
  # Run a specific job once
  python scripts/auto_update.py --run-once --job wti_oil
  
  # Start the scheduler in continuous mode
  python scripts/auto_update.py --scheduled
  
  # Show current status
  python scripts/auto_update.py --status
  
  # Dry run (no actual downloads/imports)
  python scripts/auto_update.py --run-once --dry-run
        """
    )
    
    parser.add_argument(
        '--config',
        default='config/data_sources.yml',
        help='Path to configuration file (default: config/data_sources.yml)'
    )
    
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run all jobs once and exit'
    )
    
    parser.add_argument(
        '--job',
        help='Run a specific job (requires --run-once)'
    )
    
    parser.add_argument(
        '--scheduled',
        action='store_true',
        help='Run in scheduled mode (continuous)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current job status'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (no actual downloads/imports)'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.job and not args.run_once:
        print("Error: --job requires --run-once")
        sys.exit(1)
    
    if not any([args.run_once, args.scheduled, args.status]):
        print("Error: Must specify one of --run-once, --scheduled, or --status")
        parser.print_help()
        sys.exit(1)
    
    # Initialize controller
    controller = AutomationController(config_path=args.config, dry_run=args.dry_run)
    
    if not controller.initialize():
        print("Failed to initialize automation system")
        sys.exit(1)
    
    # Execute requested action
    if args.status:
        controller.show_status()
    elif args.run_once:
        success = controller.run_once(job_id=args.job)
        sys.exit(0 if success else 1)
    elif args.scheduled:
        controller.run_scheduled()


if __name__ == '__main__':
    main()
