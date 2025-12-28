"""
Integration Tests for Message Loopback Flow

Tests full request-response cycle for the message loopback endpoint.
Tests acceptance criteria from User Story 1.

Feature: 003-backend-api-loopback User Story 1
Tests: T023-T026 (TDD - these should FAIL before implementation)
"""

import time
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_send_message_receives_loopback_response(
    client: TestClient,
    sample_message_request: dict
):
    """
    T023: POST /api/v1/messages returns loopback with "api says: " prefix.

    Acceptance Criteria (spec.md User Story 1, Scenario 1):
    - User sends "Hello world"
    - Response contains "api says: Hello world"
    - Response has status 200

    Expected: FAIL (endpoint not implemented yet)
    """
    # Send message
    response = client.post("/api/v1/messages", json=sample_message_request)

    # Assert response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == f"api says: {sample_message_request['message']}"
    assert "timestamp" in data


@pytest.mark.integration
def test_loopback_preserves_special_characters(
    client: TestClient,
    sample_message_special_chars: dict
):
    """
    T024: Special characters, emoji, and newlines are preserved in loopback.

    Acceptance Criteria (spec.md User Story 1, Scenario 4):
    - Message with emoji, line breaks, special chars
    - Response preserves all characters exactly

    Validates FR-010, FR-011: Preserve special characters and message content.

    Expected: FAIL (endpoint not implemented yet)
    """
    # Send message with special characters
    response = client.post("/api/v1/messages", json=sample_message_special_chars)

    # Assert response
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

    # Verify message is preserved exactly with "api says: " prefix
    expected_message = f"api says: {sample_message_special_chars['message']}"
    assert data["message"] == expected_message, (
        f"Expected: {expected_message}\n"
        f"Got: {data['message']}"
    )


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

    Expected: FAIL (endpoint not implemented yet)
    """
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
    T026: Multiple messages in sequence each receive loopback responses.

    Acceptance Criteria (spec.md User Story 1, Scenario 3):
    - Send multiple messages in sequence
    - Each response has "api says: " prefix with exact text

    Validates FR-005: Maintain message order.

    Expected: FAIL (endpoint not implemented yet)
    """
    messages = [
        "First message",
        "Second message",
        "Third message with emoji 🚀",
        "Fourth message\nwith newline"
    ]

    for msg in messages:
        # Send message
        response = client.post("/api/v1/messages", json={"message": msg})

        # Assert response
        assert response.status_code == 200, f"Failed on message: {msg}"

        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == f"api says: {msg}", (
            f"Mismatch on message: {msg}\n"
            f"Expected: api says: {msg}\n"
            f"Got: {data['message']}"
        )


@pytest.mark.integration
def test_minimal_message_request(client: TestClient):
    """
    Test minimal request with only required fields.

    Expected: FAIL (endpoint not implemented yet)
    """
    response = client.post("/api/v1/messages", json={"message": "Test"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "api says: Test"


@pytest.mark.integration
def test_message_with_conversation_id(client: TestClient):
    """
    Test request with optional conversationId field.

    Expected: FAIL (endpoint not implemented yet)
    """
    request_data = {
        "message": "Test with conversation ID",
        "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc"
    }

    response = client.post("/api/v1/messages", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "api says: Test with conversation ID"


@pytest.mark.integration
def test_multiline_message_preserved(client: TestClient):
    """
    Test that multiline messages are preserved exactly.

    Validates FR-011: No truncation or modification.

    Expected: FAIL (endpoint not implemented yet)
    """
    multiline_message = "Line 1\nLine 2\nLine 3\n\nLine 5 after blank"

    response = client.post("/api/v1/messages", json={"message": multiline_message})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"api says: {multiline_message}"
