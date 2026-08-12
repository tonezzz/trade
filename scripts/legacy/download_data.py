#!/usr/bin/env python3
"""
Simple script to download sample historical data using only standard library.
"""
import urllib.request
import csv
import os
import json
from datetime import datetime

def download_csv(url, filename):
    """Download CSV file from URL."""
    try:
        print(f"Downloading from {url}...")
        urllib.request.urlretrieve(url, filename)
        print(f"✅ Downloaded to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return False

def format_wti_data():
    """Format WTI oil data for our database."""
    input_file = 'data/archive/wti_raw.csv'
    output_file = 'data/imported/wti_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting WTI data...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'commodity', 'symbol', 'price', 'unit', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Skip header row
            next(reader)
            
            count = 0
            for row in reader:
                if len(row) >= 2:
                    date = row[0]
                    price = row[1]
                    writer.writerow([date, 'OIL', 'WTI', price, 'barrel', '', '', '', price, ''])
                    count += 1
            
            print(f"✅ Formatted {count} records for WTI oil data")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting WTI data: {e}")
        return False

def format_brent_data():
    """Format Brent oil data for our database."""
    input_file = 'data/archive/brent_raw.csv'
    output_file = 'data/imported/brent_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting Brent data...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'commodity', 'symbol', 'price', 'unit', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Skip header row
            next(reader)
            
            count = 0
            for row in reader:
                if len(row) >= 2:
                    date = row[0]
                    price = row[1]
                    writer.writerow([date, 'OIL', 'BRENT', price, 'barrel', '', '', '', price, ''])
                    count += 1
            
            print(f"✅ Formatted {count} records for Brent oil data")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting Brent data: {e}")
        return False

def format_thb_data(input_file=None):
    """Format THB exchange rate data from open.er-api.com JSON format."""
    # Find the actual file if not provided
    if input_file is None:
        import glob
        matching_files = glob.glob('data/archive/usd/thb_exchange_rates_*.json')
        
        if not matching_files:
            print(f"❌ Input file not found: data/archive/usd/thb_exchange_rates_*.json")
            return False
        
        input_file = matching_files[0]
    
    output_file = 'data/imported/thb_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting THB data from {input_file}...")
    
    try:
        with open(input_file, 'r') as infile:
            data = json.load(infile)
        
        # The API returns data in format: {"rates": {"THB": 33.5}, "base": "USD", "date": "2026-08-10"}
        # We need to convert this to our CSV format
        
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'base_currency', 'quote_currency', 'rate', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Extract data
            rates = data.get('rates', {})
            base = data.get('base', 'USD')
            date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            # Get THB rate
            thb_rate = rates.get('THB')
            if thb_rate:
                writer.writerow([date, base, 'THB', thb_rate, '', '', '', thb_rate, ''])
                print(f"✅ Formatted THB rate: {thb_rate} for {date}")
                print(f"📁 Saved to: {output_file}")
                return True
            else:
                print(f"❌ THB rate not found in data")
                return False
            
    except Exception as e:
        print(f"❌ Error formatting THB data: {e}")
        return False

def format_dxy_data(input_file='data/archive/dxy_fred.csv'):
    """Format Dollar Index data from FRED API CSV format."""
    output_file = 'data/imported/dxy_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting DXY data from {input_file}...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'value', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Skip header row
            next(reader)
            
            count = 0
            for row in reader:
                if len(row) >= 2:
                    date = row[0]
                    value = row[1]
                    writer.writerow([date, value, '', '', '', value, ''])
                    count += 1
            
            print(f"✅ Formatted {count} records for DXY data")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting DXY data: {e}")
        return False

def format_alpha_vantage_commodity(input_file, commodity_name=None):
    """Format commodity data from Alpha Vantage JSON format."""
    output_file = 'data/imported/commodity_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting Alpha Vantage commodity data from {input_file}...")
    
    try:
        with open(input_file, 'r') as infile:
            data = json.load(infile)
        
        # Extract commodity name from data if not provided
        if not commodity_name:
            commodity_name = data.get('name', 'COMMODITY').upper().replace(' ', '_')
        
        # Extract unit from data and normalize it
        unit_raw = data.get('unit', 'unknown')
        # Normalize unit names to match validator expectations
        unit_mapping = {
            'dollar per metric ton': 'metric_ton',
            'dollars per barrel': 'barrel',
            'dollars per million BTU': 'mmbtu',
            'dollar per metric ton': 'metric_ton'
        }
        unit = unit_mapping.get(unit_raw, unit_raw)
        
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'commodity', 'symbol', 'price', 'unit', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Extract data points
            data_points = data.get('data', [])
            
            count = 0
            skipped = 0
            for point in data_points:
                date = point.get('date')
                value = point.get('value')
                
                # Skip invalid price values (represented as "." in Alpha Vantage)
                if date and value and value != '.' and value != '':
                    try:
                        # Validate that value can be converted to float
                        float_value = float(value)
                        # Use commodity name as symbol
                        symbol = commodity_name
                        writer.writerow([date, commodity_name, symbol, value, unit, '', '', '', value, ''])
                        count += 1
                    except (ValueError, TypeError):
                        skipped += 1
                else:
                    skipped += 1
            
            print(f"✅ Formatted {count} records for {commodity_name} (skipped {skipped} invalid records)")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting Alpha Vantage commodity data: {e}")
        return False

def main():
    """Main function to download sample data."""
    print("=" * 60)
    print("HISTORICAL DATA DOWNLOADER")
    print("=" * 60)
    print()
    
    # Create data directories if they don't exist
    os.makedirs('data/archive', exist_ok=True)
    os.makedirs('data/imported', exist_ok=True)
    
    print("This script will download sample historical data from free sources.")
    print("Downloaded data will be formatted for import into your database.")
    print()
    
    # Download WTI data
    wti_url = "https://raw.githubusercontent.com/datasets/oil-prices/main/data/wti-daily.csv"
    if download_csv(wti_url, 'data/archive/wti_raw.csv'):
        format_wti_data()
        # Clean up raw file after formatting
        if os.path.exists('data/archive/wti_raw.csv'):
            os.remove('data/archive/wti_raw.csv')
            print("🗑️ Cleaned up raw WTI data file")
    print()
    
    # Download Brent data
    brent_url = "https://raw.githubusercontent.com/datasets/oil-prices/main/data/brent-daily.csv"
    if download_csv(brent_url, 'data/archive/brent_raw.csv'):
        format_brent_data()
        # Clean up raw file after formatting
        if os.path.exists('data/archive/brent_raw.csv'):
            os.remove('data/archive/brent_raw.csv')
            print("🗑️ Cleaned up raw Brent data file")
    print()
    
    print("=" * 60)
    print("Download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the downloaded files in data/imported/")
    print("2. Import using: python cli.py import commodity_prices data/imported/wti_formatted.csv")
    print("3. Or import using: python cli.py import commodity_prices data/imported/brent_formatted.csv")
    print()
    print("For more data sources and manual download instructions, see docs/DATA_SOURCES.md")

if __name__ == '__main__':
    main()
