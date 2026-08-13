#!/usr/bin/env python3
"""
Check commodity data in database.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import db
from sqlalchemy import text

def check_commodity_data():
    """Check commodity data in database."""
    session = db.get_session()
    
    try:
        # Check WTI count
        result = session.execute(text('SELECT COUNT(*) FROM commodity_prices WHERE symbol="WTI"'))
        wti_count = result.scalar()
        print(f'WTI count: {wti_count}')
        
        # Check BRENT count
        result = session.execute(text('SELECT COUNT(*) FROM commodity_prices WHERE symbol="BRENT"'))
        brent_count = result.scalar()
        print(f'BRENT count: {brent_count}')
        
        # Check recent WTI data
        result = session.execute(text('SELECT date, price FROM commodity_prices WHERE symbol="WTI" ORDER BY date DESC LIMIT 5'))
        print('Recent WTI data:')
        for row in result:
            print(f'  {row[0]}: {row[1]}')
            
        # Check recent BRENT data
        result = session.execute(text('SELECT date, price FROM commodity_prices WHERE symbol="BRENT" ORDER BY date DESC LIMIT 5'))
        print('Recent BRENT data:')
        for row in result:
            print(f'  {row[0]}: {row[1]}')
            
    finally:
        session.close()

if __name__ == '__main__':
    check_commodity_data()
