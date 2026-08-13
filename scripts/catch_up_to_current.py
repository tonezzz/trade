#!/usr/bin/env python3
"""
Enhanced catch-up script that fills data gaps to current time.
This script temporarily sets tolerance to 0 and forces updates for all data sources.
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import JobScheduler, JobStatus
from src.database import get_db
from src.models import ExchangeRate, DollarIndex, CommodityPrice


def catch_up_to_current():
    """Catch up all data sources to current date by temporarily bypassing tolerance."""
    print("=" * 60)
    print("Enhanced Catch-Up to Current Time")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    scheduler = JobScheduler()
    
    # Temporarily set all tolerances to 0 to force updates
    original_tolerances = scheduler.tolerance_days.copy()
    scheduler.tolerance_days = {
        'thb': 0,
        'dxy': 0,
        'commodities': 0,
        'currencies': 0
    }
    
    print("\n🔄 Forcing catch-up updates (tolerance temporarily set to 0)...")
    
    # Run catch-up with zero tolerance
    results = scheduler.run_catch_up_updates()
    
    # Restore original tolerances
    scheduler.tolerance_days = original_tolerances
    
    # Display results
    total_records = 0
    for job_id, result in results.items():
        if result.status == JobStatus.SUCCESS:
            print(f"✅ {job_id}: {result.records_processed} records processed")
            total_records += result.records_processed
        else:
            print(f"❌ {job_id}: {result.error_message}")
    
    print("\n" + "=" * 60)
    print(f"Enhanced catch-up completed: {total_records} total records processed")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verify final state
    print("\nFinal Data Freshness Check:")
    print("-" * 60)
    
    current_date = datetime.now().date()
    
    # Check THB
    db = next(get_db())
    thb_latest = db.query(ExchangeRate).filter(
        ExchangeRate.quote_currency == 'THB'
    ).order_by(ExchangeRate.date.desc()).first()
    if thb_latest:
        days_old = (current_date - thb_latest.date).days
        print(f"THB: {thb_latest.date} ({days_old} days old)")
    
    # Check EUR (representative of other currencies)
    eur_latest = db.query(ExchangeRate).filter(
        ExchangeRate.quote_currency == 'EUR'
    ).order_by(ExchangeRate.date.desc()).first()
    if eur_latest:
        days_old = (current_date - eur_latest.date).days
        print(f"EUR: {eur_latest.date} ({days_old} days old)")
    
    # Check DXY
    dxy_latest = db.query(DollarIndex).order_by(DollarIndex.date.desc()).first()
    if dxy_latest:
        days_old = (current_date - dxy_latest.date).days
        print(f"DXY: {dxy_latest.date} ({days_old} days old)")
    
    # Check commodities
    commodity_latest = db.query(CommodityPrice).order_by(CommodityPrice.date.desc()).first()
    if commodity_latest:
        days_old = (current_date - commodity_latest.date).days
        print(f"Commodities: {commodity_latest.date} ({days_old} days old)")
    
    db.close()
    
    return total_records


if __name__ == '__main__':
    catch_up_to_current()