
---

**Last Updated:** 2026-08-05
# Automation System Quick Start Guide

## Quick Commands

```bash
# Test the system (dry run)
python scripts/auto_update.py --run-once --dry-run

# Check status
python scripts/auto_update.py --status

# Run all jobs once
python scripts/auto_update.py --run-once

# Run specific job
python scripts/auto_update.py --run-once --job wti_oil

# Start continuous scheduler
python scripts/auto_update.py --scheduled
```

## Configuration Quick Reference

### Enable a Data Source
```yaml
data_sources:
  wti_oil:
    enabled: true
```

### Set Schedule
```yaml
# Daily at 6 AM
schedule: "daily"
schedule_time: "06:00"

# Weekly on Monday at 8 AM
schedule: "weekly"
schedule_day: "monday"
schedule_time: "08:00"
```

### Enable Notifications
```yaml
settings:
  enable_notifications: true
  notification_email: "your_email@example.com"
```

### Environment Variables
```bash
# .env file
NOTIFICATIONS_ENABLED=true
NOTIFICATION_EMAIL=your_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## Common Data Source Templates

### Daily Commodity
```yaml
commodity_daily:
  name: "Commodity Name"
  type: "commodity"
  symbol: "SYMBOL"
  commodity: "COMMODITY"
  unit: "unit"
  url: "https://example.com/data.csv"
  schedule: "daily"
  schedule_time: "06:00"
  import_function: "import_commodity_prices"
  source: "automated_source"
  enabled: true
```

### Exchange Rate
```yaml
exchange_rate:
  name: "Exchange Rate"
  type: "exchange_rate"
  url: "https://example.com/rates.xml"
  schedule: "daily"
  schedule_time: "17:00"
  import_function: "import_exchange_rates"
  source: "automated_rates"
  enabled: true
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Validation errors | Set `skip_validation: true` in config |
| Download fails | Check URL availability |
| No notifications | Check SMTP settings in .env |
| Wrong schedule time | Verify timezone and schedule_time format |
| Database errors | Check DB credentials in .env |

## Log Files

- `logs/automation.log` - Main execution log
- `logs/automation_status.log` - Status events

## Pre-configured Data Sources

The system comes with 5 pre-configured data sources:

1. **WTI Oil** - Daily at 6:00 AM
2. **Brent Oil** - Daily at 6:00 AM  
3. **ECB Exchange Rates** - Daily at 5:00 PM
4. **US Dollar Index** - Daily at 6:00 PM
5. **Gold Prices** - Weekly on Monday at 8:00 AM

All are enabled by default. Set `enabled: false` to disable any source.
