
---

**Last Updated:** 2026-08-05
# Automation System Guide

## Overview

The automation system provides a hands-off solution for automatically downloading and importing financial data on a scheduled basis. It supports multiple data sources, configurable schedules, automatic retry logic, error notifications, and comprehensive status logging.

## Components

### 1. Configuration System (`config/data_sources.yml`)

The configuration file defines all data sources, their download URLs, scheduling information, and processing parameters.

**Key Sections:**
- **Global Settings**: System-wide configuration including directories, retry logic, logging, and notifications
- **Data Sources**: Individual job configurations for each data source

**Configuration Format:**
```yaml
settings:
  download_dir: "data/archive"           # Directory for downloaded files
  import_dir: "data/imported"             # Directory for formatted files
  max_retries: 3                          # Number of retry attempts
  retry_delay: 5                          # Initial retry delay (seconds)
  dry_run: false                          # Enable/disable dry run mode
  log_file: "logs/automation.log"         # Main log file path
  enable_notifications: false             # Enable email notifications
  notification_email: ""                  # Notification email address
  skip_validation: false                  # Skip validation errors

data_sources:
  job_id:
    name: "Job Name"
    description: "Job description"
    type: "commodity|exchange_rate|dollar_index"
    url: "https://example.com/data.csv"
    schedule: "daily|weekly|hourly|interval"
    schedule_time: "HH:MM"                # Required for daily/weekly
    schedule_day: "monday|tuesday|..."    # Required for weekly
    import_function: "import_commodity_prices|import_exchange_rates|import_dollar_index"
    source: "data_source_identifier"
    enabled: true
    formatter: "optional_formatter_function"
    # Type-specific fields
    symbol: "SYMBOL"
    commodity: "COMMODITY"
    unit: "unit_of_measure"
    base_currency: "USD"
    quote_currency: "EUR"
```

### 2. Scheduler Module (`src/scheduler.py`)

The scheduler module handles job execution, retry logic, and status tracking.

**Key Classes:**
- **JobScheduler**: Main scheduler class that manages all jobs
- **RetryHandler**: Handles retry logic with exponential backoff
- **JobConfig**: Data class for job configuration
- **JobResult**: Data class for job execution results
- **JobStatus**: Enum for job status (PENDING, RUNNING, SUCCESS, FAILED, RETRYING)

**Key Features:**
- Automatic retry with exponential backoff
- Dry run mode for testing
- Integration with existing download and import functions
- Comprehensive error handling and logging
- Status tracking and history

### 3. Automation Script (`scripts/auto_update.py`)

The main automation script provides command-line interface for running the system.

**Usage:**
```bash
# Run all jobs once (for testing)
python scripts/auto_update.py --run-once

# Run a specific job once
python scripts/auto_update.py --run-once --job wti_oil

# Start the scheduler in continuous mode
python scripts/auto_update.py --scheduled

# Show current job status
python scripts/auto_update.py --status

# Dry run (no actual downloads/imports)
python scripts/auto_update.py --run-once --dry-run

# Use custom configuration file
python scripts/auto_update.py --config /path/to/config.yml --run-once
```

### 4. Notification System (`src/notifications.py`)

The notification system handles error notifications and status logging.

**Key Classes:**
- **NotificationManager**: Manages email notifications for errors and summaries
- **NotificationConfig**: Configuration for notification settings
- **StatusLogger**: Logs automation status to file for monitoring

**Features:**
- Email notifications on job failures
- Summary notifications after automation runs
- Detailed status logging
- Notification history tracking

## Setup Instructions

### 1. Install Dependencies

Ensure all required packages are installed:

```bash
pip install -r requirements.txt
```

Required packages:
- `schedule>=1.2.0` - Job scheduling
- `pyyaml>=6.0` - YAML configuration parsing
- Existing dependencies (pandas, sqlalchemy, etc.)

### 2. Configure Data Sources

Edit `config/data_sources.yml` to configure your data sources:

```yaml
data_sources:
  wti_oil:
    name: "WTI Crude Oil"
    url: "https://example.com/wti.csv"
    schedule: "daily"
    schedule_time: "06:00"
    import_function: "import_commodity_prices"
    enabled: true
```

### 3. Configure Environment Variables

Set up environment variables in `.env` file:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dollar_prices
DB_USER=postgres
DB_PASSWORD=your_password

# Notification Configuration (optional)
NOTIFICATIONS_ENABLED=false
NOTIFICATION_EMAIL=your_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=your_email@example.com
```

### 4. Test the System

Run a dry run to test the configuration:

```bash
python scripts/auto_update.py --run-once --dry-run
```

This will simulate the automation process without actually downloading or importing data.

### 5. Run a Single Job

Test a specific job:

```bash
python scripts/auto_update.py --run-once --job wti_oil
```

### 6. Start the Scheduler

For production use, start the scheduler in continuous mode:

```bash
python scripts/auto_update.py --scheduled
```

The scheduler will run continuously and execute jobs according to their schedules.

## Data Source Configuration Examples

### Daily Commodity Data (WTI Oil)

```yaml
wti_oil:
  name: "WTI Crude Oil"
  description: "West Texas Intermediate crude oil daily prices"
  type: "commodity"
  symbol: "WTI"
  commodity: "OIL"
  unit: "barrel"
  url: "https://raw.githubusercontent.com/datasets/oil-prices/main/data/wti-daily.csv"
  schedule: "daily"
  schedule_time: "06:00"
  import_function: "import_commodity_prices"
  source: "automated_wti"
  enabled: true
  formatter: "format_wti_data"
```

### Weekly Data (Gold Prices)

```yaml
gold:
  name: "Gold Prices"
  description: "Gold (XAU) daily prices"
  type: "commodity"
  symbol: "XAU"
  commodity: "GOLD"
  unit: "oz"
  url: "https://raw.githubusercontent.com/datasets/gold-prices/main/data/gold-daily.csv"
  schedule: "weekly"
  schedule_day: "monday"
  schedule_time: "08:00"
  import_function: "import_commodity_prices"
  source: "automated_gold"
  enabled: true
  formatter: "format_gold_data"
```

### Exchange Rates (ECB)

```yaml
ecb_exchange_rates:
  name: "ECB Exchange Rates"
  description: "European Central Bank daily reference exchange rates"
  type: "exchange_rate"
  url: "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
  schedule: "daily"
  schedule_time: "17:00"
  import_function: "import_exchange_rates"
  source: "automated_ecb"
  enabled: true
  formatter: "format_ecb_data"
  base_currency: "EUR"
```

## Scheduling Options

### Daily Schedule
```yaml
schedule: "daily"
schedule_time: "06:00"  # 24-hour format
```

### Weekly Schedule
```yaml
schedule: "weekly"
schedule_day: "monday"  # monday, tuesday, wednesday, etc.
schedule_time: "08:00"
```

### Hourly Schedule
```yaml
schedule: "hourly"
```

### Interval Schedule
```yaml
schedule: "interval"
# Default interval is 1 hour
```

## Error Handling and Retry Logic

The system implements automatic retry logic with exponential backoff:

- **Initial Delay**: 5 seconds (configurable)
- **Backoff Factor**: 2x (delay doubles with each retry)
- **Max Retries**: 3 attempts (configurable)

**Example Retry Timeline:**
- Attempt 1: Immediate
- Attempt 2: 5 seconds delay
- Attempt 3: 10 seconds delay
- Attempt 4: 20 seconds delay

## Monitoring and Logging

### Log Files

- **Main Log**: `logs/automation.log` - Detailed execution logs
- **Status Log**: `logs/automation_status.log` - Structured status events
- **Error Logs**: Included in main log with ERROR level

### Status Monitoring

Check current status:
```bash
python scripts/auto_update.py --status
```

### Log Analysis

View recent status events:
```python
from src.notifications import StatusLogger

status_logger = StatusLogger()
recent_status = status_logger.get_recent_status(lines=100)
```

## Email Notifications

### Setup

1. Enable notifications in configuration:
```yaml
settings:
  enable_notifications: true
  notification_email: "your_email@example.com"
```

2. Configure SMTP settings in `.env`:
```bash
NOTIFICATIONS_ENABLED=true
NOTIFICATION_EMAIL=your_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
```

### Notification Types

- **Error Notifications**: Sent immediately when a job fails
- **Summary Notifications**: Sent after each automation run with success/failure statistics

## Production Deployment

### Using Cron (Alternative to Built-in Scheduler)

If you prefer using cron instead of the built-in scheduler:

```bash
# Add to crontab
crontab -e

# Run daily at 6 AM
0 6 * * * cd /path/to/trade && source venv/bin/activate && python scripts/auto_update.py --run-once

# Run weekly on Monday at 8 AM
0 8 * * 1 cd /path/to/trade && source venv/bin/activate && python scripts/auto_update.py --run-once
```

### Using Systemd (Linux)

Create a systemd service file `/etc/systemd/system/trade-automation.service`:

```ini
[Unit]
Description=Trade Data Automation
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/trade
Environment="PATH=/path/to/trade/venv/bin"
ExecStart=/path/to/trade/venv/bin/python scripts/auto_update.py --scheduled
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable trade-automation
sudo systemctl start trade-automation
sudo systemctl status trade-automation
```

### Using Docker (Optional)

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scripts/auto_update.py", "--scheduled"]
```

## Troubleshooting

### Common Issues

**Issue**: Jobs fail with validation errors
- **Solution**: Enable `skip_validation: true` in configuration, or clean the data source

**Issue**: Download URLs are not accessible
- **Solution**: Check URL availability, consider using alternative data sources

**Issue**: Database connection errors
- **Solution**: Verify database credentials in `.env` file

**Issue**: Notifications not sending
- **Solution**: Check SMTP configuration, verify email credentials

**Issue**: Scheduler not running jobs on time
- **Solution**: Check system timezone, verify schedule configuration

### Debug Mode

Enable debug logging:
```yaml
settings:
  log_level: "DEBUG"
```

Or use command line:
```bash
python scripts/auto_update.py --run-once --log-level DEBUG
```

## Best Practices

1. **Test First**: Always use `--dry-run` before production deployment
2. **Monitor Logs**: Regularly check log files for errors and warnings
3. **Backup Data**: Keep backups of your database and configuration files
4. **Validate URLs**: Periodically verify that data source URLs are still accessible
5. **Review Schedules**: Adjust schedules based on data availability and your needs
6. **Enable Notifications**: Set up email notifications for production environments
7. **Document Changes**: Keep track of configuration changes and their reasons

## Advanced Features

### Custom Formatters

You can create custom formatter functions in `download_data.py`:

```python
def format_custom_data():
    """Custom formatter for specific data source."""
    input_file = 'data/archive/custom_raw.csv'
    output_file = 'data/imported/custom_formatted.csv'
    
    # Your custom formatting logic here
    # ...
    
    return output_file
```

Then reference it in configuration:
```yaml
custom_source:
  formatter: "format_custom_data"
```

### Conditional Scheduling

You can modify the scheduler to implement conditional logic based on:
- Business days only
- Market hours
- Data availability checks
- Custom triggers

### Integration with External Systems

The notification system can be extended to:
- Send Slack messages
- Post to webhooks
- Update monitoring systems
- Trigger external processes

## Support and Maintenance

### Regular Maintenance Tasks

1. **Review Logs**: Weekly review of automation logs
2. **Update URLs**: Monthly check of data source URLs
3. **Database Maintenance**: Regular database backups and optimization
4. **Configuration Updates**: Adjust schedules and data sources as needed
5. **Dependency Updates**: Keep Python packages up to date

### Getting Help

- Check logs in `logs/` directory
- Review configuration in `config/data_sources.yml`
- Run status check: `python scripts/auto_update.py --status`
- Test with dry run: `python scripts/auto_update.py --run-once --dry-run`

## Summary

The automation system provides a robust, hands-off solution for automated data download and import. With proper configuration and monitoring, it can reliably keep your financial data up-to-date without manual intervention.

Key benefits:
- **Automated**: No manual intervention required
- **Reliable**: Automatic retry logic and error handling
- **Flexible**: Configurable schedules and data sources
- **Monitorable**: Comprehensive logging and status tracking
- **Notifiable**: Email alerts for errors and summaries
- **Testable**: Dry run mode for safe testing
