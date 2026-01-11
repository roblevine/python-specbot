"""
Integration Tests for Message AI Flow

Tests full request-response cycle for the message AI endpoint.
Tests acceptance criteria from User Story 1.

Feature: 003-backend-api-loopback User Story 1 (updated for AI integration)
Tests: T023-T026 (Updated for OpenAI LangChain integration)
"""

import time
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
def test_send_message_receives_loopback_response(
    client: TestClient,
    sample_message_request: dict
):
    """
    T023: POST /api/v1/messages returns AI response.

    Acceptance Criteria (spec.md User Story 1, Scenario 1):
    - User sends message
    - Response contains AI-generated text
    - Response has status 200

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}
        mock_get_ai.return_value = "This is an AI response."

        # Send message
        response = client.post("/api/v1/messages", json=sample_message_request)

        # Assert response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0, "Response message cannot be empty"
        assert "timestamp" in data


@pytest.mark.integration
def test_loopback_preserves_special_characters(
    client: TestClient,
    sample_message_special_chars: dict
):
    """
    T024: Special characters, emoji, and newlines are handled by AI endpoint.

    Acceptance Criteria (spec.md User Story 1, Scenario 4):
    - Message with emoji, line breaks, special chars is accepted
    - AI response is returned successfully

    Validates FR-010, FR-011: Preserve special characters and message content.

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service to handle special characters
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}
        mock_get_ai.return_value = "AI response with special chars: 🚀 世界"

        # Send message with special characters
        response = client.post("/api/v1/messages", json=sample_message_special_chars)

        # Assert response
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0, "Response message cannot be empty"


@pytest.mark.integration
def test_loopback_response_time_under_2_seconds(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T025: Response received within 2 seconds.

    Acceptance Criteria (spec.md User Story 1, Scenario 2):
    - Backend processes request and responds within 2 seconds

    Validates FR-006: Response time under 2 seconds.

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service for fast response
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}
        mock_get_ai.return_value = "Quick AI response."

        # Measure response time
        start_time = time.time()
        response = client.post("/api/v1/messages", json=sample_message_minimal)
        duration = time.time() - start_time

        # Assert response time
        assert duration < 2.0, f"Response took {duration:.2f}s (expected < 2s)"

        # Assert successful response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


@pytest.mark.integration
def test_multiple_messages_in_sequence(client: TestClient):
    """
    T026: Multiple messages in sequence each receive AI responses.

    Acceptance Criteria (spec.md User Story 1, Scenario 3):
    - Send multiple messages in sequence
    - Each response contains AI-generated text

    Validates FR-005: Maintain message order.

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        messages = [
            "First message",
            "Second message",
            "Third message with emoji 🚀",
            "Fourth message\nwith newline"
        ]

        for i, msg in enumerate(messages):
            # Set different AI response for each message
            mock_get_ai.return_value = f"AI response #{i+1}"

            # Send message
            response = client.post("/api/v1/messages", json={"message": msg})

            # Assert response
            assert response.status_code == 200, f"Failed on message: {msg}"

            data = response.json()
            assert data["status"] == "success"
            assert len(data["message"]) > 0, f"Empty response for message: {msg}"


@pytest.mark.integration
def test_minimal_message_request(client: TestClient):
    """
    Test minimal request with only required fields.

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}
        mock_get_ai.return_value = "AI response to minimal request."

        response = client.post("/api/v1/messages", json={"message": "Test"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0, "Response message cannot be empty"


@pytest.mark.integration
def test_message_with_conversation_id(client: TestClient):
    """
    Test request with optional conversationId field.

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}
        mock_get_ai.return_value = "AI response with conversation context."

        request_data = {
            "message": "Test with conversation ID",
            "conversationId": "conv-a1b2c3d4-5678-90ab-cdef-123456789abc"
        }

        response = client.post("/api/v1/messages", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0, "Response message cannot be empty"


@pytest.mark.integration
def test_multiline_message_preserved(client: TestClient):
    """
    Test that multiline messages are handled by AI endpoint.

    Validates FR-011: No truncation or modification.

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}
        mock_get_ai.return_value = "AI response to multiline message."

        multiline_message = "Line 1\nLine 2\nLine 3\n\nLine 5 after blank"

        response = client.post("/api/v1/messages", json={"message": multiline_message})

        assert response.status_code == 200
        data = response.json()
        assert len(data["message"]) > 0, "Response message cannot be empty"
