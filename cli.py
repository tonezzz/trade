#!/usr/bin/env python3
"""
Command-line interface for the Dollar Price Database.
"""
import argparse
import subprocess
import sys
from pathlib import Path
from src.database import db
from src.importer import import_data
from src.queries import get_queries, get_analysis
from src.visualization import get_visualizer
from datetime import date


def init_db():
    """Initialize the database."""
    print("Initializing database...")
    db.init_db()
    print("Database initialized successfully.")


def setup_db(args):
    """Run database setup wizard."""
    script_path = Path(__file__).parent / 'scripts' / 'setup_database.py'
    
    if not script_path.exists():
        print(f"Error: Setup script not found at {script_path}")
        sys.exit(1)
    
    print("Launching database setup wizard...")
    result = subprocess.run([sys.executable, str(script_path)])
    sys.exit(result.returncode)


def import_csv(args):
    """Import data from CSV file."""
    data_type = args.type
    csv_path = args.file
    source = args.source or 'manual'
    
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    print(f"Importing {data_type} from {csv_path}...")
    count = import_data(data_type, csv_path, source)
    print(f"Successfully imported {count} records.")


def query_data(args):
    """Query and display data."""
    queries = get_queries()
    
    if args.type == 'exchange_rates':
        if not args.currency:
            print("Error: --currency is required for exchange_rates")
            sys.exit(1)
        
        df = queries.get_exchange_rates(args.currency, args.start_date, args.end_date)
        print(f"\nExchange Rates: USD/{args.currency}")
        print(df.to_string())
        
    elif args.type == 'dollar_index':
        df = queries.get_dollar_index(args.start_date, args.end_date)
        print(f"\nDollar Index (DXY)")
        print(df.to_string())
        
    elif args.type == 'commodity_prices':
        df = queries.get_commodity_prices(
            commodity=args.commodity,
            symbol=args.symbol,
            start_date=args.start_date,
            end_date=args.end_date
        )
        print(f"\nCommodity Prices")
        print(df.to_string())


def analyze_data(args):
    """Analyze data performance."""
    analysis = get_analysis()
    
    if args.type == 'currency':
        if not args.currency or not args.start_date or not args.end_date:
            print("Error: --currency, --start-date, and --end-date are required")
            sys.exit(1)
        
        performance = analysis.calculate_currency_performance(
            args.currency,
            args.start_date,
            args.end_date
        )
        print(f"\nCurrency Performance: USD/{args.currency}")
        for key, value in performance.items():
            print(f"  {key}: {value}")
            
    elif args.type == 'dxy':
        if not args.start_date or not args.end_date:
            print("Error: --start-date and --end-date are required")
            sys.exit(1)
        
        performance = analysis.calculate_dxy_performance(
            args.start_date,
            args.end_date
        )
        print(f"\nDollar Index Performance")
        for key, value in performance.items():
            print(f"  {key}: {value}")


def list_data(args):
    """List available data types."""
    analysis = get_analysis()
    
    if args.type == 'currencies':
        currencies = analysis.get_available_currencies()
        print(f"\nAvailable Currencies:")
        for currency in currencies:
            print(f"  - {currency}")
            
    elif args.type == 'commodities':
        commodities = analysis.get_available_commodities()
        print(f"\nAvailable Commodities:")
        for commodity in commodities:
            print(f"  - {commodity}")


def chart_data(args):
    """Generate and display charts."""
    queries = get_queries()
    visualizer = get_visualizer(queries)
    
    try:
        if args.type == 'exchange_rates':
            if not args.currency:
                print("Error: --currency is required for exchange_rates")
                sys.exit(1)
            
            fig = visualizer.plot_exchange_rate(
                currency=args.currency,
                period=args.period or '1y',
                chart_type=args.chart_type or 'line',
                show_volume=args.volume or False,
                save_path=args.output
            )
            
            if args.output:
                print(f"Chart saved to {args.output}")
            else:
                fig.show()
                
        elif args.type == 'commodity_prices':
            if not args.commodity:
                print("Error: --commodity is required for commodity_prices")
                sys.exit(1)
            
            fig = visualizer.plot_commodity_price(
                commodity=args.commodity,
                period=args.period or '1y',
                chart_type=args.chart_type or 'line',
                show_volume=args.volume or False,
                save_path=args.output
            )
            
            if args.output:
                print(f"Chart saved to {args.output}")
            else:
                fig.show()
                
        elif args.type == 'comparison':
            if not args.currencies:
                print("Error: --currencies is required for comparison")
                sys.exit(1)
            
            currencies = [c.strip() for c in args.currencies.split(',')]
            
            if args.performance:
                fig = visualizer.plot_performance_comparison(
                    currencies=currencies,
                    period=args.period or '3m',
                    save_path=args.output
                )
            else:
                fig = visualizer.plot_currency_comparison(
                    currencies=currencies,
                    period=args.period or '3m',
                    normalize=not args.raw,
                    save_path=args.output
                )
            
            if args.output:
                print(f"Chart saved to {args.output}")
            else:
                fig.show()
                
        elif args.type == 'dollar_index':
            fig = visualizer.plot_dollar_index(
                period=args.period or '1y',
                chart_type=args.chart_type or 'line',
                show_volume=args.volume or False,
                save_path=args.output
            )
            
            if args.output:
                print(f"Chart saved to {args.output}")
            else:
                fig.show()
                
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Dollar Price Database CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    subparsers.add_parser('init', help='Initialize database')
    
    # Setup command
    subparsers.add_parser('setup', help='Run database setup wizard')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data from CSV')
    import_parser.add_argument('type', choices=['exchange_rates', 'dollar_index', 'commodity_prices'],
                              help='Type of data to import_csv')
    import_parser.add_argument('file', help='Path to CSV file')
    import_parser.add_argument('--source', help='Data source identifier')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query data')
    query_parser.add_argument('type', choices=['exchange_rates', 'dollar_index', 'commodity_prices'],
                             help='Type of data to query')
    query_parser.add_argument('--currency', help='Currency code (for exchange_rates)')
    query_parser.add_argument('--commodity', help='Commodity name (for commodity_prices)')
    query_parser.add_argument('--symbol', help='Trading symbol (for commodity_prices)')
    query_parser.add_argument('--start-date', type=lambda d: date.fromisoformat(d), 
                             help='Start date (YYYY-MM-DD)')
    query_parser.add_argument('--end-date', type=lambda d: date.fromisoformat(d),
                             help='End date (YYYY-MM-DD)')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze data performance')
    analyze_parser.add_argument('type', choices=['currency', 'dxy'],
                               help='Type of analysis')
    analyze_parser.add_argument('--currency', help='Currency code (for currency analysis)')
    analyze_parser.add_argument('--start-date', type=lambda d: date.fromisoformat(d),
                               help='Start date (YYYY-MM-DD)')
    analyze_parser.add_argument('--end-date', type=lambda d: date.fromisoformat(d),
                               help='End date (YYYY-MM-DD)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available data')
    list_parser.add_argument('type', choices=['currencies', 'commodities'],
                            help='Type of data to list')
    
    # Chart command
    chart_parser = subparsers.add_parser('chart', help='Generate price charts')
    chart_parser.add_argument('type', choices=['exchange_rates', 'commodity_prices', 'comparison', 'dollar_index'],
                             help='Type of chart to generate')
    chart_parser.add_argument('--currency', help='Currency code (for exchange_rates)')
    chart_parser.add_argument('--commodity', help='Commodity name (for commodity_prices)')
    chart_parser.add_argument('--currencies', help='Comma-separated currency list (for comparison, e.g., EUR,GBP,JPY)')
    chart_parser.add_argument('--period', default='1y',
                             help='Time period: 1d, 1w, 1m, 3m, 6m, 1y, 5y (default: 1y)')
    chart_parser.add_argument('--chart-type', choices=['line', 'candlestick'],
                             help='Chart type: line or candlestick (default: line)')
    chart_parser.add_argument('--volume', action='store_true',
                             help='Show volume subplot')
    chart_parser.add_argument('--raw', action='store_true',
                             help='Show raw values instead of normalized (for comparison)')
    chart_parser.add_argument('--performance', action='store_true',
                             help='Show performance comparison (percentage change)')
    chart_parser.add_argument('--output', '-o', help='Save chart to HTML file instead of displaying')
    
    # Health command
    subparsers.add_parser('health', help='Run system health checks')
    
    # Data quality command
    subparsers.add_parser('quality', help='Generate data quality report')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_db()
    elif args.command == 'setup':
        setup_db(args)
    elif args.command == 'import':
        import_csv(args)
    elif args.command == 'query':
        query_data(args)
    elif args.command == 'analyze':
        analyze_data(args)
    elif args.command == 'list':
        list_data(args)
    elif args.command == 'chart':
        chart_data(args)
    elif args.command == 'health':
        from src.health import main as health_main
        import sys
        sys.exit(health_main())
    elif args.command == 'quality':
        from src.data_quality import main as quality_main
        import sys
        sys.exit(quality_main())
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
