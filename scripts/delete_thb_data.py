#!/usr/bin/env python3
"""
Delete existing THB data from the database to allow fresh import.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import db
from src.models import ExchangeRate

def delete_thb_data():
    """Delete all THB exchange rate data."""
    print("Deleting existing THB data from database...")
    
    session = db.get_session()
    try:
        # Count existing THB records
        count = session.query(ExchangeRate).filter(ExchangeRate.quote_currency == 'THB').count()
        print(f"Found {count} existing THB records")
        
        # Delete all THB records
        session.query(ExchangeRate).filter(ExchangeRate.quote_currency == 'THB').delete()
        session.commit()
        
        print(f"✅ Successfully deleted {count} THB records")
        return True
    except Exception as e:
        session.rollback()
        print(f"❌ Error deleting THB data: {e}")
        return False
    finally:
        session.close()

if __name__ == '__main__':
    delete_thb_data()