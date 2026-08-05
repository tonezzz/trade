"""
Example script demonstrating the visualization system.
This script shows how to use the visualization module programmatically.
"""
from src.database import db
from src.queries import PriceQueries
from src.visualization import get_visualizer
from datetime import date

def main():
    """Demonstrate visualization capabilities."""
    print("Visualization System Example")
    print("=" * 50)
    
    # Get database session
    session = db.get_session()
    
    try:
        # Initialize queries and visualizer
        queries = PriceQueries(session)
        visualizer = get_visualizer(queries)
        
        print("\n1. Creating EUR exchange rate chart (1 year)...")
        fig = visualizer.plot_exchange_rate(
            currency='EUR',
            period='1y',
            chart_type='line'
        )
        fig.write_html('/tmp/example_eur.html')
        print("   Saved to /tmp/example_eur.html")
        
        print("\n2. Creating GBP candlestick chart (6 months)...")
        fig = visualizer.plot_exchange_rate(
            currency='GBP',
            period='6m',
            chart_type='candlestick'
        )
        fig.write_html('/tmp/example_gbp_candlestick.html')
        print("   Saved to /tmp/example_gbp_candlestick.html")
        
        print("\n3. Creating currency comparison (EUR, GBP, JPY)...")
        fig = visualizer.plot_currency_comparison(
            currencies=['EUR', 'GBP', 'JPY'],
            period='3m',
            normalize=True
        )
        fig.write_html('/tmp/example_comparison.html')
        print("   Saved to /tmp/example_comparison.html")
        
        print("\n4. Creating performance comparison...")
        fig = visualizer.plot_performance_comparison(
            currencies=['EUR', 'GBP', 'JPY'],
            period='3m'
        )
        fig.write_html('/tmp/example_performance.html')
        print("   Saved to /tmp/example_performance.html")
        
        print("\n5. Creating Dollar Index chart...")
        fig = visualizer.plot_dollar_index(
            period='1y'
        )
        fig.write_html('/tmp/example_dxy.html')
        print("   Saved to /tmp/example_dxy.html")
        
        print("\n" + "=" * 50)
        print("All charts generated successfully!")
        print("\nOpen the HTML files in your browser to view the interactive charts.")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This example requires data in the database.")
        print("Import data first using: python cli.py import <type> <file>")
    finally:
        session.close()

if __name__ == '__main__':
    main()
