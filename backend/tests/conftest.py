"""
Pytest configuration and shared fixtures for backend tests

Provides:
- TestClient for integration tests
- OpenAPI spec loader for contract tests
- Common test data fixtures
- Environment variable mocking for test isolation
"""

import os
from typing import Generator

import pytest
import yaml
from fastapi.testclient import TestClient
from openapi_core import Spec


@pytest.fixture(scope="function", autouse=True)
def mock_test_env_vars(monkeypatch):
    """
    Override environment variables for all tests to ensure test isolation.

    This fixture runs automatically for every test (autouse=True) and ensures
    tests don't depend on local .env configuration which may differ across machines.

    Args:
        monkeypatch: pytest fixture for modifying environment variables
    """
    # CRITICAL: Unset OPENAI_MODELS to prevent it from overriding OPENAI_MODEL
    # The config loader prioritizes OPENAI_MODELS over OPENAI_MODEL (see config/models.py:101-137)
    monkeypatch.delenv("OPENAI_MODELS", raising=False)

    # Set predictable test values BEFORE any imports that load config
    monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-12345")

    # Clear any cached LLM instances to force reload with new env vars
    try:
        import src.services.llm_service as llm_service
        llm_service._llm_instance = None
    except (ImportError, AttributeError):
        pass  # Module not imported yet or no cache to clear

    # Note: Individual tests can still override these with their own patch.dict
    # if they need to test different configurations


@pytest.fixture(scope="session")
def openapi_spec() -> Spec:
    """
    Load OpenAPI specification for contract testing.

    Returns:
        openapi_core.Spec object for validating requests/responses
    """
    # Path to OpenAPI contract
    spec_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "specs",
        "003-backend-api-loopback",
        "contracts",
        "message-api.yaml"
    )

    # Load YAML spec
    with open(spec_path, 'r') as f:
        spec_dict = yaml.safe_load(f)

    # Create OpenAPI spec object
    return Spec.from_dict(spec_dict)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Create FastAPI TestClient for integration tests.

    Yields:
        TestClient instance for making test requests
    """
    # Import app here (not at module level) to ensure env vars are set first
    from main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_message_request() -> dict:
    """
    Sample valid message request payload.

    Returns:
        Dictionary with valid MessageRequest fields
    """
    return {
        "message": "Hello world",
        "conversationId": "conv-a1b2c3d4-5678-90ab-cdef-123456789abc",
        "timestamp": "2025-12-28T10:00:00.000Z"
    }


@pytest.fixture
def sample_message_minimal() -> dict:
    """
    Minimal valid message request (only required fields).

    Returns:
        Dictionary with only required MessageRequest fields
    """
    return {
        "message": "Test message"
    }


@pytest.fixture
def sample_message_special_chars() -> dict:
    """
    Message request with special characters, emoji, and formatting.

    Returns:
        Dictionary with special character message
    """
    return {
        "message": "Hello 🚀 World!\nNew line here.\nAnd another: special chars !@#$%^&*()"
    }
