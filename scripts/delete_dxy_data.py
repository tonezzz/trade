#!/usr/bin/env python3
"""
Delete existing DXY data from the database to allow fresh import.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import db
from src.models import DollarIndex

def delete_dxy_data():
    """Delete all DXY data."""
    print("Deleting existing DXY data from database...")
    
    session = db.get_session()
    try:
        # Count existing DXY records
        count = session.query(DollarIndex).count()
        print(f"Found {count} existing DXY records")
        
        # Delete all DXY records
        session.query(DollarIndex).delete()
        session.commit()
        
        print(f"✅ Successfully deleted {count} DXY records")
        return True
    except Exception as e:
        session.rollback()
        print(f"❌ Error deleting DXY data: {e}")
        return False
    finally:
        session.close()

if __name__ == '__main__':
    delete_dxy_data()