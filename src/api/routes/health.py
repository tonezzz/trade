"""
Health check API routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.health import HealthChecker
from src.data_quality import DataQualityReporter
from src.api.schemas import HealthResponse, DataQualityResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    System health check endpoint.
    
    Returns:
        Overall system health status and individual check results
    """
    try:
        checker = HealthChecker()
        results = checker.run_all_checks()
        return HealthResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/health/data-quality", response_model=DataQualityResponse)
async def get_data_quality():
    """
    Data quality assessment endpoint.
    
    Returns:
        Data quality report with issues, warnings, and recommendations
    """
    try:
        reporter = DataQualityReporter()
        report = reporter.generate_report()
        return DataQualityResponse(**report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data quality check failed: {str(e)}"
        )


@router.get("/health/database")
async def check_database():
    """
    Database health check endpoint.
    
    Returns:
        Database connection and table status
    """
    try:
        checker = HealthChecker()
        connection_ok = checker.check_database_connection()
        tables_ok = checker.check_database_tables()
        
        return {
            "status": "healthy" if (connection_ok and tables_ok) else "unhealthy",
            "database_connection": connection_ok,
            "database_tables": tables_ok,
            "issues": checker.issues,
            "warnings": checker.warnings
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/health/system")
async def check_system():
    """
    System resource health check endpoint.
    
    Returns:
        System resource usage (CPU, memory, disk)
    """
    try:
        checker = HealthChecker()
        resources_ok = checker.check_system_resources()
        
        return {
            "status": "healthy" if resources_ok else "warning",
            "system_resources": resources_ok,
            "issues": checker.issues,
            "warnings": checker.warnings
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System health check failed: {str(e)}"
        )
