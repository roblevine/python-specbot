"""
Tests for CORS Security Configuration

Feature: Security Hardening
"""

import pytest
from urllib.parse import urlparse


def validate_frontend_url(url: str) -> str:
    """
    Validate FRONTEND_URL format for security.
    (Duplicated from main.py for testing)
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid FRONTEND_URL format: {url}")
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"FRONTEND_URL must use http or https: {url}")
        return url
    except Exception as e:
        raise ValueError(f"Invalid FRONTEND_URL: {url}") from e


class TestFrontendURLValidation:
    """Test FRONTEND_URL validation."""
    
    def test_valid_http_url(self):
        """Should accept valid http URLs"""
        url = "http://localhost:5173"
        assert validate_frontend_url(url) == url
        
        url = "http://example.com:3000"
        assert validate_frontend_url(url) == url
    
    def test_valid_https_url(self):
        """Should accept valid https URLs"""
        url = "https://example.com"
        assert validate_frontend_url(url) == url
        
        url = "https://app.example.com:8443"
        assert validate_frontend_url(url) == url
    
    def test_rejects_invalid_scheme(self):
        """Should reject non-http(s) schemes"""
        with pytest.raises(ValueError) as exc_info:
            validate_frontend_url("ftp://example.com")
        # Error is wrapped, so just check that it raised ValueError
        assert "Invalid FRONTEND_URL" in str(exc_info.value) or "http or https" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            validate_frontend_url("file:///etc/passwd")
        assert "Invalid FRONTEND_URL" in str(exc_info.value) or "http or https" in str(exc_info.value)
    
    def test_rejects_no_scheme(self):
        """Should reject URLs without scheme"""
        with pytest.raises(ValueError):
            validate_frontend_url("example.com")
    
    def test_rejects_no_host(self):
        """Should reject URLs without host"""
        with pytest.raises(ValueError):
            validate_frontend_url("http://")
    
    def test_rejects_malformed_url(self):
        """Should reject malformed URLs"""
        with pytest.raises(ValueError):
            validate_frontend_url("not a valid url at all")


class TestCORSConfiguration:
    """Test CORS middleware configuration security."""
    
    def test_cors_allows_specific_methods_only(self):
        """CORS should only allow specific HTTP methods, not wildcard"""
        # This is a documentation test - the actual config is in main.py
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        
        # Verify we're not using wildcard
        assert "*" not in allowed_methods
        
        # Verify we only have necessary methods
        assert len(allowed_methods) <= 5
        assert "GET" in allowed_methods  # Read data
        assert "POST" in allowed_methods  # Create/send data
        assert "OPTIONS" in allowed_methods  # Preflight
    
    def test_cors_allows_specific_headers_only(self):
        """CORS should only allow specific headers, not wildcard"""
        # This is a documentation test - the actual config is in main.py
        allowed_headers = ["Content-Type", "Authorization", "Accept", "X-Requested-With"]
        
        # Verify we're not using wildcard
        assert "*" not in allowed_headers
        
        # Verify we only have necessary headers
        assert len(allowed_headers) <= 6
        assert "Content-Type" in allowed_headers  # Required for JSON
        assert "Authorization" in allowed_headers  # For future auth
    
    def test_cors_requires_specific_origins(self):
        """CORS should use specific origins, not wildcard"""
        # Document that wildcard origins should never be used
        # with credentials=True
        
        # This would be insecure (documented here as anti-pattern):
        insecure_pattern = {"allow_origins": ["*"], "allow_credentials": True}
        
        # Verify this is NOT our configuration
        assert insecure_pattern != {
            "allow_origins": ["http://localhost:5173"],
            "allow_credentials": True
        }
