"""
Service for data quality business logic.
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from src.services.base_service import BaseService
from src.data_quality import DataQualityReporter


class DataQualityService(BaseService):
    """Service for data quality operations."""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.reporter = DataQualityReporter()
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Returns:
            Dictionary with data quality assessment
        """
        try:
            report = self.reporter.generate_report()
            return report
        except Exception as e:
            return self.handle_exception(e, "Error generating quality report")
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """
        Check data freshness across all tables.
        
        Returns:
            Dictionary with freshness status
        """
        try:
            from src.health import HealthChecker
            checker = HealthChecker()
            
            freshness_ok = checker.check_data_freshness()
            
            return {
                'status': 'ok' if freshness_ok else 'warning',
                'issues': checker.issues,
                'warnings': checker.warnings
            }
        except Exception as e:
            return self.handle_exception(e, "Error checking data freshness")
    
    def check_data_completeness(self) -> Dict[str, Any]:
        """
        Check data completeness across all tables.
        
        Returns:
            Dictionary with completeness status
        """
        try:
            from src.health import HealthChecker
            checker = HealthChecker()
            
            volume_ok = checker.check_data_volume()
            
            return {
                'status': 'ok' if volume_ok else 'warning',
                'issues': checker.issues,
                'warnings': checker.warnings
            }
        except Exception as e:
            return self.handle_exception(e, "Error checking data completeness")
    
    def check_data_quality(self) -> Dict[str, Any]:
        """
        Check data quality (null values, duplicates, etc.).
        
        Returns:
            Dictionary with data quality status
        """
        try:
            from src.health import HealthChecker
            checker = HealthChecker()
            
            quality_ok = checker.check_data_quality()
            
            return {
                'status': 'ok' if quality_ok else 'warning',
                'issues': checker.issues,
                'warnings': checker.warnings
            }
        except Exception as e:
            return self.handle_exception(e, "Error checking data quality")
    
    def run_quality_checks(self) -> Dict[str, Any]:
        """
        Run all quality checks and return combined results.
        
        Returns:
            Dictionary with combined quality check results
        """
        try:
            freshness = self.check_data_freshness()
            completeness = self.check_data_completeness()
            quality = self.check_data_quality()
            
            # Combine issues and warnings
            all_issues = (
                freshness.get('issues', []) + 
                completeness.get('issues', []) + 
                quality.get('issues', [])
            )
            all_warnings = (
                freshness.get('warnings', []) + 
                completeness.get('warnings', []) + 
                quality.get('warnings', [])
            )
            
            # Determine overall status
            if all_issues:
                overall_status = 'unhealthy'
            elif all_warnings:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'
            
            return {
                'overall_status': overall_status,
                'freshness': freshness,
                'completeness': completeness,
                'quality': quality,
                'total_issues': len(all_issues),
                'total_warnings': len(all_warnings),
                'issues': all_issues,
                'warnings': all_warnings
            }
        except Exception as e:
            return self.handle_exception(e, "Error running quality checks")
