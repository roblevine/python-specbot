"""
Integration tests for DEBUG mode error handling.

Verifies that when DEBUG=true, detailed error information is exposed in API responses.
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


@pytest.mark.integration
def test_debug_mode_model_configuration_error():
    """
    Verify that model configuration errors include debug info when DEBUG=true.
    """
    # Enable DEBUG mode with invalid configuration
    # Use clear=True to avoid inheriting environment configs that may conflict
    # Must include OPENAI_API_KEY to enable the OpenAI provider (so invalid JSON triggers error)
    with patch.dict(os.environ, {
        "DEBUG": "true",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODELS": "invalid json"
    }, clear=True):
        client = TestClient(app)

        # Request models endpoint
        response = client.get("/api/v1/models")

        # Should return 503
        assert response.status_code == 503

        data = response.json()

        # HTTPException puts everything under 'detail'
        assert "detail" in data
        detail = data["detail"]

        # Should include debug_info
        assert "debug_info" in detail
        assert detail["debug_info"]["error_type"] == "ModelConfigurationError"
        assert "traceback" in detail["debug_info"]
        assert "Invalid JSON" in detail["debug_info"]["error_message"]


@pytest.mark.integration
def test_debug_mode_disabled_hides_details():
    """
    Verify that when DEBUG=false, detailed error information is NOT exposed.
    """
    # Disable DEBUG mode with invalid configuration
    # Use clear=True to avoid inheriting environment configs that may conflict
    # Must include OPENAI_API_KEY to enable the OpenAI provider (so invalid JSON triggers error)
    with patch.dict(os.environ, {
        "DEBUG": "false",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODELS": "invalid json"
    }, clear=True):
        client = TestClient(app)

        # Request models endpoint
        response = client.get("/api/v1/models")

        # Should return 503
        assert response.status_code == 503

        data = response.json()

        # HTTPException puts everything under 'detail'
        assert "detail" in data
        detail = data["detail"]

        # Should NOT include debug_info when DEBUG is false
        assert "debug_info" not in detail
