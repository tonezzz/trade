"""
Error notification system for automation failures.
Supports email notifications and status logging.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
import os
from pathlib import Path

from src.logging_config import get_logger


@dataclass
class NotificationConfig:
    """Configuration for notifications."""
    enabled: bool = False
    email: Optional[str] = None
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None


class NotificationManager:
    """Manages error notifications for automation system."""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.notification_history: List[dict] = []
    
    def send_error_notification(
        self,
        job_name: str,
        error_message: str,
        traceback: str = None,
        retry_count: int = 0
    ) -> bool:
        """
        Send error notification.
        
        Args:
            job_name: Name of the job that failed
            error_message: Error message
            traceback: Optional traceback string
            retry_count: Number of retry attempts
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.config.enabled:
            self.logger.debug("Notifications disabled, skipping error notification")
            return False
        
        if not self.config.email:
            self.logger.warning("Notification enabled but no email configured")
            return False
        
        try:
            subject = f"❌ Automation Failure: {job_name}"
            body = self._format_error_email(
                job_name, error_message, traceback, retry_count
            )
            
            success = self._send_email(self.config.email, subject, body)
            
            if success:
                self.logger.info(f"Error notification sent for job: {job_name}")
                self.notification_history.append({
                    'timestamp': datetime.now(),
                    'type': 'error',
                    'job_name': job_name,
                    'message': error_message,
                    'sent': True
                })
            else:
                self.logger.error(f"Failed to send error notification for job: {job_name}")
                self.notification_history.append({
                    'timestamp': datetime.now(),
                    'type': 'error',
                    'job_name': job_name,
                    'message': error_message,
                    'sent': False
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def send_summary_notification(
        self,
        total_jobs: int,
        successful: int,
        failed: int,
        results: List[dict]
    ) -> bool:
        """
        Send summary notification after automation run.
        
        Args:
            total_jobs: Total number of jobs
            successful: Number of successful jobs
            failed: Number of failed jobs
            results: List of job results
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.config.enabled:
            self.logger.debug("Notifications disabled, skipping summary notification")
            return False
        
        if not self.config.email:
            self.logger.warning("Notification enabled but no email configured")
            return False
        
        try:
            subject = f"📊 Automation Summary: {successful}/{total_jobs} Successful"
            body = self._format_summary_email(
                total_jobs, successful, failed, results
            )
            
            success = self._send_email(self.config.email, subject, body)
            
            if success:
                self.logger.info("Summary notification sent")
            else:
                self.logger.error("Failed to send summary notification")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending summary notification: {e}")
            return False
    
    def _format_error_email(
        self,
        job_name: str,
        error_message: str,
        traceback: str = None,
        retry_count: int = 0
    ) -> str:
        """Format error email body."""
        body = f"""
Automation Job Failure Alert
{'=' * 50}

Job Name: {job_name}
Failure Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Retry Attempts: {retry_count}

Error Message:
{error_message}

"""
        if traceback:
            body += f"Traceback:\n{traceback}\n\n"
        
        body += f"Please check the logs for more details.\n"
        body += f"Log file: logs/automation.log\n"
        
        return body
    
    def _format_summary_email(
        self,
        total_jobs: int,
        successful: int,
        failed: int,
        results: List[dict]
    ) -> str:
        """Format summary email body."""
        body = f"""
Automation Run Summary
{'=' * 50}

Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Jobs: {total_jobs}
Successful: {successful}
Failed: {failed}

"""
        if failed > 0:
            body += "\nFailed Jobs:\n"
            for result in results:
                if result.get('status') == 'failed':
                    body += f"  - {result.get('job_name')}: {result.get('error_message', 'Unknown error')}\n"
        
        body += "\nDetailed Results:\n"
        for result in results:
            status_symbol = "✅" if result.get('status') == 'success' else "❌"
            body += f"  {status_symbol} {result.get('job_name')}: {result.get('status')}\n"
        
        body += f"\nLog file: logs/automation.log\n"
        
        return body
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP."""
        try:
            if not self.config.smtp_username or not self.config.smtp_password:
                self.logger.warning("SMTP credentials not configured, cannot send email")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.config.from_email or self.config.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP error: {e}")
            return False
    
    def get_notification_history(self) -> List[dict]:
        """Get history of sent notifications."""
        return self.notification_history.copy()


class StatusLogger:
    """Logs automation status to file for monitoring."""
    
    def __init__(self, log_file: str = "logs/status.log"):
        self.log_file = log_file
        self.logger = get_logger(__name__)
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_status(self, status: dict):
        """
        Log status information.
        
        Args:
            status: Dictionary containing status information
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] {status}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            
            self.logger.debug(f"Status logged: {status}")
            
        except Exception as e:
            self.logger.error(f"Error logging status: {e}")
    
    def log_job_start(self, job_name: str):
        """Log job start."""
        self.log_status({
            'event': 'job_start',
            'job_name': job_name,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_job_complete(self, job_name: str, status: str, records: int = 0):
        """Log job completion."""
        self.log_status({
            'event': 'job_complete',
            'job_name': job_name,
            'status': status,
            'records_processed': records,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_job_error(self, job_name: str, error: str):
        """Log job error."""
        self.log_status({
            'event': 'job_error',
            'job_name': job_name,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_automation_start(self):
        """Log automation start."""
        self.log_status({
            'event': 'automation_start',
            'timestamp': datetime.now().isoformat()
        })
    
    def log_automation_complete(self, total_jobs: int, successful: int, failed: int):
        """Log automation completion."""
        self.log_status({
            'event': 'automation_complete',
            'total_jobs': total_jobs,
            'successful': successful,
            'failed': failed,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_recent_status(self, lines: int = 100) -> List[str]:
        """Get recent status log entries."""
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
            
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        except Exception as e:
            self.logger.error(f"Error reading status log: {e}")
            return []


def load_notification_config_from_env() -> NotificationConfig:
    """Load notification configuration from environment variables."""
    return NotificationConfig(
        enabled=os.getenv('NOTIFICATIONS_ENABLED', 'false').lower() == 'true',
        email=os.getenv('NOTIFICATION_EMAIL'),
        smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_username=os.getenv('SMTP_USERNAME'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('SMTP_FROM_EMAIL')
    )
