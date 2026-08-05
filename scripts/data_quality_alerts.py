#!/usr/bin/env python3
"""
Data Quality Alert System

Provides alerting capabilities for data quality issues including:
- Email notifications
- System logging
- Webhook integrations
- Console alerts
"""
import smtplib
import logging
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
import requests

logger = logging.getLogger('DataQualityAlerts')


@dataclass
class AlertConfig:
    """Configuration for alert system."""
    enabled: bool = True
    email_enabled: bool = False
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: List[str] = None
    webhook_enabled: bool = False
    webhook_url: str = ""
    log_alerts: bool = True
    console_alerts: bool = True
    alert_threshold: int = 3  # Number of failures before alerting


class AlertSystem:
    """Manages data quality alerts across multiple channels."""
    
    def __init__(self, config: AlertConfig = None):
        """
        Initialize alert system.
        
        Args:
            config: Alert configuration (uses defaults if not provided)
        """
        self.config = config or AlertConfig()
        self.alert_history = []
        self.failure_count = {}
        
        # Load configuration from environment if available
        self._load_env_config()
    
    def _load_env_config(self):
        """Load alert configuration from environment variables."""
        self.config.email_enabled = os.getenv('ALERT_EMAIL_ENABLED', 'false').lower() == 'true'
        self.config.email_smtp_server = os.getenv('ALERT_SMTP_SERVER', self.config.email_smtp_server)
        self.config.email_smtp_port = int(os.getenv('ALERT_SMTP_PORT', self.config.email_smtp_port))
        self.config.email_username = os.getenv('ALERT_EMAIL_USERNAME', '')
        self.config.email_password = os.getenv('ALERT_EMAIL_PASSWORD', '')
        
        recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '')
        if recipients:
            self.config.email_recipients = [r.strip() for r in recipients.split(',')]
        
        self.config.webhook_enabled = os.getenv('ALERT_WEBHOOK_ENABLED', 'false').lower() == 'true'
        self.config.webhook_url = os.getenv('ALERT_WEBHOOK_URL', '')
        self.config.alert_threshold = int(os.getenv('ALERT_THRESHOLD', str(self.config.alert_threshold)))
    
    def send_alert(self, validation_result: Dict, alert_type: str = "warning"):
        """
        Send alert through configured channels.
        
        Args:
            validation_result: Validation result data
            alert_type: Type of alert (warning, critical, info)
        """
        if not self.config.enabled:
            return
        
        symbol = validation_result.get('symbol', 'unknown')
        data_type = validation_result.get('data_type', 'unknown')
        issues = validation_result.get('issues', [])
        
        # Track failure count per symbol
        key = f"{data_type}_{symbol}"
        self.failure_count[key] = self.failure_count.get(key, 0) + 1
        
        # Only send alert if threshold exceeded
        if self.failure_count[key] < self.config.alert_threshold:
            logger.info(f"Failure count for {key}: {self.failure_count[key]}/{self.config.alert_threshold} (not alerting yet)")
            return
        
        # Create alert message
        message = self._create_alert_message(validation_result, alert_type)
        
        # Send through configured channels
        if self.config.console_alerts:
            self._send_console_alert(message, alert_type)
        
        if self.config.log_alerts:
            self._send_log_alert(message, alert_type)
        
        if self.config.email_enabled:
            self._send_email_alert(message, alert_type)
        
        if self.config.webhook_enabled:
            self._send_webhook_alert(validation_result, alert_type)
        
        # Record alert history
        self.alert_history.append({
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'data_type': data_type,
            'alert_type': alert_type,
            'message': message
        })
        
        # Reset failure count after alert
        self.failure_count[key] = 0
    
    def _create_alert_message(self, validation_result: Dict, alert_type: str) -> str:
        """Create formatted alert message."""
        symbol = validation_result.get('symbol', 'unknown')
        data_type = validation_result.get('data_type', 'unknown')
        issues = validation_result.get('issues', [])
        db_value = validation_result.get('db_value')
        external_value = validation_result.get('external_value')
        difference_pct = validation_result.get('difference_pct')
        freshness_days = validation_result.get('freshness_days')
        
        message = f"""
DATA QUALITY ALERT - {alert_type.upper()}
{'=' * 50}
Symbol: {symbol}
Data Type: {data_type}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Issues:
"""
        for issue in issues:
            message += f"  - {issue}\n"
        
        if db_value is not None:
            message += f"\nDatabase Value: {db_value:.4f}"
        
        if external_value is not None:
            message += f"\nExternal Value: {external_value:.4f}"
        
        if difference_pct is not None:
            message += f"\nDifference: {difference_pct:.2f}%"
        
        if freshness_days is not None:
            message += f"\nData Age: {freshness_days} days"
        
        message += f"\n{'=' * 50}"
        
        return message
    
    def _send_console_alert(self, message: str, alert_type: str):
        """Send alert to console."""
        if alert_type == "critical":
            print(f"\n🚨 CRITICAL ALERT 🚨{message}\n")
        elif alert_type == "warning":
            print(f"\n⚠️  WARNING ALERT ⚠️{message}\n")
        else:
            print(f"\nℹ️  INFO ALERT ℹ️{message}\n")
    
    def _send_log_alert(self, message: str, alert_type: str):
        """Send alert to log file."""
        if alert_type == "critical":
            logger.critical(message)
        elif alert_type == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def _send_email_alert(self, message: str, alert_type: str):
        """Send alert via email."""
        if not self.config.email_recipients:
            logger.warning("Email alerts enabled but no recipients configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.email_username
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = f"Data Quality Alert - {alert_type.upper()}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port) as server:
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(self.config.email_recipients)} recipients")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_webhook_alert(self, validation_result: Dict, alert_type: str):
        """Send alert via webhook."""
        if not self.config.webhook_url:
            logger.warning("Webhook alerts enabled but no URL configured")
            return
        
        try:
            payload = {
                'alert_type': alert_type,
                'timestamp': datetime.now().isoformat(),
                'validation_result': validation_result
            }
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Webhook alert sent successfully")
            else:
                logger.warning(f"Webhook returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def send_summary_alert(self, summary: Dict):
        """
        Send summary alert after full validation run.
        
        Args:
            summary: Validation summary data
        """
        if not self.config.enabled:
            return
        
        failed_count = summary.get('failed_validations', 0)
        total_count = summary.get('total_validations', 0)
        success_rate = summary.get('success_rate', 0)
        
        if failed_count == 0:
            # All good - send info alert
            message = f"""
DATA QUALITY SUMMARY - SUCCESS
{'=' * 50}
Timestamp: {summary.get('timestamp')}
Total Validations: {total_count}
Failed Validations: {failed_count}
Success Rate: {success_rate:.1f}%
Duration: {summary.get('duration_seconds', 0):.2f} seconds
{'=' * 50}
"""
            if self.config.console_alerts:
                print(f"\n✅ {message}\n")
            if self.config.log_alerts:
                logger.info(message)
        else:
            # Issues found - send warning alert
            message = f"""
DATA QUALITY SUMMARY - ISSUES FOUND
{'=' * 50}
Timestamp: {summary.get('timestamp')}
Total Validations: {total_count}
Failed Validations: {failed_count}
Success Rate: {success_rate:.1f}%
Duration: {summary.get('duration_seconds', 0):.2f} seconds

⚠️  {failed_count} data quality issues detected
{'=' * 50}
"""
            if self.config.console_alerts:
                print(f"\n⚠️  {message}\n")
            if self.config.log_alerts:
                logger.warning(message)
            
            # Send email/webhook for failures
            if self.config.email_enabled:
                self._send_email_alert(message, "warning")
            if self.config.webhook_enabled:
                self._send_webhook_alert({'summary': summary}, "warning")
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent alert history.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alert_history[-limit:]


def main():
    """Test the alert system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Data Quality Alert System')
    parser.add_argument('--type', choices=['warning', 'critical', 'info'], 
                       default='warning', help='Alert type to test')
    parser.add_argument('--test-email', action='store_true',
                       help='Test email alert')
    parser.add_argument('--test-webhook', action='store_true',
                       help='Test webhook alert')
    
    args = parser.parse_args()
    
    config = AlertConfig()
    alert_system = AlertSystem(config)
    
    # Test validation result
    test_result = {
        'symbol': 'THB',
        'data_type': 'exchange_rates',
        'db_value': 35.4,
        'external_value': 33.37,
        'difference_pct': 6.1,
        'freshness_days': 5,
        'issues': [
            'Value difference 6.10% exceeds tolerance 2.0%',
            'Data is 5 days old (max: 2)'
        ]
    }
    
    print("Testing alert system...")
    alert_system.send_alert(test_result, args.type)
    
    # Test summary
    test_summary = {
        'timestamp': datetime.now().isoformat(),
        'total_validations': 10,
        'failed_validations': 2,
        'success_rate': 80.0,
        'duration_seconds': 5.2
    }
    
    alert_system.send_summary_alert(test_summary)
    
    print("Alert system test completed.")


if __name__ == '__main__':
    main()