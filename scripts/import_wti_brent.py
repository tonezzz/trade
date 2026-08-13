#!/usr/bin/env python3
"""
Quick import script for WTI and Brent commodity data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import db
from src.models import CommodityPrice
import csv
from datetime import datetime

def import_commodity_data(csv_file):
    """Import commodity data from CSV file."""
    session = db.get_session()
    count = 0
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = CommodityPrice(
                    date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                    commodity=row['commodity'],
                    symbol=row['symbol'],
                    price=float(row['price']),
                    unit=row['unit']
                )
                session.add(record)
                count += 1
        
        session.commit()
        print(f'✅ Imported {count} records from {csv_file}')
        return count
    except Exception as e:
        session.rollback()
        print(f'❌ Error importing {csv_file}: {e}')
        return 0
    finally:
        session.close()

if __name__ == '__main__':
    print("Importing WTI and Brent data...")
    
    wti_count = import_commodity_data('/app/data/imported/wti_formatted.csv')
    brent_count = import_commodity_data('/app/data/imported/brent_formatted.csv')
    
    total = wti_count + brent_count
    print(f'\n📊 Total imported: {total} records')
