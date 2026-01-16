"""
Integration Tests for Error Handling

Tests error scenarios and validation for the message API.
Tests acceptance criteria from User Story 2.

Feature: 003-backend-api-loopback User Story 2
Tests: T052-T054 (error handling validation)
Updated for OpenAI LangChain integration.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
def test_empty_message_rejected_by_backend(client: TestClient):
    """
    T052: Empty message returns 422 error (Pydantic validation).

    Validates FR-012: Backend validates and rejects malformed requests.

    Expected: 422 Unprocessable Entity with error message
    """
    response = client.post("/api/v1/messages", json={"message": ""})

    assert response.status_code == 422
    data = response.json()
    # FastAPI returns validation errors in 'detail' field
    assert "detail" in data
    # Validation errors should be present
    assert len(data["detail"]) > 0


@pytest.mark.integration
def test_whitespace_only_message_rejected(client: TestClient):
    """
    Test whitespace-only message returns 422 error (Pydantic validation).

    Validates FR-012: Backend validates and rejects malformed requests.
    """
    # Test with spaces
    response = client.post("/api/v1/messages", json={"message": "   "})
    assert response.status_code == 422

    # Test with newlines
    response = client.post("/api/v1/messages", json={"message": "\n\n\n"})
    assert response.status_code == 422

    # Test with tabs
    response = client.post("/api/v1/messages", json={"message": "\t\t\t"})
    assert response.status_code == 422


@pytest.mark.integration
def test_too_long_message_rejected(client: TestClient):
    """
    T053: Message exceeding 10,000 characters returns 422 error (Pydantic validation).

    Validates FR-007: Reject messages > 10,000 chars.
    """
    long_message = "a" * 10001

    response = client.post("/api/v1/messages", json={"message": long_message})

    assert response.status_code == 422
    data = response.json()
    assert "status" in data or "detail" in data
    # Error should mention length or maximum
    error_text = str(data).lower()
    assert "length" in error_text or "maximum" in error_text or "long" in error_text


@pytest.mark.integration
def test_malformed_json_rejected(client: TestClient):
    """
    T054: Malformed JSON returns 422 error.

    Validates FR-012: Backend validates and rejects malformed requests.
    """
    # Send invalid JSON
    response = client.post(
        "/api/v1/messages",
        data="this is not json",
        headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_missing_message_field_rejected(client: TestClient):
    """
    Test missing required 'message' field returns 422 error.

    Validates FR-012: Backend validates and rejects malformed requests.
    """
    # Send empty JSON
    response = client.post("/api/v1/messages", json={})
    assert response.status_code == 422

    # Send JSON without message field
    response = client.post("/api/v1/messages", json={"other": "field"})
    assert response.status_code == 422


@pytest.mark.integration
def test_invalid_conversation_id_format(client: TestClient):
    """
    Test invalid UUID format for conversationId.

    Optional field should validate format if provided.
    """
    response = client.post(
        "/api/v1/messages",
        json={
            "message": "Test",
            "conversationId": "not-a-uuid"
        }
    )

    # Should be 400 or 422 (validation error)
    assert response.status_code in [400, 422]


@pytest.mark.integration
def test_error_response_structure(client: TestClient):
    """
    Test that error responses have consistent structure.

    All errors should include:
    - status: "error" (or error detail)
    - error message
    - timestamp
    """
    response = client.post("/api/v1/messages", json={"message": ""})

    assert response.status_code == 422
    data = response.json()

    # Check response structure (may be in root or in detail)
    if "status" in data:
        assert data["status"] == "error"
        assert "error" in data or "detail" in data
    else:
        # FastAPI may wrap in detail
        assert "detail" in data


@pytest.mark.integration
def test_exactly_10000_chars_accepted(client: TestClient):
    """
    Test that exactly 10,000 characters is accepted (boundary test).

    Validates FR-007: Maximum is 10,000 chars (inclusive).

    Updated for OpenAI LangChain integration.
    """
    # Mock the LLM service
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        mock_get_ai.return_value = ("AI response to 10,000 character message.", "gpt-3.5-turbo")

        message = "a" * 10000

        response = client.post("/api/v1/messages", json={"message": message})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0, "Response message cannot be empty"
