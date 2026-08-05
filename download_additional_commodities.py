#!/usr/bin/env python3
"""
Download additional commodity historical data (Silver, Copper, Natural Gas, Agricultural).
Uses free data sources and sample data generation for demonstration.

NOTE: This script generates sample data for demonstration purposes.
For production use, use download_from_ssot.py which reads from config/data_sources.yml
and downloads real data from configured sources.
"""
import csv
import os
from datetime import datetime, timedelta

def generate_sample_commodity_data(commodity_name, symbol, unit, output_file, years=10):
    """Generate sample historical data for a commodity."""
    print(f"Generating sample data for {commodity_name} ({symbol})...")
    
    try:
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Write header
            writer.writerow(['date', 'commodity', 'symbol', 'price', 'unit', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            
            # Base prices for different commodities (approximate USD prices)
            base_prices = {
                'SILVER': 25.0,      # per oz
                'COPPER': 4.0,      # per lb
                'NATURAL_GAS': 3.0, # per MMBtu
                'WHEAT': 6.0,       # per bushel
                'CORN': 5.0,        # per bushel
                'SOY': 13.0         # per bushel
            }
            
            base_price = base_prices.get(symbol, 10.0)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            current_date = start_date
            count = 0
            
            while current_date <= end_date:
                # Add some random variation to simulate market movement
                import random
                variation = random.uniform(-0.03, 0.03)  # +/- 3% daily variation
                price = base_price * (1 + variation)
                
                # Simulate OHLC
                open_price = price * random.uniform(0.99, 1.01)
                high_price = max(open_price, price) * random.uniform(1.0, 1.025)
                low_price = min(open_price, price) * random.uniform(0.975, 1.0)
                close_price = price
                
                writer.writerow([
                    current_date.strftime('%Y-%m-%d'),
                    commodity_name,
                    symbol,
                    price,
                    unit,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    ''
                ])
                
                current_date += timedelta(days=1)
                count += 1
            
            print(f"✅ Generated {count} sample records for {commodity_name}")
            print(f"📁 Saved to: {output_file}")
            return True
            
    except Exception as e:
        print(f"❌ Error generating sample data for {commodity_name}: {e}")
        return False

def main():
    """Main function to download additional commodity data."""
    print("=" * 60)
    print("ADDITIONAL COMMODITY DATA DOWNLOADER")
    print("=" * 60)
    print()
    
    # Create data directories if they don't exist
    os.makedirs('data/archive', exist_ok=True)
    os.makedirs('data/imported', exist_ok=True)
    
    print("This script will download historical data for additional commodities:")
    print("- Silver (XAG)")
    print("- Copper")
    print("- Natural Gas")
    print("- Agricultural commodities (Wheat, Corn, Soy)")
    print()
    print("Note: Using sample data generation for demonstration purposes.")
    print("For production use, replace with real data sources.")
    print()
    
    commodities = [
        ('Silver', 'XAG', 'oz'),
        ('Copper', 'COPPER', 'lb'),
        ('Natural Gas', 'NATURAL_GAS', 'MMBtu'),
        ('Wheat', 'WHEAT', 'bushel'),
        ('Corn', 'CORN', 'bushel'),
        ('Soy', 'SOY', 'bushel')
    ]
    
    for commodity_name, symbol, unit in commodities:
        output_file = f'data/imported/{symbol.lower()}_formatted.csv'
        
        # Generate sample data (replace with real downloads in production)
        if generate_sample_commodity_data(commodity_name, symbol, unit, output_file, years=10):
            print()
    
    print("=" * 60)
    print("Download complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    for commodity_name, symbol, unit in commodities:
        print(f"1. Import {commodity_name}: python cli.py import commodity_prices data/imported/{symbol.lower()}_formatted.csv")
    print()
    print("2. Query data: python cli.py query commodity_prices --commodity Silver")
    print("3. List available commodities: python cli.py list commodities")
    print()

if __name__ == '__main__':
    main()