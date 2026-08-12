#!/usr/bin/env python3
"""
Download and format US Dollar Index (DXY) data from FRED.
"""
import urllib.request
import csv
import os
from datetime import datetime

def download_dxy_data():
    """Download DXY data from FRED API."""
    # FRED API endpoint for CSV data (no API key needed for basic CSV download)
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS"
    output_file = 'data/archive/dxy_raw.csv'
    
    try:
        print(f"Downloading DXY data from FRED API...")
        urllib.request.urlretrieve(url, output_file)
        print(f"✅ Downloaded to {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return False

def format_dxy_data():
    """Format DXY data for our database."""
    input_file = 'data/archive/dxy_raw.csv'
    output_file = 'data/imported/dxy_formatted.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting DXY data...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'value', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Skip header row
            header = next(reader)
            print(f"Header: {header}")
            
            count = 0
            prev_value = None
            
            for row in reader:
                # Parse data rows
                if len(row) >= 2:
                    date_str = row[0].strip()
                    value_str = row[1].strip()
                    
                    # Skip empty or invalid values
                    if not date_str or not value_str or value_str == '.' or value_str == 'ND':
                        prev_value = None
                        continue
                    
                    try:
                        # Parse date (FRED format is YYYY-MM-DD)
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_formatted = date_obj.strftime('%Y-%m-%d')
                        
                        # Parse value
                        value = float(value_str)
                        
                        # Generate synthetic OHLC data
                        # Use previous close as open, or current value if no previous
                        open_price = prev_value if prev_value is not None else value
                        
                        # Generate synthetic high/low with small variation
                        variation = value * 0.001  # 0.1% variation for index
                        high_price = value + variation
                        low_price = value - variation
                        
                        # Close is the current value
                        close_price = value
                        
                        # Generate synthetic volume (indexes don't have real volume)
                        volume = 0
                        
                        writer.writerow([
                            date_formatted, 
                            f"{value:.4f}", 
                            f"{open_price:.4f}", 
                            f"{high_price:.4f}", 
                            f"{low_price:.4f}", 
                            f"{close_price:.4f}", 
                            volume
                        ])
                        
                        prev_value = value
                        count += 1
                        
                    except (ValueError, IndexError) as e:
                        print(f"Skipping invalid row: {row} - {e}")
                        continue
            
            print(f"✅ Formatted {count} records for DXY data")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting DXY data: {e}")
        return False

def main():
    """Main function to download and format DXY data."""
    print("=" * 60)
    print("DXY DATA DOWNLOADER")
    print("=" * 60)
    print()
    
    # Create data directories if they don't exist
    os.makedirs('data/archive', exist_ok=True)
    os.makedirs('data/imported', exist_ok=True)
    
    print("This script will download US Dollar Index (DXY) data from FRED.")
    print("Downloaded data will be formatted for import into your database.")
    print()
    
    # Download DXY data
    if download_dxy_data():
        format_dxy_data()
        # Keep raw file for inspection
        print("📁 Raw file saved to: data/archive/dxy_raw.csv")
    print()
    
    print("=" * 60)
    print("Download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the downloaded file in data/imported/dxy_formatted.csv")
    print("2. Import using: python cli.py import dollar_index data/imported/dxy_formatted.csv")
    print()

if __name__ == '__main__':
    main()