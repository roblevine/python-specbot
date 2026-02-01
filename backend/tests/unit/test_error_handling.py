"""
Tests for Secure Error Handling Utilities

Feature: Security Hardening
"""

import os
import pytest
from unittest.mock import patch
from src.utils.error_handling import (
    is_debug_mode,
    is_production_environment,
    get_safe_error_response,
    validate_environment_security,
)


class TestDebugMode:
    """Test debug mode detection."""
    
    def test_debug_mode_true(self):
        """Should detect DEBUG=true"""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            assert is_debug_mode() is True
    
    def test_debug_mode_false(self):
        """Should detect DEBUG=false"""
        with patch.dict(os.environ, {"DEBUG": "false"}):
            assert is_debug_mode() is False
    
    def test_debug_mode_default(self):
        """Should default to false when not set"""
        with patch.dict(os.environ, {}, clear=True):
            assert is_debug_mode() is False


class TestProductionEnvironment:
    """Test production environment detection."""
    
    def test_production_environment(self):
        """Should detect ENVIRONMENT=production"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            assert is_production_environment() is True
    
    def test_non_production_environment(self):
        """Should detect non-production environments"""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            assert is_production_environment() is False
        
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            assert is_production_environment() is False
    
    def test_default_environment(self):
        """Should default to development when not set"""
        with patch.dict(os.environ, {}, clear=True):
            assert is_production_environment() is False


class TestGetSafeErrorResponse:
    """Test safe error response generation."""
    
    def test_basic_error_response(self):
        """Should return basic error structure"""
        error = ValueError("Test error")
        response = get_safe_error_response(
            error=error,
            user_message="Something went wrong"
        )
        
        assert response["status"] == "error"
        assert response["error"] == "Something went wrong"
        assert "timestamp" in response
        assert "error_id" in response
    
    def test_no_debug_info_by_default(self):
        """Should not include debug_info by default"""
        with patch.dict(os.environ, {"DEBUG": "false", "ENVIRONMENT": "development"}):
            error = ValueError("Test error")
            response = get_safe_error_response(
                error=error,
                user_message="Something went wrong"
            )
            
            assert "debug_info" not in response
    
    def test_debug_info_in_development(self):
        """Should include debug_info when DEBUG=true in development"""
        with patch.dict(os.environ, {"DEBUG": "true", "ENVIRONMENT": "development"}):
            error = ValueError("Test error")
            response = get_safe_error_response(
                error=error,
                user_message="Something went wrong"
            )
            
            assert "debug_info" in response
            assert response["debug_info"]["error_type"] == "ValueError"
            assert "traceback" in response["debug_info"]
    
    def test_no_debug_info_in_production(self):
        """Should NEVER include debug_info in production, even with DEBUG=true"""
        with patch.dict(os.environ, {"DEBUG": "true", "ENVIRONMENT": "production"}):
            error = ValueError("Test error")
            response = get_safe_error_response(
                error=error,
                user_message="Something went wrong"
            )
            
            # Debug info should be blocked in production
            assert "debug_info" not in response
    
    def test_error_id_generation(self):
        """Should generate unique error IDs"""
        error = ValueError("Test error")
        response1 = get_safe_error_response(error=error, user_message="Error 1")
        response2 = get_safe_error_response(error=error, user_message="Error 2")
        
        assert response1["error_id"] != response2["error_id"]
    
    def test_no_error_id_when_disabled(self):
        """Should not include error_id when disabled"""
        error = ValueError("Test error")
        response = get_safe_error_response(
            error=error,
            user_message="Something went wrong",
            include_error_id=False
        )
        
        assert "error_id" not in response


class TestValidateEnvironmentSecurity:
    """Test environment security validation."""
    
    def test_production_with_debug_runs(self):
        """Should run without error when DEBUG is enabled in production"""
        with patch.dict(os.environ, {"DEBUG": "true", "ENVIRONMENT": "production"}):
            # Should log but not raise - defense in depth blocks debug exposure
            validate_environment_security()  # Should not raise
    
    def test_development_with_debug_runs(self):
        """Should run without error when DEBUG is enabled in development"""
        with patch.dict(os.environ, {"DEBUG": "true", "ENVIRONMENT": "development"}):
            validate_environment_security()  # Should not raise
    
    def test_production_without_debug_runs(self):
        """Should run without error in secure production configuration"""
        with patch.dict(os.environ, {"DEBUG": "false", "ENVIRONMENT": "production"}):
            validate_environment_security()  # Should not raise
    
    def test_all_configurations_run(self):
        """Test various environment configurations"""
        configs = [
            {"DEBUG": "true", "ENVIRONMENT": "production"},
            {"DEBUG": "false", "ENVIRONMENT": "production"},
            {"DEBUG": "true", "ENVIRONMENT": "development"},
            {"DEBUG": "false", "ENVIRONMENT": "development"},
            {"DEBUG": "true"},  # No ENVIRONMENT set
            {"DEBUG": "false"},  # No ENVIRONMENT set
        ]
        
        for config in configs:
            with patch.dict(os.environ, config, clear=True):
                # All configurations should run without raising
                validate_environment_security()
