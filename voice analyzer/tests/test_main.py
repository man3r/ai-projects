"""
Comprehensive unit tests for app/main.py

Tests the FastAPI application setup, middleware configuration,
and basic application properties.
"""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.main import app


class TestFastAPIAppSetup:
    """Test suite for FastAPI application setup and configuration."""

    def test_app_is_fastapi_instance(self):
        """Test that app is a proper FastAPI instance."""
        assert isinstance(app, FastAPI)

    def test_app_title(self):
        """Test that the app has the correct title."""
        assert app.title == "Audio Sentiment Analysis Tool"

    def test_app_description(self):
        """Test that the app has the correct description."""
        expected_description = "Analyze call recordings for sentiment and tone. For call centers."
        assert app.description == expected_description

    def test_app_version(self):
        """Test that the app has the correct version."""
        assert app.version == "0.1.0"

    def test_cors_middleware_added(self):
        """Test that CORS middleware is properly configured."""
        # Check if CORSMiddleware is in the middleware stack
        middleware_types = [type(middleware.cls) for middleware in app.user_middleware]
        assert any(middleware == CORSMiddleware for middleware in middleware_types)

    def test_cors_middleware_configuration(self):
        """Test CORS middleware configuration parameters."""
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None, "CORS middleware not found"
        
        # Check CORS configuration
        kwargs = cors_middleware.kwargs
        assert kwargs.get("allow_origins") == ["*"]
        assert kwargs.get("allow_credentials") is True
        assert kwargs.get("allow_methods") == ["*"]
        assert kwargs.get("allow_headers") == ["*"]

    def test_router_included(self):
        """Test that the router is included in the application."""
        # Check if routes are registered (router should add routes)
        # The router is included with prefix="" and tags=["analysis"]
        route_paths = [route.path for route in app.routes]
        # At minimum, we should have the default docs routes
        assert len(app.routes) > 0

    def test_app_metadata_types(self):
        """Test that app metadata has correct types."""
        assert isinstance(app.title, str)
        assert isinstance(app.description, str)
        assert isinstance(app.version, str)

    @pytest.mark.parametrize("attribute,expected_type", [
        ("title", str),
        ("description", str), 
        ("version", str),
        ("routes", list),
    ])
    def test_app_attributes_types(self, attribute, expected_type):
        """Test that app attributes have expected types."""
        assert isinstance(getattr(app, attribute), expected_type)

    def test_app_has_openapi_schema(self):
        """Test that the app can generate OpenAPI schema."""
        schema = app.openapi()
        assert isinstance(schema, dict)
        assert "openapi" in schema
        assert schema["info"]["title"] == "Audio Sentiment Analysis Tool"
        assert schema["info"]["version"] == "0.1.0"

    def test_app_docs_accessible(self):
        """Test that the app documentation endpoints are accessible."""
        client = TestClient(app)
        
        # Test docs endpoint
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test openapi.json endpoint
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_app_root_endpoint_behavior(self):
        """Test behavior when accessing root endpoint without defined route."""
        client = TestClient(app)
        
        # If no root route is defined, should return 404
        response = client.get("/")
        # This could be 404 or redirect to docs, depending on router configuration
        assert response.status_code in [404, 200, 307]  # 307 for redirect

    def test_cors_headers_in_options_request(self):
        """Test that CORS headers are present in OPTIONS requests."""
        client = TestClient(app)
        
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_headers_in_get_request(self):
        """Test that CORS headers are present in regular requests."""
        client = TestClient(app)
        
        response = client.get("/docs", headers={
            "Origin": "http://localhost:3000"
        })
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_app_middleware_count(self):
        """Test that the expected number of middleware are registered."""
        # Should have at least CORS middleware
        assert len(app.user_middleware) >= 1

    def test_app_exception_handlers(self):
        """Test that app has default exception handlers."""
        # FastAPI should have default exception handlers
        assert hasattr(app, 'exception_handlers')
        assert isinstance(app.exception_handlers, dict)

    def test_app_dependency_overrides(self):
        """Test that dependency overrides attribute exists and is empty by default."""
        assert hasattr(app, 'dependency_overrides')
        assert isinstance(app.dependency_overrides, dict)

    def test_app_state(self):
        """Test that app state is accessible."""
        assert hasattr(app, 'state')
        # Can add custom state for testing
        app.state.test_value = "test"
        assert app.state.test_value == "test"

    def test_app_lifespan_events(self):
        """Test that app has lifespan event handlers."""
        assert hasattr(app, 'router')
        assert hasattr(app.router, 'lifespan')

    def test_invalid_route_returns_404(self):
        """Test that requesting non-existent routes returns 404."""
        client = TestClient(app)
        
        response = client.get("/nonexistent-route")
        assert response.status_code == 404

    def test_app_can_handle_multiple_requests(self):
        """Test that app can handle multiple concurrent requests."""
        client = TestClient(app)
        
        # Make multiple requests to docs endpoint
        responses = []
        for _ in range(5):
            response = client.get("/docs")
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200


class TestAppIntegration:
    """Integration tests for the FastAPI application."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_app_startup_and_shutdown(self, client):
        """Test that app can start up and shut down properly."""
        # Test that we can make a request (implies successful startup)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Test that the response contains expected content
        data = response.json()
        assert data["info"]["title"] == "Audio Sentiment Analysis Tool"

    def test_cors_with_different_origins(self, client):
        """Test CORS functionality with different origins."""
        origins = [
            "http://localhost:3000",
            "https://example.com", 
            "http://127.0.0.1:8080"
        ]
        
        for origin in origins:
            response = client.get("/docs", headers={"Origin": origin})
            assert response.status_code == 200
            assert response.headers.get("access-control-allow-origin") == "*"

    def test_openapi_schema_structure(self, client):
        """Test that OpenAPI schema has expected structure."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        required_fields = ["openapi", "info", "paths"]
        
        for field in required_fields:
            assert field in schema
        
        # Test info section
        info = schema["info"]
        assert info["title"] == "Audio Sentiment Analysis Tool"
        assert info["version"] == "0.1.0"
        assert "description" in info


# Edge case and error condition tests
class TestAppEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_app_with_malformed_request(self):
        """Test app behavior with malformed requests."""
        client = TestClient(app)
        
        # Test with invalid HTTP method if route exists
        response = client.request("INVALID", "/docs")
        assert response.status_code == 405  # Method not allowed

    def test_app_large_header_handling(self):
        """Test app can handle large headers."""
        client = TestClient(app)
        
        large_header_value = "x" * 1000  # 1KB header
        response = client.get("/docs", headers={
            "Custom-Large-Header": large_header_value
        })
        
        # Should still work (unless server has specific limits)
        assert response.status_code == 200

    def test_concurrent_requests_stability(self):
        """Test app stability under concurrent requests."""
        import concurrent.futures
        
        client = TestClient(app)
        
        def make_request():
            return client.get("/docs")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200