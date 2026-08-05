#!/usr/bin/env python3
"""
Simple script to download sample historical data using only standard library.
"""
import urllib.request
import csv
import os

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
