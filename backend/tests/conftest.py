"""
Pytest configuration and shared fixtures for backend tests

Provides:
- TestClient for integration tests
- OpenAPI spec loader for contract tests
- Common test data fixtures
"""

import os
from typing import Generator

import pytest
import yaml
from fastapi.testclient import TestClient
from openapi_core import Spec

from main import app


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
        "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc",
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
