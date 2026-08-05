#!/usr/bin/env python3
"""
Download and format USD/THB exchange rate data from FRED.
"""
import urllib.request
import csv
import os
from datetime import datetime

def download_thb_data():
    """Download USD/THB data from FRED API."""
    # FRED API endpoint for CSV data (using DEXTHUS for daily data instead of EXTHUS monthly)
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXTHUS"
    output_file = 'data/archive/thb_raw.csv'
    
    try:
        print(f"Downloading USD/THB data from FRED API...")
        urllib.request.urlretrieve(url, output_file)
        print(f"✅ Downloaded to {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return False

def format_thb_data():
    """Format USD/THB data for our database."""
    input_file = 'data/archive/thb_raw.csv'
    output_file = 'data/imported/thb_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting USD/THB data...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'base_currency', 'quote_currency', 'rate', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Skip header row
            header = next(reader)
            print(f"Header: {header}")
            
            count = 0
            prev_rate = None
            
            for row in reader:
                # Parse data rows
                if len(row) >= 2:
                    date_str = row[0].strip()
                    rate_str = row[1].strip()
                    
                    # Skip empty or invalid values
                    if not date_str or not rate_str or rate_str == '.' or rate_str == 'ND':
                        prev_rate = None
                        continue
                    
                    try:
                        # Parse date (FRED format is YYYY-MM-DD)
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_formatted = date_obj.strftime('%Y-%m-%d')
                        
                        # Parse rate
                        rate = float(rate_str)
                        
                        # Generate synthetic OHLC data
                        # Use previous close as open, or current rate if no previous
                        open_price = prev_rate if prev_rate is not None else rate
                        
                        # Generate synthetic high/low with small variation
                        variation = rate * 0.002  # 0.2% variation
                        high_price = rate + variation
                        low_price = rate - variation
                        
                        # Close is the current rate
                        close_price = rate
                        
                        # Generate synthetic volume
                        volume = 1000000 + (hash(date_str) % 500000)
                        
                        writer.writerow([
                            date_formatted, 
                            'USD',
                            'THB', 
                            f"{rate:.4f}", 
                            f"{open_price:.4f}", 
                            f"{high_price:.4f}", 
                            f"{low_price:.4f}", 
                            f"{close_price:.4f}", 
                            volume
                        ])
                        
                        prev_rate = rate
                        count += 1
                        
                    except (ValueError, IndexError) as e:
                        print(f"Skipping invalid row: {row} - {e}")
                        continue
            
            print(f"✅ Formatted {count} records for USD/THB data")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting USD/THB data: {e}")
        return False

def main():
    """Main function to download and format USD/THB data."""
    print("=" * 60)
    print("USD/THB DATA DOWNLOADER")
    print("=" * 60)
    print()
    
    # Create data directories if they don't exist
    os.makedirs('data/archive', exist_ok=True)
    os.makedirs('data/imported', exist_ok=True)
    
    print("This script will download USD/THB exchange rate data from FRED.")
    print("Downloaded data will be formatted for import into your database.")
    print()
    
    # Download THB data
    if download_thb_data():
        format_thb_data()
        # Keep raw file for inspection
        print("📁 Raw file saved to: data/archive/thb_raw.csv")
    print()
    
    print("=" * 60)
    print("Download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the downloaded file in data/imported/thb_formatted.csv")
    print("2. Import using: python cli.py import exchange_rates data/imported/thb_formatted.csv")
    print()

if __name__ == '__main__':
    main()
