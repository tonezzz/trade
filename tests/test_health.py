"""
Unit tests for health check module.
"""
import pytest
from datetime import date, datetime
from src.health import HealthChecker


class TestHealthChecker:
    """Test HealthChecker class."""
    
    def test_health_checker_initialization(self):
        """Test health checker initialization."""
        checker = HealthChecker()
        assert checker.engine is not None
        assert checker.issues == []
        assert checker.warnings == []
    
    def test_health_checker_with_config(self):
        """Test health checker with custom config."""
        checker = HealthChecker(config_path="config/data_sources.yml")
        assert checker.config_path == "config/data_sources.yml"
        assert checker.tolerance_settings is not None
    
    def test_load_tolerance_settings(self):
        """Test loading tolerance settings."""
        checker = HealthChecker()
        tolerances = checker._load_tolerance_settings()
        
        assert isinstance(tolerances, dict)
        assert 'thb' in tolerances or 'currencies' in tolerances
        assert 'dxy' in tolerances or 'commodities' in tolerances
    
    def test_load_tolerance_settings_fallback(self):
        """Test loading tolerance settings with fallback."""
        checker = HealthChecker(config_path="nonexistent.yml")
        tolerances = checker._load_tolerance_settings()
        
        # Should return default tolerances
        assert isinstance(tolerances, dict)
        assert 'thb' in tolerances or 'currencies' in tolerances
    
    def test_parse_date(self):
        """Test date parsing."""
        checker = HealthChecker()
        
        # Test string date
        result = checker._parse_date('2024-01-01')
        assert result == date(2024, 1, 1)
        
        # Test date object
        test_date = date(2024, 1, 1)
        result = checker._parse_date(test_date)
        assert result == test_date
    
    def test_print_results(self):
        """Test printing health check results."""
        checker = HealthChecker()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {}
        }
        
        # Should not raise exception
        checker.print_results(results)
    
    def test_print_results_with_gaps(self):
        """Test printing health check results with gaps."""
        checker = HealthChecker()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'checks': {},
            'data_gaps': {
                'critical': [],
                'warning': [],
                'info': ['Test gap: 2 days']
            }
        }
        
        # Should not raise exception
        checker.print_results(results)
    
    def test_print_results_with_issues(self):
        """Test printing health check results with issues."""
        checker = HealthChecker()
        checker.issues = ['Test issue']
        checker.warnings = ['Test warning']
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'unhealthy',
            'checks': {}
        }
        
        # Should not raise exception
        checker.print_results(results)


class TestHealthCheckIntegration:
    """Integration tests for health checks."""
    
    def test_health_checker_integration(self):
        """Test health checker with real database."""
        checker = HealthChecker()
        
        # Test that it can be instantiated
        assert checker is not None
        assert checker.engine is not None
    
    def test_health_checker_run_all_checks(self):
        """Test running all health checks."""
        checker = HealthChecker()
        
        # Run all checks - this will use real database
        results = checker.run_all_checks()
        
        # Verify structure
        assert 'timestamp' in results
        assert 'status' in results
        assert 'checks' in results