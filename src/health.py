"""
Health check and monitoring module.
"""
import sys
import psutil
from datetime import datetime, timedelta
from sqlalchemy import text
from src.database import db


class HealthChecker:
    """Check system health and database status."""
    
    def __init__(self):
        self.engine = db.engine
        self.issues = []
        self.warnings = []
    
    def check_database_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self.issues.append(f"Database connection failed: {e}")
            return False
    
    def check_database_tables(self) -> bool:
        """Check if required tables exist."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                
                required_tables = ['exchange_rates', 'dollar_index', 'commodity_prices']
                missing_tables = [t for t in required_tables if t not in tables]
                
                if missing_tables:
                    self.issues.append(f"Missing database tables: {missing_tables}")
                    return False
                
                return True
        except Exception as e:
            self.issues.append(f"Database table check failed: {e}")
            return False
    
    def check_data_freshness(self) -> bool:
        """Check if data is reasonably recent."""
        try:
            with self.engine.connect() as conn:
                # Check latest date in each table
                for table in ['exchange_rates', 'dollar_index', 'commodity_prices']:
                    result = conn.execute(text(f"""
                        SELECT MAX(date) as latest_date 
                        FROM {table}
                    """))
                    row = result.fetchone()
                    if row and row[0]:
                        latest_date = row[0]
                        days_old = (datetime.now().date() - latest_date).days
                        
                        if days_old > 30:
                            self.warnings.append(f"{table} data is {days_old} days old")
                        elif days_old > 7:
                            self.warnings.append(f"{table} data is {days_old} days old (consider updating)")
                
            return True
        except Exception as e:
            self.issues.append(f"Data freshness check failed: {e}")
            return False
    
    def check_data_volume(self) -> bool:
        """Check if tables have reasonable data volume."""
        try:
            with self.engine.connect() as conn:
                for table in ['exchange_rates', 'dollar_index', 'commodity_prices']:
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) as row_count 
                        FROM {table}
                    """))
                    row = result.fetchone()
                    if row:
                        count = row[0]
                        if count == 0:
                            self.warnings.append(f"{table} has no data")
                        elif count < 10:
                            self.warnings.append(f"{table} has very little data ({count} rows)")
                
                return True
        except Exception as e:
            self.issues.append(f"Data volume check failed: {e}")
            return False
    
    def check_system_resources(self) -> bool:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                self.warnings.append(f"High CPU usage: {cpu_percent}%")
            elif cpu_percent > 90:
                self.issues.append(f"Critical CPU usage: {cpu_percent}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                self.warnings.append(f"High memory usage: {memory.percent}%")
            elif memory.percent > 90:
                self.issues.append(f"Critical memory usage: {memory.percent}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 80:
                self.warnings.append(f"High disk usage: {disk.percent}%")
            elif disk.percent > 90:
                self.issues.append(f"Critical disk usage: {disk.percent}%")
            
            return True
        except Exception as e:
            self.issues.append(f"System resource check failed: {e}")
            return False
    
    def check_data_quality(self) -> bool:
        """Check for basic data quality issues."""
        try:
            with self.engine.connect() as conn:
                # Check for null rates/prices
                for table, column in [('exchange_rates', 'rate'), 
                                      ('dollar_index', 'value'),
                                      ('commodity_prices', 'price')]:
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM {table} 
                        WHERE {column} IS NULL OR {column} <= 0
                    """))
                    count = result.fetchone()[0]
                    if count > 0:
                        self.warnings.append(f"{table} has {count} invalid {column} values")
                
                # Check for duplicate dates
                for table in ['dollar_index']:
                    result = conn.execute(text(f"""
                        SELECT date, COUNT(*) as count 
                        FROM {table} 
                        GROUP BY date 
                        HAVING COUNT(*) > 1
                    """))
                    duplicates = result.fetchall()
                    if duplicates:
                        self.issues.append(f"{table} has {len(duplicates)} duplicate dates")
                
                return True
        except Exception as e:
            self.issues.append(f"Data quality check failed: {e}")
            return False
    
    def run_all_checks(self) -> dict:
        """Run all health checks and return results."""
        print("Running health checks...")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        # Run checks
        results['checks']['database_connection'] = self.check_database_connection()
        results['checks']['database_tables'] = self.check_database_tables()
        results['checks']['data_freshness'] = self.check_data_freshness()
        results['checks']['data_volume'] = self.check_data_volume()
        results['checks']['data_quality'] = self.check_data_quality()
        results['checks']['system_resources'] = self.check_system_resources()
        
        # Determine overall status
        if self.issues:
            results['status'] = 'unhealthy'
        elif self.warnings:
            results['status'] = 'warning'
        
        results['issues'] = self.issues
        results['warnings'] = self.warnings
        
        return results
    
    def print_results(self, results: dict):
        """Print health check results."""
        print(f"\nHealth Check Results - {results['timestamp']}")
        print("=" * 60)
        print(f"Overall Status: {results['status'].upper()}")
        print()
        
        print("Check Results:")
        for check, passed in results['checks'].items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check.replace('_', ' ').title()}: {status}")
        
        if self.issues:
            print("\n❌ Issues:")
            for issue in self.issues:
                print(f"  - {issue}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ All checks passed!")
        
        print("=" * 60)
        
        # Return exit code
        if self.issues:
            return 2  # Critical issues
        elif self.warnings:
            return 1  # Warnings
        else:
            return 0  # Healthy


def main():
    """Main function to run health checks."""
    checker = HealthChecker()
    results = checker.run_all_checks()
    exit_code = checker.print_results(results)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()