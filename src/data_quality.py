"""
Data quality reporting module.
"""
from datetime import datetime, timedelta
from sqlalchemy import text
from src.database import db


class DataQualityReporter:
    """Generate data quality reports for database content."""
    
    def __init__(self):
        self.engine = db.engine
    
    def generate_report(self) -> dict:
        """
        Generate comprehensive data quality report.
        
        Returns:
            Dictionary containing quality metrics and issues
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'tables': {},
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Analyze each table
        report['tables']['exchange_rates'] = self._analyze_exchange_rates()
        report['tables']['dollar_index'] = self._analyze_dollar_index()
        report['tables']['commodity_prices'] = self._analyze_commodity_prices()
        
        # Generate summary
        self._generate_summary(report)
        
        # Generate recommendations
        self._generate_recommendations(report)
        
        return report
    
    def _analyze_exchange_rates(self) -> dict:
        """Analyze exchange rates table."""
        analysis = {
            'total_records': 0,
            'date_range': {'earliest': None, 'latest': None},
            'currencies': {},
            'data_quality': {},
            'issues': []
        }
        
        try:
            with self.engine.connect() as conn:
                # Total records
                result = conn.execute(text("SELECT COUNT(*) FROM exchange_rates"))
                analysis['total_records'] = result.fetchone()[0]
                
                # Date range
                result = conn.execute(text("""
                    SELECT MIN(date), MAX(date) FROM exchange_rates
                """))
                row = result.fetchone()
                if row:
                    analysis['date_range']['earliest'] = str(row[0])
                    analysis['date_range']['latest'] = str(row[1])
                
                # Currency breakdown
                result = conn.execute(text("""
                    SELECT quote_currency, COUNT(*) as count 
                    FROM exchange_rates 
                    GROUP BY quote_currency
                """))
                for row in result:
                    analysis['currencies'][row[0]] = row[1]
                
                # Data quality checks
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM exchange_rates 
                    WHERE rate IS NULL OR rate <= 0
                """))
                analysis['data_quality']['invalid_rates'] = result.fetchone()[0]
                
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM exchange_rates 
                    WHERE date IS NULL
                """))
                analysis['data_quality']['null_dates'] = result.fetchone()[0]
                
                # Check for gaps in data
                if analysis['total_records'] > 0:
                    result = conn.execute(text("""
                        SELECT date, COUNT(*) as count 
                        FROM exchange_rates 
                        GROUP BY date 
                        HAVING COUNT(*) < 3
                        ORDER BY date DESC
                        LIMIT 5
                    """))
                    for row in result:
                        analysis['issues'].append(f"Date {row[0]} has only {row[1]} currencies")
                
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_dollar_index(self) -> dict:
        """Analyze dollar index table."""
        analysis = {
            'total_records': 0,
            'date_range': {'earliest': None, 'latest': None},
            'value_range': {'min': None, 'max': None, 'avg': None},
            'data_quality': {},
            'issues': []
        }
        
        try:
            with self.engine.connect() as conn:
                # Total records
                result = conn.execute(text("SELECT COUNT(*) FROM dollar_index"))
                analysis['total_records'] = result.fetchone()[0]
                
                # Date range
                result = conn.execute(text("""
                    SELECT MIN(date), MAX(date) FROM dollar_index
                """))
                row = result.fetchone()
                if row:
                    analysis['date_range']['earliest'] = str(row[0])
                    analysis['date_range']['latest'] = str(row[1])
                
                # Value range
                result = conn.execute(text("""
                    SELECT MIN(value), MAX(value), AVG(value) 
                    FROM dollar_index
                """))
                row = result.fetchone()
                if row:
                    analysis['value_range']['min'] = float(row[0])
                    analysis['value_range']['max'] = float(row[1])
                    analysis['value_range']['avg'] = float(row[2])
                
                # Data quality checks
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM dollar_index 
                    WHERE value IS NULL OR value <= 0
                """))
                analysis['data_quality']['invalid_values'] = result.fetchone()[0]
                
                # Check for duplicates
                result = conn.execute(text("""
                    SELECT date, COUNT(*) as count 
                    FROM dollar_index 
                    GROUP BY date 
                    HAVING COUNT(*) > 1
                """))
                duplicates = result.fetchall()
                if duplicates:
                    analysis['issues'].append(f"Found {len(duplicates)} duplicate dates")
                
                # Check for gaps
                if analysis['total_records'] > 1:
                    result = conn.execute(text("""
                        SELECT date, LEAD(date) OVER (ORDER BY date) as next_date
                        FROM dollar_index
                        ORDER BY date
                    """))
                    rows = result.fetchall()
                    gaps = []
                    for i in range(len(rows) - 1):
                        if rows[i][0] and rows[i][1]:
                            gap = (rows[i][1] - rows[i][0]).days
                            if gap > 7:  # More than a week gap
                                gaps.append(f"{gap} days gap starting {rows[i][0]}")
                    
                    if gaps:
                        analysis['issues'].extend(gaps[:5])  # Show first 5 gaps
                
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_commodity_prices(self) -> dict:
        """Analyze commodity prices table."""
        analysis = {
            'total_records': 0,
            'date_range': {'earliest': None, 'latest': None},
            'commodities': {},
            'data_quality': {},
            'issues': []
        }
        
        try:
            with self.engine.connect() as conn:
                # Total records
                result = conn.execute(text("SELECT COUNT(*) FROM commodity_prices"))
                analysis['total_records'] = result.fetchone()[0]
                
                # Date range
                result = conn.execute(text("""
                    SELECT MIN(date), MAX(date) FROM commodity_prices
                """))
                row = result.fetchone()
                if row:
                    analysis['date_range']['earliest'] = str(row[0])
                    analysis['date_range']['latest'] = str(row[1])
                
                # Commodity breakdown
                result = conn.execute(text("""
                    SELECT commodity, COUNT(*) as count 
                    FROM commodity_prices 
                    GROUP BY commodity
                """))
                for row in result:
                    analysis['commodities'][row[0]] = row[1]
                
                # Data quality checks
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM commodity_prices 
                    WHERE price IS NULL OR price <= 0
                """))
                analysis['data_quality']['invalid_prices'] = result.fetchone()[0]
                
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM commodity_prices 
                    WHERE date IS NULL
                """))
                analysis['data_quality']['null_dates'] = result.fetchone()[0]
                
                # Check for extreme prices (potential data errors)
                result = conn.execute(text("""
                    SELECT commodity, AVG(price) as avg_price, STDDEV(price) as std_price
                    FROM commodity_prices
                    GROUP BY commodity
                """))
                for row in result:
                    if row[2]:  # If std exists
                        # Check for prices > 3 standard deviations from mean
                        result2 = conn.execute(text("""
                            SELECT COUNT(*) FROM commodity_prices 
                            WHERE commodity = :commodity 
                            AND ABS(price - :avg_price) > 3 * :std_price
                        """), {'commodity': row[0], 'avg_price': row[1], 'std_price': row[2]})
                        outliers = result2.fetchone()[0]
                        if outliers > 0:
                            analysis['issues'].append(f"{row[0]}: {outliers} potential price outliers")
                
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _generate_summary(self, report: dict):
        """Generate overall summary."""
        total_records = sum(
            table.get('total_records', 0) 
            for table in report['tables'].values()
        )
        
        total_issues = sum(
            len(table.get('issues', [])) 
            for table in report['tables'].values()
        )
        
        report['summary'] = {
            'total_records': total_records,
            'total_issues': total_issues,
            'tables_analyzed': len(report['tables']),
            'overall_health': 'good' if total_issues == 0 else 'needs_attention'
        }
    
    def _generate_recommendations(self, report: dict):
        """Generate improvement recommendations."""
        recommendations = []
        
        # Check for empty tables
        for table_name, table_data in report['tables'].items():
            if table_data.get('total_records', 0) == 0:
                recommendations.append(f"Import data into {table_name} table")
        
        # Check for old data
        for table_name, table_data in report['tables'].items():
            if table_data.get('date_range', {}).get('latest'):
                latest_date = datetime.strptime(
                    table_data['date_range']['latest'], '%Y-%m-%d'
                ).date()
                days_old = (datetime.now().date() - latest_date).days
                if days_old > 30:
                    recommendations.append(
                        f"Update {table_name} data (last update {days_old} days ago)"
                    )
        
        # Check for data quality issues
        for table_name, table_data in report['tables'].items():
            quality = table_data.get('data_quality', {})
            for metric, value in quality.items():
                if value > 0:
                    recommendations.append(
                        f"Fix {value} {metric} issues in {table_name}"
                    )
        
        report['recommendations'] = recommendations
    
    def print_report(self, report: dict):
        """Print formatted data quality report."""
        print("=" * 70)
        print("DATA QUALITY REPORT")
        print("=" * 70)
        print(f"Generated: {report['timestamp']}")
        print()
        
        # Summary
        print("SUMMARY")
        print("-" * 70)
        print(f"Total Records: {report['summary']['total_records']}")
        print(f"Total Issues: {report['summary']['total_issues']}")
        print(f"Tables Analyzed: {report['summary']['tables_analyzed']}")
        print(f"Overall Health: {report['summary']['overall_health'].upper()}")
        print()
        
        # Table details
        for table_name, table_data in report['tables'].items():
            print(f"{table_name.upper()}")
            print("-" * 70)
            print(f"Total Records: {table_data.get('total_records', 0)}")
            
            if table_data.get('date_range'):
                print(f"Date Range: {table_data['date_range'].get('earliest')} to {table_data['date_range'].get('latest')}")
            
            if table_data.get('currencies'):
                print(f"Currencies: {', '.join(table_data['currencies'].keys())}")
            
            if table_data.get('commodities'):
                print(f"Commodities: {', '.join(table_data['commodities'].keys())}")
            
            if table_data.get('value_range'):
                vr = table_data['value_range']
                print(f"Value Range: {vr.get('min')} to {vr.get('max')} (avg: {vr.get('avg'):.2f})")
            
            if table_data.get('data_quality'):
                print("Data Quality:")
                for metric, value in table_data['data_quality'].items():
                    print(f"  {metric}: {value}")
            
            if table_data.get('issues'):
                print("Issues:")
                for issue in table_data['issues'][:5]:  # Show first 5
                    print(f"  - {issue}")
                if len(table_data['issues']) > 5:
                    print(f"  ... and {len(table_data['issues']) - 5} more issues")
            
            print()
        
        # Recommendations
        if report['recommendations']:
            print("RECOMMENDATIONS")
            print("-" * 70)
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
            print()
        
        print("=" * 70)


def main():
    """Main function to generate and print data quality report."""
    reporter = DataQualityReporter()
    report = reporter.generate_report()
    reporter.print_report(report)
    
    # Return exit code based on issues
    if report['summary']['total_issues'] > 10:
        return 2  # Many issues
    elif report['summary']['total_issues'] > 0:
        return 1  # Some issues
    else:
        return 0  # No issues


if __name__ == '__main__':
    import sys
    sys.exit(main())