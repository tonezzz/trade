#!/usr/bin/env python3
"""
Schedule and manage regular data quality checks.

This script provides functionality to:
1. Schedule regular data quality checks
2. Monitor weekly quality trends
3. Generate quality reports
4. Send scheduled notifications
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import json
import subprocess

# Import the data quality agent
from scripts.data_quality_agent import DataQualityAgent
from scripts.data_quality_alerts import AlertSystem, AlertConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/quality_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('QualityScheduler')


class QualityScheduler:
    """Manages scheduled data quality checks and monitoring."""
    
    def __init__(self, config_path: str = "config/data_sources.yml"):
        """Initialize the quality scheduler."""
        self.config = self._load_config(config_path)
        self.quality_config = self.config.get('settings', {}).get('data_quality', {})
        
        # Initialize alert system
        alert_config = AlertConfig(
            enabled=self.quality_config.get('alert_threshold', 3) > 0,
            alert_threshold=self.quality_config.get('alert_threshold', 3)
        )
        self.alert_system = AlertSystem(alert_config)
        
        # Load environment-specific settings
        self._load_env_config()
        
        logger.info("Quality Scheduler initialized")
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def _load_env_config(self):
        """Load configuration from environment variables."""
        # Override with environment variables if set
        self.quality_config['tolerance_pct'] = float(os.getenv('QUALITY_TOLERANCE', self.quality_config.get('tolerance_pct', 2.0)))
        self.quality_config['max_freshness_days'] = int(os.getenv('QUALITY_FRESHNESS_DAYS', self.quality_config.get('max_freshness_days', 2)))
        self.quality_config['min_completeness_pct'] = float(os.getenv('QUALITY_COMPLETENESS_PCT', self.quality_config.get('min_completeness_pct', 90.0)))
    
    def run_quality_check(self):
        """Run a scheduled data quality check."""
        logger.info("=" * 60)
        logger.info("Running scheduled data quality check")
        logger.info("=" * 60)
        
        try:
            agent = DataQualityAgent(
                tolerance_pct=self.quality_config.get('tolerance_pct', 2.0),
                max_freshness_days=self.quality_config.get('max_freshness_days', 2)
            )
            
            summary = agent.run_full_validation()
            
            # Send alert if there are failures
            if summary['failed_validations'] > 0:
                self.alert_system.send_summary_alert(summary)
            
            logger.info(f"Quality check completed: {summary['success_rate']:.1f}% success rate")
            
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            # Send error alert
            self.alert_system.send_alert({
                'symbol': 'SYSTEM',
                'data_type': 'quality_check',
                'issues': [f"Scheduled quality check failed: {str(e)}"]
            }, "critical")
    
    def generate_weekly_report(self):
        """Generate weekly quality trend report."""
        logger.info("Generating weekly quality report...")
        
        try:
            agent = DataQualityAgent()
            history = agent.get_quality_history(days=7)
            
            if not history:
                logger.warning("No quality history available for weekly report")
                return
            
            # Calculate weekly statistics
            total_checks = len(history)
            avg_success_rate = sum(h['success_rate'] for h in history) / total_checks if total_checks > 0 else 0
            avg_failures = sum(h['failed_validations'] for h in history) / total_checks if total_checks > 0 else 0
            
            # Find trends
            recent_success = history[-1]['success_rate'] if history else 0
            earlier_success = history[0]['success_rate'] if len(history) > 1 else recent_success
            trend = recent_success - earlier_success
            
            # Generate report
            report = {
                'report_date': datetime.now().isoformat(),
                'period_days': 7,
                'total_checks': total_checks,
                'average_success_rate': avg_success_rate,
                'average_failures': avg_failures,
                'trend_percentage_points': trend,
                'trend_direction': 'improving' if trend > 0 else 'declining' if trend < 0 else 'stable',
                'recent_success_rate': recent_success,
                'earliest_success_rate': earlier_success,
                'data_points': history
            }
            
            # Save report
            reports_dir = 'data/quality/reports'
            Path(reports_dir).mkdir(parents=True, exist_ok=True)
            
            report_file = os.path.join(reports_dir, f'weekly_report_{datetime.now().strftime("%Y%m%d")}.json')
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Weekly report saved to: {report_file}")
            
            # Send summary alert
            summary_message = f"""
WEEKLY DATA QUALITY REPORT
{'=' * 50}
Period: Last 7 days
Total Checks: {total_checks}
Average Success Rate: {avg_success_rate:.1f}%
Average Failures: {avg_failures:.1f}
Trend: {report['trend_direction']} ({trend:+.1f} percentage points)
Recent Success Rate: {recent_success:.1f}%
{'=' * 50}
"""
            
            if trend < -5:  # Significant decline
                self.alert_system.send_alert({
                    'symbol': 'QUALITY_TREND',
                    'data_type': 'weekly_report',
                    'issues': [f"Data quality declining by {abs(trend):.1f} percentage points over 7 days"]
                }, "warning")
            
            logger.info(summary_message)
            
        except Exception as e:
            logger.error(f"Failed to generate weekly report: {e}")
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """Clean up old quality records."""
        logger.info(f"Cleaning up quality records older than {days_to_keep} days...")
        
        try:
            quality_dir = Path('data/quality')
            if not quality_dir.exists():
                return
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for file_path in quality_dir.glob('validation_*.json'):
                try:
                    # Extract date from filename
                    file_date_str = file_path.stem.replace('validation_', '')
                    file_date = datetime.strptime(file_date_str, '%Y%m%d_%H%M%S')
                    
                    if file_date < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old record: {file_path.name}")
                
                except ValueError:
                    # Skip files that don't match the expected format
                    continue
            
            logger.info(f"Cleanup completed: {deleted_count} files deleted")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def setup_schedule(self):
        """Set up the scheduled tasks."""
        if not self.quality_config.get('enabled', True):
            logger.info("Data quality scheduling is disabled")
            return
        
        # Schedule daily quality check
        schedule_time = self.quality_config.get('schedule_time', '18:00')
        schedule.every().day.at(schedule_time).do(self.run_quality_check)
        logger.info(f"Scheduled daily quality check at {schedule_time}")
        
        # Schedule weekly report (every Monday at 9:00 AM)
        schedule.every().monday.at("09:00").do(self.generate_weekly_report)
        logger.info("Scheduled weekly quality report for Mondays at 09:00")
        
        # Schedule monthly cleanup (1st of each month at 3:00 AM)
        schedule.every().month.do(self.cleanup_old_records)
        logger.info("Scheduled monthly cleanup for 1st of each month")
    
    def run_once(self):
        """Run all tasks once for testing."""
        logger.info("Running all quality tasks once...")
        self.run_quality_check()
        self.generate_weekly_report()
        self.cleanup_old_records()
    
    def start_scheduler(self):
        """Start the scheduler loop."""
        logger.info("Starting quality scheduler...")
        self.setup_schedule()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Quality Scheduler')
    parser.add_argument('--run-once', action='store_true',
                       help='Run all tasks once and exit')
    parser.add_argument('--config', default='config/data_sources.yml',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    scheduler = QualityScheduler(args.config)
    
    if args.run_once:
        scheduler.run_once()
    else:
        scheduler.start_scheduler()


if __name__ == '__main__':
    main()