#!/usr/bin/env python3
"""
Data Quality Scheduler
Manages scheduled data quality checks and reporting.
"""
import sys
import os
import argparse
import signal
from pathlib import Path
from datetime import datetime, timedelta
import yaml

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_quality_agent import DataQualityAgent
from src.logging_config import setup_logging, get_logger


class QualityScheduler:
    """Scheduler for data quality checks."""
    
    def __init__(self, config_path: str = "config/ssot/ssot.data.yml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = get_logger(__name__)
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def check_data_quality_enabled(self):
        """Check if data quality checks are enabled."""
        data_quality_config = self.config.get('settings', {}).get('data_quality', {})
        return data_quality_config.get('enabled', False)
    
    def run_quality_checks(self):
        """Run data quality checks."""
        if not self.check_data_quality_enabled():
            self.logger.info("Data quality checks are disabled in configuration")
            return
        
        self.logger.info("Running data quality checks...")
        
        try:
            # Get data quality settings
            dq_config = self.config.get('settings', {}).get('data_quality', {})
            tolerance = dq_config.get('tolerance_pct', 2.0)
            freshness = dq_config.get('max_freshness_days', 2)
            
            # Initialize data quality agent with configured tolerance
            agent = DataQualityAgent(tolerance_pct=tolerance, max_freshness_days=freshness)
            
            # Run comprehensive quality check
            report = agent.run_full_validation()
            
            # Log results
            self.logger.info(f"Quality check completed: {report.get('overall_quality', 'unknown')}")
            self.logger.info(f"Data freshness: {report.get('data_freshness', 'unknown')}")
            self.logger.info(f"Completeness: {report.get('completeness', 'unknown')}")
            self.logger.info(f"Success rate: {report.get('success_rate', 'unknown')}")
            
            # Check if quality meets thresholds
            min_completeness = dq_config.get('min_completeness_pct', 90.0)
            completeness = report.get('completeness', 0)
            if completeness and completeness < min_completeness:
                self.logger.warning(f"Data completeness ({completeness}%) below threshold ({min_completeness}%)")
            
            # Store results for history tracking
            self.store_quality_history(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error running quality checks: {e}")
            return None
    
    def store_quality_history(self, report):
        """Store quality check results for history tracking."""
        try:
            history_file = Path("data/quality_history.jsonl")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'overall_quality': report.get('overall_quality', 'unknown'),
                'data_freshness': report.get('data_freshness', 'unknown'),
                'completeness': report.get('completeness', 0),
                'total_validated': report.get('total_validated', 0),
                'total_accurate': report.get('total_accurate', 0),
                'success_rate': report.get('success_rate', 0),
                'currency_issues': len(report.get('currency_issues', [])),
                'commodity_issues': len(report.get('commodity_issues', [])),
                'dxy_issues': len(report.get('dxy_issues', []))
            }
            
            with open(history_file, 'a') as f:
                import json
                f.write(json.dumps(history_entry) + '\n')
                
            self.logger.info(f"Quality history stored: {history_file}")
            
        except Exception as e:
            self.logger.error(f"Error storing quality history: {e}")
    
    def run_scheduled_checks(self):
        """Run checks according to schedule."""
        schedule = self.config.get('data_quality', {}).get('schedule', 'daily')
        schedule_time = self.config.get('data_quality', {}).get('schedule_time', '18:00')
        
        self.logger.info(f"Starting quality scheduler (schedule: {schedule} at {schedule_time})")
        self.running = True
        
        while self.running:
            try:
                # Check if it's time to run
                now = datetime.now()
                current_time = now.strftime('%H:%M')
                
                if current_time == schedule_time:
                    self.logger.info("Scheduled quality check time reached")
                    self.run_quality_checks()
                    
                    # Wait until next day to avoid multiple runs
                    import time
                    time.sleep(3600)  # Wait 1 hour
                
                # Sleep for 1 minute before checking again
                import time
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                import time
                time.sleep(60)
    
    def run_once(self):
        """Run quality checks once and exit."""
        self.logger.info("Running quality checks once...")
        report = self.run_quality_checks()
        
        if report:
            self.logger.info("Quality check completed successfully")
            return 0
        else:
            self.logger.error("Quality check failed")
            return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Data Quality Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all quality tasks once (for testing)
  python scripts/schedule_quality_checks.py --run-once
  
  # Start the quality scheduler daemon
  python scripts/schedule_quality_checks.py
  
  # Start with custom configuration
  python scripts/schedule_quality_checks.py --config /path/to/config.yml
        """
    )
    
    parser.add_argument(
        '--config',
        default='config/ssot/ssot.data.yml',
        help='Path to configuration file (default: config/ssot/ssot.data.yml)'
    )
    
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run all quality tasks once and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize scheduler
    scheduler = QualityScheduler(config_path=args.config)
    
    # Execute requested action
    if args.run_once:
        exit_code = scheduler.run_once()
        sys.exit(exit_code)
    else:
        scheduler.run_scheduled_checks()


if __name__ == '__main__':
    main()