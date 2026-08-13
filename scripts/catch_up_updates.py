#!/usr/bin/env python3
"""
Catch-up script for missed data updates.
Runs when machine comes back online to fill data gaps.
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler import JobScheduler, JobStatus
from src.database import get_db
from src.models import ExchangeRate, DollarIndex, CommodityPrice


def check_thb_gap():
    """Check THB data freshness."""
    try:
        db = next(get_db())
        latest = db.query(ExchangeRate).filter(
            ExchangeRate.quote_currency == 'THB'
        ).order_by(ExchangeRate.date.desc()).first()
        
        if not latest:
            return {'status': 'missing', 'days': 999, 'latest': None}
        
        gap = (datetime.now().date() - latest.date).days
        return {'status': 'stale' if gap > 2 else 'fresh', 'days': gap, 'latest': latest.date}
    except Exception as e:
        print(f"Error checking THB gap: {e}")
        return {'status': 'error', 'days': 999, 'latest': None}


def check_dxy_gap():
    """Check DXY data freshness."""
    try:
        db = next(get_db())
        latest = db.query(DollarIndex).order_by(DollarIndex.date.desc()).first()
        
        if not latest:
            return {'status': 'missing', 'days': 999, 'latest': None}
        
        gap = (datetime.now().date() - latest.date).days
        return {'status': 'stale' if gap > 30 else 'fresh', 'days': gap, 'latest': latest.date}
    except Exception as e:
        print(f"Error checking DXY gap: {e}")
        return {'status': 'error', 'days': 999, 'latest': None}


def check_commodity_gaps():
    """Check commodity data freshness."""
    try:
        db = next(get_db())
        latest = db.query(CommodityPrice).order_by(CommodityPrice.date.desc()).first()
        
        if not latest:
            return {'status': 'missing', 'days': 999, 'latest': None}
        
        gap = (datetime.now().date() - latest.date).days
        return {'status': 'stale' if gap > 90 else 'fresh', 'days': gap, 'latest': latest.date}
    except Exception as e:
        print(f"Error checking commodity gaps: {e}")
        return {'status': 'error', 'days': 999, 'latest': None}


def check_currency_gaps():
    """Check currency data freshness (excluding THB)."""
    try:
        db = next(get_db())
        # Check EUR as representative of other currencies
        latest = db.query(ExchangeRate).filter(
            ExchangeRate.quote_currency == 'EUR'
        ).order_by(ExchangeRate.date.desc()).first()
        
        if not latest:
            return {'status': 'missing', 'days': 999, 'latest': None}
        
        gap = (datetime.now().date() - latest.date).days
        return {'status': 'stale' if gap > 7 else 'fresh', 'days': gap, 'latest': latest.date}
    except Exception as e:
        print(f"Error checking currency gaps: {e}")
        return {'status': 'error', 'days': 999, 'latest': None}


def check_data_gaps():
    """Check for data gaps in each data source."""
    print("Checking data gaps...")
    gaps = {
        'thb': check_thb_gap(),
        'dxy': check_dxy_gap(),
        'commodities': check_commodity_gaps(),
        'currencies': check_currency_gaps()
    }
    return gaps


def catch_up_data(gaps):
    """Run catch-up updates for stale data using scheduler's built-in catch-up method."""
    print("\nStarting catch-up updates...")
    scheduler = JobScheduler()
    
    # Use the scheduler's built-in catch-up method
    results = scheduler.run_catch_up_updates()
    
    # Display results
    for job_id, result in results.items():
        if result.status == JobStatus.SUCCESS:
            print(f"✅ {job_id}: {result.records_processed} records processed")
        else:
            print(f"❌ {job_id}: {result.error_message}")
    
    # Show summary
    successful = sum(1 for r in results.values() if r.status == JobStatus.SUCCESS)
    failed = len(results) - successful
    print(f"\nCatch-up summary: {successful} successful, {failed} failed")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Trade System Catch-Up Updates")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check data gaps
    gaps = check_data_gaps()
    
    print("\nData Freshness Status:")
    print("-" * 60)
    for source, gap in gaps.items():
        status_symbol = "✅" if gap['status'] == 'fresh' else "⚠️"
        latest_str = gap['latest'].strftime('%Y-%m-%d') if gap['latest'] else 'N/A'
        print(f"{status_symbol} {source:15s}: {gap['status']:8s} ({gap['days']:3d} days) - Latest: {latest_str}")
    
    # Run catch-up updates
    catch_up_data(gaps)
    
    print("\n" + "=" * 60)
    print("Catch-up updates completed")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verify final state
    print("\nFinal Data Quality Check:")
    print("-" * 60)
    final_gaps = check_data_gaps()
    for source, gap in final_gaps.items():
        status_symbol = "✅" if gap['status'] == 'fresh' else "⚠️"
        latest_str = gap['latest'].strftime('%Y-%m-%d') if gap['latest'] else 'N/A'
        print(f"{status_symbol} {source:15s}: {gap['status']:8s} ({gap['days']:3d} days) - Latest: {latest_str}")


if __name__ == '__main__':
    main()
