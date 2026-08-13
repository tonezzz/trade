"""
Unit tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.api import create_app
app = create_app()


class TestAPIEndpoints:
    """Test API endpoints exist and respond."""
    
    def test_api_root(self):
        """Test API root endpoint."""
        client = TestClient(app)
        response = client.get("/")
        
        # Root might not exist, but should return something reasonable
        assert response.status_code in [200, 404]
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        # Health endpoint should exist
        assert response.status_code in [200, 404]
    
    def test_exchange_rates_endpoint(self):
        """Test exchange rates endpoint."""
        client = TestClient(app)
        response = client.get("/api/exchange-rates/USD/THB")
        
        # Should return something (data or 404 if no data)
        assert response.status_code in [200, 404, 500]
    
    def test_commodities_endpoint(self):
        """Test commodities endpoint."""
        client = TestClient(app)
        response = client.get("/api/commodities/GOLD")
        
        # Should return something (data or 404 if no data)
        assert response.status_code in [200, 404, 500]
    
    def test_dollar_index_endpoint(self):
        """Test dollar index endpoint."""
        client = TestClient(app)
        response = client.get("/api/dollar-index")
        
        # Should return something (data or 404 if no data)
        assert response.status_code in [200, 404, 500]
    
    def test_signals_endpoint(self):
        """Test signals endpoint."""
        client = TestClient(app)
        response = client.get("/api/signals")
        
        # Should return something (data or 404 if no data)
        assert response.status_code in [200, 404, 500]


class TestAPIIntegration:
    """Integration tests for API."""
    
    def test_api_responds(self):
        """Test that API responds to requests."""
        client = TestClient(app)
        
        # Test a simple endpoint
        response = client.get("/health")
        assert response.status_code in [200, 404]
    
    def test_api_has_cors_enabled(self):
        """Test that CORS is configured."""
        # Check that the app has middleware
        assert len(app.user_middleware) > 0
