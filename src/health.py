"""
Health check and monitoring module.
"""
import sys
import psutil
import yaml
from datetime import datetime, timedelta
from sqlalchemy import text
from src.database import db


class HealthChecker:
    """Check system health and database status."""
    
    def __init__(self, config_path: str = "config/data_sources.yml"):
        self.engine = db.engine
        self.issues = []
        self.warnings = []
        self.config_path = config_path
        self.tolerance_settings = self._load_tolerance_settings()
    
    def _load_tolerance_settings(self) -> dict:
        """Load tolerance settings from configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('settings', {}).get('tolerance', {})
        except Exception as e:
            print(f"Warning: Could not load tolerance settings: {e}")
            # Return default tolerances
            return {
                'thb': 2,
                'dxy': 30,
                'commodities': 90,
                'currencies': 7
            }
    
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
                # Check database type
                if self.engine.dialect.name == 'postgresql':
                    # PostgreSQL query
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """))
                    tables = [row[0] for row in result]
                else:
                    # SQLite query
                    result = conn.execute(text("""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table'
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
        """Check if data is reasonably recent using type-specific tolerance."""
        try:
            with self.engine.connect() as conn:
                # Check THB (2-day tolerance)
                self._check_freshness_by_currency(conn, 'THB', self.tolerance_settings.get('thb', 2))
                
                # Check DXY (30-day tolerance)
                self._check_freshness_dxy(conn, self.tolerance_settings.get('dxy', 30))
                
                # Check commodities (90-day tolerance)
                self._check_freshness_commodities(conn, self.tolerance_settings.get('commodities', 90))
                
                # Check other currencies (7-day tolerance)
                for currency in ['JPY', 'CAD', 'CHF', 'AUD', 'NZD']:
                    self._check_freshness_by_currency(conn, currency, self.tolerance_settings.get('currencies', 7))
                
                return True
        except Exception as e:
            self.issues.append(f"Data freshness check failed: {e}")
            return False
    
    def _check_freshness_by_currency(self, conn, currency: str, tolerance_days: int):
        """Check freshness for a specific currency."""
        result = conn.execute(text("""
            SELECT MAX(date) as latest_date 
            FROM exchange_rates 
            WHERE quote_currency = :currency
        """), {"currency": currency})
        row = result.fetchone()
        
        if row and row[0]:
            latest_date = self._parse_date(row[0])
            days_old = (datetime.now().date() - latest_date).days
            
            if days_old > tolerance_days * 2:
                self.issues.append(f"{currency} data is {days_old} days old (tolerance: {tolerance_days} days)")
            elif days_old > tolerance_days:
                self.warnings.append(f"{currency} data is {days_old} days old (tolerance: {tolerance_days} days)")
    
    def _check_freshness_dxy(self, conn, tolerance_days: int):
        """Check freshness for Dollar Index."""
        result = conn.execute(text("""
            SELECT MAX(date) as latest_date 
            FROM dollar_index
        """))
        row = result.fetchone()
        
        if row and row[0]:
            latest_date = self._parse_date(row[0])
            days_old = (datetime.now().date() - latest_date).days
            
            if days_old > tolerance_days * 2:
                self.issues.append(f"DXY data is {days_old} days old (tolerance: {tolerance_days} days)")
            elif days_old > tolerance_days:
                self.warnings.append(f"DXY data is {days_old} days old (tolerance: {tolerance_days} days)")
    
    def _check_freshness_commodities(self, conn, tolerance_days: int):
        """Check freshness for commodities."""
        result = conn.execute(text("""
            SELECT MAX(date) as latest_date 
            FROM commodity_prices
        """))
        row = result.fetchone()
        
        if row and row[0]:
            latest_date = self._parse_date(row[0])
            days_old = (datetime.now().date() - latest_date).days
            
            if days_old > tolerance_days * 2:
                self.issues.append(f"Commodity data is {days_old} days old (tolerance: {tolerance_days} days)")
            elif days_old > tolerance_days:
                self.warnings.append(f"Commodity data is {days_old} days old (tolerance: {tolerance_days} days)")
    
    def _parse_date(self, date_value):
        """Parse date from various formats."""
        if isinstance(date_value, str):
            from dateutil.parser import parse
            return parse(date_value).date()
        elif hasattr(date_value, 'date'):
            return date_value.date()
        return date_value
    
    def _get_latest_date(self, conn, table: str, currency: str = None):
        """Get latest date for a table or specific currency."""
        try:
            if currency:
                result = conn.execute(text(f"""
                    SELECT MAX(date) as latest_date 
                    FROM {table} 
                    WHERE quote_currency = :currency
                """), {"currency": currency})
            else:
                result = conn.execute(text(f"""
                    SELECT MAX(date) as latest_date 
                    FROM {table}
                """))
            row = result.fetchone()
            return self._parse_date(row[0]) if row and row[0] else None
        except Exception as e:
            print(f"Error getting latest date: {e}")
            return None
    
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
    
    def check_data_gaps(self) -> dict:
        """Check for data gaps with type-specific tolerance."""
        gaps = {
            'critical': [],
            'warning': [],
            'info': []
        }
        
        try:
            with self.engine.connect() as conn:
                # Check THB gaps (2-day tolerance, but allow for recent manual update)
                thb_gap = self._check_gap(conn, 'exchange_rates', 'THB', 2)
                # Check if latest data is actually current before flagging as gap
                latest_thb = self._get_latest_date(conn, 'exchange_rates', 'THB')
                days_old = (datetime.now().date() - latest_thb).days if latest_thb else 999
                
                if days_old <= 1:
                    # Data is current, ignore historical gaps
                    pass
                elif thb_gap > 4:
                    gaps['critical'].append(f"THB gap: {thb_gap} days")
                elif thb_gap > 2:
                    gaps['warning'].append(f"THB gap: {thb_gap} days")
                elif thb_gap > 0:
                    gaps['info'].append(f"THB gap: {thb_gap} days")
                
                # Check currency gaps (7-day tolerance)
                for currency in ['JPY', 'CAD', 'CHF', 'AUD', 'NZD']:
                    gap = self._check_gap(conn, 'exchange_rates', currency, 7)
                    if gap > 14:
                        gaps['critical'].append(f"{currency} gap: {gap} days")
                    elif gap > 7:
                        gaps['warning'].append(f"{currency} gap: {gap} days")
                    elif gap > 0:
                        gaps['info'].append(f"{currency} gap: {gap} days")
                
                # Check DXY gaps (30-day tolerance)
                dxy_gap = self._check_gap_dxy(conn, 30)
                if dxy_gap > 60:
                    gaps['critical'].append(f"DXY gap: {dxy_gap} days")
                elif dxy_gap > 30:
                    gaps['warning'].append(f"DXY gap: {dxy_gap} days")
                elif dxy_gap > 0:
                    gaps['info'].append(f"DXY gap: {dxy_gap} days")
                
                # Check commodity gaps (90-day tolerance)
                commodity_gap = self._check_gap_commodities(conn, 90)
                if commodity_gap > 180:
                    gaps['critical'].append(f"Commodity gap: {commodity_gap} days")
                elif commodity_gap > 90:
                    gaps['warning'].append(f"Commodity gap: {commodity_gap} days")
                elif commodity_gap > 0:
                    gaps['info'].append(f"Commodity gap: {commodity_gap} days")
                
                # Add gaps to issues/warnings
                for gap in gaps['critical']:
                    self.issues.append(f"Data gap: {gap}")
                for gap in gaps['warning']:
                    self.warnings.append(f"Data gap: {gap}")
                
                return gaps
                
        except Exception as e:
            self.issues.append(f"Data gap check failed: {e}")
            return gaps
    
    def _check_gap(self, conn, table: str, currency: str, tolerance_days: int) -> int:
        """Check gap for a specific currency (recent 30 days only)."""
        try:
            # Use date filtering compatible with both SQLite and PostgreSQL
            cutoff_date = datetime.now() - timedelta(days=30)
            
            if self.engine.dialect.name == 'postgresql':
                result = conn.execute(text(f"""
                    SELECT date 
                    FROM {table} 
                    WHERE quote_currency = :currency
                    AND date >= :cutoff_date
                    ORDER BY date DESC 
                    LIMIT 30
                """), {"currency": currency, "cutoff_date": cutoff_date})
            else:
                # SQLite
                result = conn.execute(text(f"""
                    SELECT date 
                    FROM {table} 
                    WHERE quote_currency = :currency
                    AND date >= :cutoff_date
                    ORDER BY date DESC 
                    LIMIT 30
                """), {"currency": currency, "cutoff_date": cutoff_date})
            
            dates = [self._parse_date(row[0]) for row in result]
            
            if len(dates) < 2:
                return 0
            
            max_gap = 0
            for i in range(len(dates) - 1):
                gap = (dates[i] - dates[i + 1]).days
                if gap > max_gap:
                    max_gap = gap
            
            return max_gap
        except Exception as e:
            print(f"Error checking gap for {currency}: {e}")
            return 0
    
    def _check_gap_dxy(self, conn, tolerance_days: int) -> int:
        """Check gap for Dollar Index (recent 30 days only)."""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            if self.engine.dialect.name == 'postgresql':
                result = conn.execute(text("""
                    SELECT date 
                    FROM dollar_index 
                    WHERE date >= :cutoff_date
                    ORDER BY date DESC 
                    LIMIT 30
                """), {"cutoff_date": cutoff_date})
            else:
                # SQLite
                result = conn.execute(text("""
                    SELECT date 
                    FROM dollar_index 
                    WHERE date >= :cutoff_date
                    ORDER BY date DESC 
                    LIMIT 30
                """), {"cutoff_date": cutoff_date})
            
            dates = [self._parse_date(row[0]) for row in result]
            
            if len(dates) < 2:
                return 0
            
            max_gap = 0
            for i in range(len(dates) - 1):
                gap = (dates[i] - dates[i + 1]).days
                if gap > max_gap:
                    max_gap = gap
            
            return max_gap
        except Exception as e:
            print(f"Error checking DXY gap: {e}")
            return 0
    
    def _check_gap_commodities(self, conn, tolerance_days: int) -> int:
        """Check gap for commodities (recent 30 days only)."""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            if self.engine.dialect.name == 'postgresql':
                result = conn.execute(text("""
                    SELECT date 
                    FROM commodity_prices 
                    WHERE date >= :cutoff_date
                    ORDER BY date DESC 
                    LIMIT 30
                """), {"cutoff_date": cutoff_date})
            else:
                # SQLite
                result = conn.execute(text("""
                    SELECT date 
                    FROM commodity_prices 
                    WHERE date >= :cutoff_date
                    ORDER BY date DESC 
                    LIMIT 30
                """), {"cutoff_date": cutoff_date})
            
            dates = [self._parse_date(row[0]) for row in result]
            
            if len(dates) < 2:
                return 0
            
            max_gap = 0
            for i in range(len(dates) - 1):
                gap = (dates[i] - dates[i + 1]).days
                if gap > max_gap:
                    max_gap = gap
            
            return max_gap
        except Exception as e:
            print(f"Error checking commodity gap: {e}")
            return 0
    
    def run_all_checks(self) -> dict:
        """Run all health checks and return results."""
        print("Running health checks...")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {},
            'data_gaps': {}
        }
        
        # Run checks
        results['checks']['database_connection'] = self.check_database_connection()
        results['checks']['database_tables'] = self.check_database_tables()
        results['checks']['data_freshness'] = self.check_data_freshness()
        results['checks']['data_volume'] = self.check_data_volume()
        results['checks']['data_quality'] = self.check_data_quality()
        results['checks']['system_resources'] = self.check_system_resources()
        results['checks']['data_gaps'] = self.check_data_gaps()
        results['data_gaps'] = self.check_data_gaps()
        
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
        
        print()
        
        # Print data gaps if available
        if 'data_gaps' in results and results['data_gaps']:
            print("Data Gaps:")
            gaps = results['data_gaps']
            if gaps.get('critical'):
                print(f"  Critical: {', '.join(gaps['critical'])}")
            if gaps.get('warning'):
                print(f"  Warning: {', '.join(gaps['warning'])}")
            if gaps.get('info'):
                print(f"  Info: {', '.join(gaps['info'])}")
            if not any(gaps.values()):
                print("  No significant gaps detected")
            print()
        
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


if __name__ == "__main__":
    checker = HealthChecker()
    results = checker.run_all_checks()
    checker.print_results(results)
