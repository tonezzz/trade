#!/usr/bin/env python3
"""
Data freshness monitoring and alerting.
Checks data freshness and sends alerts when data becomes too stale.
"""
import sys
import os
import urllib.request
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import JobScheduler


def check_freshness() -> List[str]:
    """Check data freshness from API."""
    try:
        with urllib.request.urlopen('http://localhost:9000/api/data_quality', timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return [f"Error fetching data quality: {e}"]
    
    alerts = []
    current_date = datetime.now()
    
    # Load tolerance settings
    scheduler = JobScheduler()
    tolerance = scheduler.tolerance_days
    
    # Check THB freshness
    try:
        thb_latest_str = data['tables']['exchange_rates']['date_range']['latest']
        thb_latest = datetime.strptime(thb_latest_str, '%Y-%m-%d')
        thb_days = (current_date - thb_latest).days
        if thb_days > tolerance.get('thb', 2):
            alerts.append(f"THB data is {thb_days} days old (threshold: {tolerance.get('thb', 2)} days)")
    except (KeyError, ValueError) as e:
        alerts.append(f"Error checking THB freshness: {e}")
    
    # Check DXY freshness
    try:
        dxy_latest_str = data['tables']['dollar_index']['date_range']['latest']
        dxy_latest = datetime.strptime(dxy_latest_str, '%Y-%m-%d')
        dxy_days = (current_date - dxy_latest).days
        if dxy_days > tolerance.get('dxy', 30):
            alerts.append(f"DXY data is {dxy_days} days old (threshold: {tolerance.get('dxy', 30)} days)")
    except (KeyError, ValueError) as e:
        alerts.append(f"Error checking DXY freshness: {e}")
    
    # Check commodity freshness
    try:
        commodity_latest_str = data['tables']['commodity_prices']['date_range']['latest']
        commodity_latest = datetime.strptime(commodity_latest_str, '%Y-%m-%d')
        commodity_days = (current_date - commodity_latest).days
        if commodity_days > tolerance.get('commodities', 90):
            alerts.append(f"Commodity data is {commodity_days} days old (threshold: {tolerance.get('commodities', 90)} days)")
    except (KeyError, ValueError) as e:
        alerts.append(f"Error checking commodity freshness: {e}")
    
    # Check currency freshness (using EUR as representative)
    try:
        currencies = data['tables']['exchange_rates']['currencies']
        if 'EUR' in currencies:
            # Need to get latest EUR date specifically
            # For now, use the overall exchange rate latest date
            exchange_latest_str = data['tables']['exchange_rates']['date_range']['latest']
            exchange_latest = datetime.strptime(exchange_latest_str, '%Y-%m-%d')
            exchange_days = (current_date - exchange_latest).days
            if exchange_days > tolerance.get('currencies', 7):
                alerts.append(f"Currency data is {exchange_days} days old (threshold: {tolerance.get('currencies', 7)} days)")
    except (KeyError, ValueError) as e:
        alerts.append(f"Error checking currency freshness: {e}")
    
    return alerts


def check_data_quality_issues() -> List[str]:
    """Check for data quality issues."""
    try:
        with urllib.request.urlopen('http://localhost:9000/api/data_quality', timeout=10) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return [f"Error fetching data quality: {e}"]
    
    alerts = []
    
    # Check overall health
    overall_health = data['summary'].get('overall_health', 'unknown')
    if overall_health != 'healthy':
        alerts.append(f"Overall system health: {overall_health}")
    
    # Check for data quality issues
    tables = data.get('tables', {})
    for table_name, table_data in tables.items():
        issues = table_data.get('issues', [])
        if issues:
            for issue in issues:
                alerts.append(f"{table_name}: {issue}")
    
    return alerts


def send_alert(alerts: List[str]):
    """Send alerts (placeholder for future notification integration)."""
    if not alerts:
        print("✅ No alerts - all data is fresh and healthy")
        return
    
    print(f"⚠️  {len(alerts)} alert(s) generated:")
    for alert in alerts:
        print(f"  - {alert}")
    
    # TODO: Integrate with notification system
    # For now, just print to console
    print("\nAlert notification would be sent here (email, Slack, etc.)")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Data Freshness Monitor")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check data freshness
    print("\nChecking data freshness...")
    freshness_alerts = check_freshness()
    
    # Check data quality issues
    print("Checking data quality issues...")
    quality_alerts = check_data_quality_issues()
    
    # Combine alerts
    all_alerts = freshness_alerts + quality_alerts
    
    # Send alerts
    print("\nAlert Summary:")
    print("-" * 60)
    send_alert(all_alerts)
    
    print("\n" + "=" * 60)
    print("Monitoring completed")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Return exit code based on alerts
    if all_alerts:
        return 1  # Exit with error if there are alerts
    return 0


if __name__ == '__main__':
    sys.exit(main())