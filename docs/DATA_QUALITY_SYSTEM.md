# Data Quality Monitoring System

**Last Updated:** 2026-08-07

## Overview
The Data Quality Monitoring System is designed to prevent data accuracy issues like the USD/THB problem we encountered. It provides automated validation, historical tracking, and alerting for all data in the trade database.

## Components

### 1. Data Quality Agent (`scripts/data_quality_agent.py`)
The core validation engine that:
- **Validates data accuracy** by comparing database values against external sources
- **Checks data freshness** to ensure data isn't stale
- **Measures data completeness** to detect gaps in historical data
- **Maintains historical records** of all validation runs
- **Generates detailed reports** with specific issues identified

**Key Features:**
- Configurable tolerance levels for acceptable differences
- Configurable maximum data age thresholds
- Multi-source validation (exchange rates, commodities, dollar index)
- JSON-based historical record keeping
- Integration with external APIs for real-time comparison

### 2. Alert System (`scripts/data_quality_alerts.py`)
Provides multi-channel alerting for data quality issues:
- **Console alerts** for immediate visibility
- **Log file alerts** for historical tracking
- **Email notifications** for critical issues
- **Webhook integrations** for external systems
- **Smart thresholding** to avoid alert fatigue

**Configuration:**
```bash
# Environment variables for alert configuration
ALERT_EMAIL_ENABLED=true
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=admin@example.com,trader@example.com
ALERT_WEBHOOK_ENABLED=true
ALERT_WEBHOOK_URL=https://your-webhook-url.com/alerts
ALERT_THRESHOLD=3  # Number of failures before alerting
```

### 3. Scheduler Integration (`src/scheduler.py`)
The data quality system is integrated into the existing automation:
- **Automatic validation** after each successful data import
- **Scheduled quality checks** as part of automation workflow
- **Notification integration** with existing notification system
- **Status tracking** alongside regular job status

## Usage

### Manual Validation
```bash
# Run full validation with default settings (2% tolerance, 2 days max age)
python cli.py quality

# Run with custom tolerance and freshness
python cli.py quality --tolerance 5.0 --freshness 7

# View historical quality data
python cli.py quality --history-only --history 30
```

### Scheduled Quality Checks
```bash
# Run all quality tasks once (for testing)
python cli.py quality-scheduler --run-once

# Start the quality scheduler daemon
python cli.py quality-scheduler

# Start with custom configuration
python cli.py quality-scheduler --config /path/to/config.yml
```

The scheduler automatically:
- **Daily quality checks** at configured time (default: 18:00)
- **Weekly reports** every Monday at 09:00
- **Monthly cleanup** on the 1st of each month

### Automated Validation
The system automatically runs data quality checks after each successful data import when using the scheduler. Failed validations trigger notifications based on your configuration.

### Standalone Agent
```bash
# Run the agent directly
python scripts/data_quality_agent.py --tolerance 2.0 --freshness 2

# Test the alert system
python scripts/data_quality_alerts.py --type warning --test-email
```

## Validation Criteria

### 1. Accuracy Validation
- Compares database values against external API sources
- Calculates percentage difference
- Flags differences exceeding configured tolerance
- **Exchange Rates**: Uses exchangerate-api.com (primary) and FRED API (secondary)
- **Commodities**: Uses Alpha Vantage API for WTI, BRENT, WHEAT, CORN, COPPER, NATURAL_GAS
- **Precious Metals**: Uses Minted Metal API (primary) and MetalPrices API (fallback) for GOLD/XAU, SILVER/XAG
- **Dollar Index**: Uses FRED API (DTWEXBGS series)

### 2. Freshness Validation
- Checks data age against current date
- Flags data older than configured threshold
- Helps identify failed automated updates
- Critical for time-sensitive trading data

### 3. Completeness Validation
- Measures expected vs actual data points
- Calculates percentage of data coverage
- Flags gaps in historical data
- Helps identify data import issues

## Historical Tracking

All validation results are stored in `data/quality/` directory:
- **File naming**: `validation_YYYYMMDD_HHMMSS.json`
- **Content**: Summary statistics + detailed per-symbol results
- **Retention**: Manual cleanup required (consider adding automated cleanup)

**Example output structure:**
```json
{
  "summary": {
    "timestamp": "2026-08-05T13:43:28",
    "duration_seconds": 6.16,
    "total_validations": 17,
    "failed_validations": 7,
    "success_rate": 58.8,
    "tolerance_pct": 15.0,
    "max_freshness_days": 10
  },
  "detailed_results": [
    {
      "symbol": "THB",
      "data_type": "exchange_rates",
      "is_accurate": true,
      "db_value": 33.42,
      "external_value": null,
      "freshness_days": 5,
      "issues": []
    }
  ]
}
```

## Prevention Strategy

This system would have prevented the USD/THB issue by:

1. **Detecting the wrong data source**: The monthly EXTHUS vs daily DEXTHUS issue would show up as completeness problems (monthly data has fewer points than expected for daily data)

2. **Identifying stale data**: The system would flag data older than 2 days, prompting investigation

3. **External validation**: When external APIs are integrated, significant differences between database and external values would trigger alerts

4. **Historical tracking**: Patterns of data quality issues would be visible over time, helping identify systemic problems

## Future Enhancements

### Completed Improvements (as of 2026-08-07)
1. **✅ Alpha Vantage API Integration** (commodities, oil prices)
   - **Status**: Fully implemented and tested
   - **Free tier**: 25 requests/day, 5 requests/minute
   - **Supports**: WTI, BRENT, WHEAT, CORN, COPPER, NATURAL_GAS
   - **Integration**: MCP server configured and working
   - **Usage**: Primary validation source for oil and agricultural commodities

2. **✅ Minted Metal API Integration** (precious metals validation)
   - **Status**: Fully implemented and tested
   - **Free**: No API key required, LBMA benchmark prices
   - **Supports**: GOLD (XAU), SILVER (XAG), PLATINUM, PALLADIUM, RHODIUM
   - **Update Schedule**: Twice daily at 11:00 and 16:00 UTC (Mon-Fri)
   - **License**: CC BY 4.0 (attribution required)
   - **Integration**: Primary validation source for precious metals
   - **Fallback**: MetalPrices API as secondary source

### Remaining Improvements
1. **Additional External API Integration**:
   - **Quandl** (financial data, economic indicators)
     - Free tier: 50,000 calls/day
     - Premium: $50/month for additional datasets
     - Supports: DXY, economic indicators, commodity prices
     - API endpoint: `https://www.quandl.com/api/v3/datasets/FRED/DEXUSJP.json?api_key=YOUR_KEY`
   
   - **FRED API** (Federal Reserve Economic Data)
     - Free: 120 requests/minute
     - Supports: Exchange rates, economic indicators, interest rates
     - API endpoint: `https://api.stlouisfed.org/fred/series/observations?series_id=DEXTHUS&api_key=YOUR_KEY`
   
   - **ExchangeRate-API** (current exchange rates)
     - Free: 1,500 requests/month
     - Premium: $10/month for higher limits
     - Supports: 170+ currencies
     - API endpoint: `https://api.exchangerate-api.com/v4/latest/USD`

2. **Automated Cleanup**: Add scheduled cleanup of old quality records (older than 90 days)

3. **Dashboard**: Create a web dashboard for visualizing quality trends

### Advanced Features
1. **Machine Learning**: Anomaly detection for unusual price movements
2. **Correlation Analysis**: Cross-validate related instruments
3. **Source Reliability Scoring**: Track which data sources are most reliable
4. **Auto-Recovery**: Automatic fallback to alternative data sources
5. **Predictive Quality**: Forecast potential data quality issues before they occur

## Configuration

### SSOT Configuration
Data quality settings are now integrated into `config/data_sources.yml`:

```yaml
# Data quality settings
data_quality:
  enabled: true
  tolerance_pct: 2.0
  max_freshness_days: 2
  min_completeness_pct: 90.0
  alert_threshold: 3
  run_after_import: true
  schedule: "daily"
  schedule_time: "18:00"
```

### Environment Variables
Create a `.env` file for sensitive configuration (see `.env.example`):

```bash
# Data Quality Configuration
DATA_QUALITY_ENABLED=true
QUALITY_TOLERANCE=2.0
QUALITY_FRESHNESS_DAYS=2
QUALITY_COMPLETENESS_PCT=90.0

# External API Keys for Data Quality Validation
FRED_API_KEY=your_fred_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
METAL_PRICES_API_KEY=your_metal_prices_key_here  # Optional backup for precious metals
# Minted Metal API: No API key required (free, LBMA benchmark prices)

# Alert Configuration
ALERT_EMAIL_ENABLED=false
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_USERNAME=your-email@gmail.com
ALERT_EMAIL_PASSWORD=your-app-password
ALERT_EMAIL_RECIPIENTS=admin@example.com,trader@example.com
ALERT_WEBHOOK_ENABLED=false
ALERT_WEBHOOK_URL=https://your-webhook-url.com/alerts
ALERT_THRESHOLD=3
```

### Getting API Keys

**Alpha Vantage (Free Tier) - ✅ CONFIGURED:**
1. Go to https://www.alphavantage.co/support/#api-key
2. Sign up for free account
3. 25 requests/day, 5 requests/minute
4. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`
5. **Current Status**: Configured and working for WTI, BRENT, WHEAT, CORN, COPPER, NATURAL_GAS

**Minted Metal API (Free) - ✅ CONFIGURED:**
1. No API key required
2. Free LBMA benchmark prices
3. Updates twice daily at 11:00 and 16:00 UTC
4. Attribution required: "Cite: Minted Metal (mintedmetal.com)"
5. **Current Status**: Integrated as primary source for precious metals validation

**MetalPrices API (Free Tier) - Optional Backup:**
1. Go to https://metalpriceapi.com/
2. Sign up for free account
3. 100 requests/month
4. Add to `.env`: `METAL_PRICES_API_KEY=your_key`
5. **Current Status**: Configured as fallback for precious metals

**FRED API (Free) - Optional:**
1. Go to https://fred.stlouisfed.org/docs/api/api_key.html
2. Request a free API key (no account required)
3. 120 requests/minute limit
4. Add to `.env`: `FRED_API_KEY=your_key`
5. **Current Status**: Optional for enhanced validation

## Monitoring and Maintenance

### Regular Tasks
1. **Review quality reports** weekly to identify trends
2. **Update external API credentials** as needed
3. **Clean up old quality records** monthly
4. **Adjust tolerance levels** based on market conditions

### Troubleshooting
1. **High failure rates**: Check external API connectivity
2. **Stale data alerts**: Verify automation scheduler is running
3. **Completeness issues**: Check for data import errors
4. **Accuracy problems**: Investigate data source quality

## Integration with Existing Systems

### Trade Verification Skill
The data quality system complements the existing `trade-verify` skill:
- **Trade-verify**: System health, API status, infrastructure
- **Data quality**: Data accuracy, completeness, freshness

### Automation System
Integrated with existing scheduler:
- Runs after successful imports
- Uses existing notification system
- Follows existing retry logic patterns

### CLI Integration
New `quality` command in CLI:
- Consistent with existing CLI patterns
- Supports same configuration approach
- Integrates with existing error handling

## Conclusion

This data quality monitoring system provides comprehensive protection against data accuracy issues like the USD/THB problem. By automating validation, maintaining historical records, and providing multi-channel alerting, it ensures data reliability while minimizing manual oversight requirements.

The system is designed to be:
- **Automated**: Runs without manual intervention
- **Configurable**: Adaptable to different requirements
- **Informative**: Provides detailed actionable information
- **Integrated**: Works with existing systems
- **Extensible**: Easy to add new validation rules and sources

Regular use of this system will maintain high data quality standards and prevent similar accuracy issues in the future.