#!/usr/bin/env python3
"""
Unified data downloader using the modular data source system.
Replaces multiple individual download scripts with a single, unified interface.
"""
import argparse
import sys
from pathlib import Path
from datetime import date, datetime
import logging
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv(project_root / '.env')

from src.data_sources.downloader import UnifiedDataDownloader
from src.data_sources.base_source import DataSourceConfig, DataSourceType


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def download_single_source(
    downloader: UnifiedDataDownloader,
    source_id: str,
    symbol: str,
    start_date: str = None,
    end_date: str = None,
    output_file: str = None
):
    """
    Download data from a single source.
    
    Args:
        downloader: UnifiedDataDownloader instance
        source_id: ID of the data source
        symbol: Symbol to fetch
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_file: Output file path
    """
    print(f"\n{'='*60}")
    print(f"Downloading from source: {source_id}")
    print(f"Symbol: {symbol}")
    print(f"{'='*60}\n")
    
    # Parse dates
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    
    # Download data
    result = downloader.download_data(source_id, symbol, start_date_obj, end_date_obj)
    
    if result.success:
        print(f"✅ Successfully downloaded {result.records_count} records")
        print(f"Source: {result.source}")
        print(f"Metadata: {result.metadata}")
        
        # Save to file if specified
        if output_file:
            if downloader.save_to_csv(result, output_file):
                print(f"📁 Saved to: {output_file}")
        else:
            # Default output file
            default_output = f"data/imported/{symbol.lower()}_formatted.csv"
            if downloader.save_to_csv(result, default_output):
                print(f"📁 Saved to: {default_output}")
    else:
        print(f"❌ Download failed: {result.error}")
        return False
    
    return True


def download_all_sources(
    downloader: UnifiedDataDownloader,
    source_type: str = None,
    output_dir: str = "data/imported"
):
    """
    Download data from all enabled sources.
    
    Args:
        downloader: UnifiedDataDownloader instance
        source_type: Filter by source type (optional)
        output_dir: Directory to save output files
    """
    print(f"\n{'='*60}")
    print(f"Downloading from all enabled sources")
    if source_type:
        print(f"Filter by type: {source_type}")
    print(f"{'='*60}\n")
    
    results = downloader.download_all_enabled(source_type)
    
    success_count = 0
    failure_count = 0
    
    for source_id, result in results.items():
        if result.success:
            print(f"✅ {source_id}: {result.records_count} records")
            
            # Save to file
            symbol = result.metadata.get('symbol', source_id)
            output_file = f"{output_dir}/{symbol.lower()}_formatted.csv"
            if downloader.save_to_csv(result, output_file):
                print(f"   📁 Saved to: {output_file}")
            
            success_count += 1
        else:
            print(f"❌ {source_id}: {result.error}")
            failure_count += 1
    
    print(f"\n{'='*60}")
    print(f"Download Summary")
    print(f"{'='*60}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Total: {len(results)}")
    
    return failure_count == 0


def list_sources(downloader: UnifiedDataDownloader):
    """List all available data sources."""
    print(f"\n{'='*60}")
    print("Available Data Sources")
    print(f"{'='*60}\n")
    
    data_sources = downloader.config.get('data_sources', {})
    
    for source_id, source_config in data_sources.items():
        enabled = "✅" if source_config.get('enabled', True) else "❌"
        source_type = source_config.get('type', 'unknown')
        name = source_config.get('name', source_id)
        symbol = source_config.get('symbol') or source_config.get('commodity', 'N/A')
        
        print(f"{enabled} {source_id:20s} {source_type:15s} {symbol:10s} {name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified data downloader for trade service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download from a specific source
  python download_unified.py --source fred_dxy --symbol DXY
  
  # Download with date range
  python download_unified.py --source alpha_vantage_wti --symbol WTI --start-date 2024-01-01 --end-date 2024-12-31
  
  # Download all enabled sources
  python download_unified.py --all
  
  # Download all commodity sources
  python download_unified.py --all --type commodity
  
  # List available sources
  python download_unified.py --list
        """
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Data source ID (e.g., fred_dxy, alpha_vantage_wti)'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        help='Symbol to fetch data for (e.g., DXY, WTI, EUR)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download from all enabled sources'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['exchange_rate', 'commodity', 'dollar_index'],
        help='Filter by data type (with --all)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available data sources'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/data_sources.yml',
        help='Path to configuration file (default: config/data_sources.yml)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Initialize downloader
    try:
        downloader = UnifiedDataDownloader(args.config)
    except Exception as e:
        print(f"Error initializing downloader: {e}")
        sys.exit(1)
    
    # Handle different modes
    if args.list:
        list_sources(downloader)
    elif args.all:
        output_dir = args.config.get('settings', {}).get('import_dir', 'data/imported')
        success = download_all_sources(downloader, args.type, output_dir)
        sys.exit(0 if success else 1)
    elif args.source and args.symbol:
        success = download_single_source(
            downloader,
            args.source,
            args.symbol,
            args.start_date,
            args.end_date,
            args.output
        )
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
