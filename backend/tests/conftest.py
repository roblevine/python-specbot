"""
Pytest configuration and shared fixtures for backend tests

Provides:
- TestClient for integration tests
- OpenAPI spec loader for contract tests
- Common test data fixtures
- LLM mocks for streaming tests (Feature 005)
"""

import os
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

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


# ============================================================================
# LLM Streaming Fixtures (Feature 005 - T012)
# ============================================================================


@pytest.fixture
def sample_chat_stream_request() -> dict:
    """
    Sample valid chat stream request payload.

    Returns:
        Dictionary with valid ChatStreamRequest fields
    """
    return {
        "message": "Hello, how are you?",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "conversationHistory": [],
        "model": "gpt-5"
    }


@pytest.fixture
def sample_chat_stream_request_with_history() -> dict:
    """
    Chat stream request with conversation history.

    Returns:
        Dictionary with ChatStreamRequest including history
    """
    return {
        "message": "What was my previous question?",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "conversationHistory": [
            {
                "role": "user",
                "content": "Tell me about Python"
            },
            {
                "role": "assistant",
                "content": "Python is a high-level programming language..."
            }
        ],
        "model": "gpt-5"
    }


@pytest.fixture
def mock_llm_service():
    """
    Mock LLMService for testing streaming without real API calls.

    Returns:
        Mock LLMService instance with async generator
    """
    mock_service = MagicMock()

    # Mock stream_chat_response as async generator
    async def mock_stream():
        """Mock streaming response"""
        yield 'event: message\ndata: {"type": "start", "messageId": "msg-test-123"}\n\n'
        yield 'event: message\ndata: {"type": "chunk", "content": "Hello"}\n\n'
        yield 'event: message\ndata: {"type": "chunk", "content": " world"}\n\n'
        yield 'event: message\ndata: {"type": "done", "messageId": "msg-test-123", "model": "gpt-5"}\n\n'

    mock_service.stream_chat_response = AsyncMock(return_value=mock_stream())
    return mock_service


@pytest.fixture
def mock_llm_error():
    """
    Mock LLMService that raises an error for testing error handling.

    Returns:
        Mock LLMService instance that raises exceptions
    """
    mock_service = MagicMock()

    async def mock_error_stream():
        """Mock error during streaming"""
        yield 'event: message\ndata: {"type": "start", "messageId": "msg-test-456"}\n\n'
        raise Exception("Mock LLM API error")

    mock_service.stream_chat_response = AsyncMock(return_value=mock_error_stream())
    return mock_service


@pytest.fixture
def chat_openapi_spec() -> Spec:
    """
    Load Chat Streaming API OpenAPI specification for contract testing.

    Returns:
        openapi_core.Spec object for validating chat streaming requests/responses
    """
    spec_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "specs",
        "005-llm-integration",
        "contracts",
        "chat-streaming-api.yaml"
    )

    # Load YAML spec
    with open(spec_path, 'r') as f:
        spec_dict = yaml.safe_load(f)

    # Create OpenAPI spec object
    return Spec.from_dict(spec_dict)
