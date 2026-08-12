#!/usr/bin/env python3
"""
Download additional currency pair historical data (JPY, CAD, CHF, AUD, NZD).
Uses free data sources like Federal Reserve and other financial data providers.

NOTE: This script generates sample data for demonstration purposes.
For production use, use download_from_ssot.py which reads from config/data_sources.yml
and downloads real data from configured sources.
"""
import urllib.request
import csv
import os
from datetime import datetime, timedelta

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

def format_currency_data(currency_code, input_file, output_file):
    """Format currency data for our database."""
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Formatting {currency_code} data...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'base_currency', 'quote_currency', 'rate', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Skip header row if it exists
            first_row = next(reader)
            if 'date' not in first_row[0].lower():
                # First row is data, not header
                writer.writerow([first_row[0], 'USD', currency_code, first_row[1], '', '', '', first_row[1], ''])
            
            count = 1 if 'date' not in first_row[0].lower() else 0
            
            for row in reader:
                if len(row) >= 2:
                    date = row[0]
                    rate = row[1]
                    # Convert to USD quote (most data is USD/base, we need base/USD)
                    try:
                        rate_float = float(rate)
                        if rate_float > 0:
                            usd_rate = 1.0 / rate_float  # Convert to USD/base
                        else:
                            usd_rate = rate
                    except:
                        usd_rate = rate
                    
                    writer.writerow([date, 'USD', currency_code, usd_rate, '', '', '', usd_rate, ''])
                    count += 1
            
            print(f"✅ Formatted {count} records for {currency_code}")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error formatting {currency_code} data: {e}")
        return False

def generate_sample_data(currency_code, output_file, years=10):
    """Generate sample historical data for a currency pair."""
    print(f"Generating sample data for {currency_code}...")
    
    try:
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'base_currency', 'quote_currency', 'rate', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Base rates for different currencies (approximate USD/base)
            base_rates = {
                'JPY': 110.0,
                'CAD': 1.25,
                'CHF': 0.90,
                'AUD': 1.35,
                'NZD': 1.45
            }
            
            base_rate = base_rates.get(currency_code, 1.0)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            current_date = start_date
            count = 0
            
            while current_date <= end_date:
                # Add some random variation to simulate market movement
                import random
                variation = random.uniform(-0.02, 0.02)  # +/- 2% daily variation
                rate = base_rate * (1 + variation)
                
                # Simulate OHLC
                open_price = rate * random.uniform(0.99, 1.01)
                high_price = max(open_price, rate) * random.uniform(1.0, 1.02)
                low_price = min(open_price, rate) * random.uniform(0.98, 1.0)
                close_price = rate
                
                writer.writerow([
                    current_date.strftime('%Y-%m-%d'),
                    'USD',
                    currency_code,
                    rate,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    ''
                ])
                
                current_date += timedelta(days=1)
                count += 1
            
            print(f"✅ Generated {count} sample records for {currency_code}")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error generating sample data for {currency_code}: {e}")
        return False

def main():
    """Main function to download additional currency data."""
    print("=" * 60)
    print("ADDITIONAL CURRENCY DATA DOWNLOADER")
    print("=" * 60)
    print()
    
    # Create data directories if they don't exist
    os.makedirs('data/archive', exist_ok=True)
    os.makedirs('data/imported', exist_ok=True)
    
    print("This script will download historical data for additional currency pairs:")
    print("- JPY (Japanese Yen)")
    print("- CAD (Canadian Dollar)")
    print("- CHF (Swiss Franc)")
    print("- AUD (Australian Dollar)")
    print("- NZD (New Zealand Dollar)")
    print()
    print("Note: Using sample data generation for demonstration purposes.")
    print("For production use, replace with real data sources.")
    print()
    
    currencies = ['JPY', 'CAD', 'CHF', 'AUD', 'NZD']
    
    for currency in currencies:
        output_file = f'data/imported/{currency.lower()}_formatted.csv'
        
        # Generate sample data (replace with real downloads in production)
        if generate_sample_data(currency, output_file, years=10):
            print()
    
    print("=" * 60)
    print("Download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    for currency in currencies:
        print(f"1. Import {currency}: python cli.py import exchange_rates data/imported/{currency.lower()}_formatted.csv")
    print()
    print("2. Query data: python cli.py query exchange_rates --currency JPY")
    print("3. List available currencies: python cli.py list currencies")
    print()

if __name__ == '__main__':
    main()