#!/usr/bin/env python3
"""
Download data from sources defined in SSOT (config/data_sources.yml).
This script reads the configuration and downloads data for enabled sources.
"""
import yaml
import urllib.request
import csv
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SSOTDataDownloader:
    """Download data from sources defined in SSOT configuration."""
    
    def __init__(self, config_path: str = "config/data_sources.yml"):
        """Initialize downloader with SSOT configuration."""
        self.config_path = config_path
        self.config = self.load_config()
        self.settings = self.config.get('settings', {})
        self.data_sources = self.config.get('data_sources', {})
        
    def load_config(self) -> Dict:
        """Load SSOT configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def download_csv(self, url: str, filename: str) -> bool:
        """Download CSV file from URL."""
        try:
            logger.info(f"Downloading from {url}...")
            urllib.request.urlretrieve(url, filename)
            logger.info(f"✅ Downloaded to {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Error downloading: {e}")
            return False
    
    def format_currency_data(self, source_config: Dict, input_file: str, output_file: str) -> bool:
        """Format currency data for database import."""
        if not os.path.exists(input_file):
            logger.warning(f"Input file not found: {input_file}")
            return False
        
        quote_currency = source_config.get('quote_currency', source_config.get('symbol', 'USD'))
        logger.info(f"Formatting {quote_currency} data...")
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                
                # Write header
                writer.writerow(['date', 'base_currency', 'quote_currency', 'rate', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
                
                # Skip header row if it exists
                first_row = next(reader)
                if 'date' not in str(first_row[0]).lower():
                    # First row is data, not header
                    self._write_currency_row(writer, first_row, quote_currency)
                
                count = 1 if 'date' not in str(first_row[0]).lower() else 0
                
                for row in reader:
                    if len(row) >= 2:
                        self._write_currency_row(writer, row, quote_currency)
                        count += 1
                
                logger.info(f"✅ Formatted {count} records for {quote_currency}")
                logger.info(f"📁 Saved to: {output_file}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error formatting {quote_currency} data: {e}")
            return False
    
    def _write_currency_row(self, writer, row: List, quote_currency: str):
        """Write a single currency data row."""
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
        
        writer.writerow([date, 'USD', quote_currency, usd_rate, '', '', '', usd_rate, ''])
    
    def format_commodity_data(self, source_config: Dict, input_file: str, output_file: str) -> bool:
        """Format commodity data for database import."""
        if not os.path.exists(input_file):
            logger.warning(f"Input file not found: {input_file}")
            return False
        
        commodity = source_config.get('commodity', source_config.get('symbol', 'UNKNOWN'))
        symbol = source_config.get('symbol', commodity)
        unit = source_config.get('unit', 'unit')
        
        logger.info(f"Formatting {commodity} ({symbol}) data...")
        
        try:
            with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                
                # Write header
                writer.writerow(['date', 'commodity', 'symbol', 'price', 'unit', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
                
                # Skip header row if it exists
                first_row = next(reader)
                if 'date' not in str(first_row[0]).lower():
                    # First row is data, not header
                    self._write_commodity_row(writer, first_row, commodity, symbol, unit)
                
                count = 1 if 'date' not in str(first_row[0]).lower() else 0
                
                for row in reader:
                    if len(row) >= 2:
                        self._write_commodity_row(writer, row, commodity, symbol, unit)
                        count += 1
                
                logger.info(f"✅ Formatted {count} records for {commodity}")
                logger.info(f"📁 Saved to: {output_file}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error formatting {commodity} data: {e}")
            return False
    
    def _write_commodity_row(self, writer, row: List, commodity: str, symbol: str, unit: str):
        """Write a single commodity data row."""
        date = row[0]
        price = row[1]
        writer.writerow([date, commodity, symbol, price, unit, '', '', '', price, ''])
    
    def process_source(self, source_name: str, source_config: Dict) -> bool:
        """Process a single data source."""
        if not source_config.get('enabled', False):
            logger.info(f"Skipping disabled source: {source_name}")
            return True
        
        logger.info(f"Processing source: {source_name}")
        
        # Create directories
        download_dir = self.settings.get('download_dir', 'data/archive')
        import_dir = self.settings.get('import_dir', 'data/imported')
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(import_dir, exist_ok=True)
        
        # Download file
        url = source_config.get('url')
        if not url:
            logger.error(f"No URL specified for {source_name}")
            return False
        
        # Generate filename
        symbol = source_config.get('symbol', source_name)
        raw_filename = os.path.join(download_dir, f"{symbol.lower()}_raw.csv")
        formatted_filename = os.path.join(import_dir, f"{symbol.lower()}_formatted.csv")
        
        # Download
        if not self.download_csv(url, raw_filename):
            return False
        
        # Format based on type
        data_type = source_config.get('type')
        if data_type == 'exchange_rate':
            success = self.format_currency_data(source_config, raw_filename, formatted_filename)
        elif data_type == 'commodity':
            success = self.format_commodity_data(source_config, raw_filename, formatted_filename)
        else:
            logger.warning(f"Unknown data type: {data_type}, skipping formatting")
            success = True
        
        # Clean up raw file if formatting was successful
        if success and os.path.exists(raw_filename):
            os.remove(raw_filename)
            logger.info(f"🗑️ Cleaned up raw file: {raw_filename}")
        
        return success
    
    def process_all_sources(self, source_type: Optional[str] = None) -> Dict[str, bool]:
        """Process all enabled data sources, optionally filtered by type."""
        results = {}
        
        for source_name, source_config in self.data_sources.items():
            # Filter by type if specified
            if source_type and source_config.get('type') != source_type:
                continue
            
            success = self.process_source(source_name, source_config)
            results[source_name] = success
        
        return results
    
    def process_currencies(self) -> Dict[str, bool]:
        """Process all currency exchange rate sources."""
        return self.process_all_sources('exchange_rate')
    
    def process_commodities(self) -> Dict[str, bool]:
        """Process all commodity sources."""
        return self.process_all_sources('commodity')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download data from SSOT configuration')
    parser.add_argument('--config', default='config/data_sources.yml', help='Path to SSOT config file')
    parser.add_argument('--type', choices=['all', 'currencies', 'commodities'], 
                       default='all', help='Type of data sources to process')
    parser.add_argument('--source', help='Process specific source by name')
    
    args = parser.parse_args()
    
    downloader = SSOTDataDownloader(args.config)
    
    if args.source:
        # Process specific source
        source_config = downloader.data_sources.get(args.source)
        if not source_config:
            logger.error(f"Source not found: {args.source}")
            sys.exit(1)
        success = downloader.process_source(args.source, source_config)
        sys.exit(0 if success else 1)
    
    # Process by type
    if args.type == 'currencies':
        results = downloader.process_currencies()
    elif args.type == 'commodities':
        results = downloader.process_commodities()
    else:
        results = downloader.process_all_sources()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 60)
    
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    for source, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"{status} {source}")
    
    logger.info(f"\nTotal: {successful}/{total} successful")
    
    sys.exit(0 if successful == total else 1)


if __name__ == '__main__':
    main()