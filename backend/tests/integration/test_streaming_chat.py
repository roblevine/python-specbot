"""
Integration Tests for Streaming Chat Flow

Tests full request-response cycle for the streaming chat endpoint.
Tests acceptance criteria from User Story 1.

Feature: 005-llm-integration User Story 1
Task: T017 (TDD - should FAIL before implementation)
"""

import pytest
import json
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_stream_chat_returns_sse_response(
    client: TestClient,
    sample_chat_stream_request: dict
):
    """
    T017: POST /api/v1/chat/stream returns Server-Sent Events stream.

    Acceptance Criteria (spec.md User Story 1, Scenario 1):
    - User sends message
    - Response has status 200
    - Response content-type is text/event-stream
    - Stream contains start, chunk, and done events

    Expected: FAIL (endpoint returns 501 until implementation)
    """
    # Send streaming request
    response = client.post(
        "/api/v1/chat/stream",
        json=sample_chat_stream_request
    )

    # Should return 200 (not 501) when implemented
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. "
        f"Endpoint should stream, not return 501."
    )

    # Verify content type is SSE
    content_type = response.headers.get('content-type', '')
    assert 'text/event-stream' in content_type, (
        f"Expected content-type 'text/event-stream', got '{content_type}'"
    )


@pytest.mark.integration
def test_stream_contains_start_chunk_done_events(
    client: TestClient,
    sample_chat_stream_request: dict
):
    """
    Test that stream contains all required event types.

    Verifies:
    - Start event with messageId
    - At least one chunk event with content
    - Done event with messageId and model
    """
    response = client.post(
        "/api/v1/chat/stream",
        json=sample_chat_stream_request
    )

    # Parse SSE stream
    events = parse_sse_stream(response.text)

    # Should have at least 3 events: start, chunk(s), done
    assert len(events) >= 3, f"Expected at least 3 events, got {len(events)}"

    # First event should be start
    first_event = events[0]
    assert first_event['type'] == 'start', f"First event should be 'start', got {first_event['type']}"
    assert 'messageId' in first_event, "Start event should include messageId"
    assert first_event['messageId'].startswith('msg-'), "MessageId should have msg- prefix"

    # Middle events should be chunks
    chunk_events = [e for e in events if e['type'] == 'chunk']
    assert len(chunk_events) > 0, "Should have at least one chunk event"
    for chunk in chunk_events:
        assert 'content' in chunk, "Chunk event should have content"
        assert isinstance(chunk['content'], str), "Chunk content should be string"

    # Last event should be done
    last_event = events[-1]
    assert last_event['type'] == 'done', f"Last event should be 'done', got {last_event['type']}"
    assert 'messageId' in last_event, "Done event should include messageId"
    assert 'model' in last_event, "Done event should include model"
    assert last_event['model'] == sample_chat_stream_request['model'], \
        f"Done event model should match request model"


@pytest.mark.integration
def test_stream_uses_correct_model(
    client: TestClient
):
    """
    Test that stream uses the model specified in request.

    Verifies:
    - Done event includes correct model name
    - Different models can be selected
    """
    # Test with gpt-5
    request_gpt5 = {
        "message": "Test with GPT-5",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "model": "gpt-5"
    }

    response = client.post("/api/v1/chat/stream", json=request_gpt5)
    events = parse_sse_stream(response.text)
    done_event = events[-1]

    assert done_event['model'] == 'gpt-5', "Should use gpt-5 model"

    # Test with gpt-5-codex
    request_codex = {
        "message": "Test with Codex",
        "conversationId": "conv-987fcdeb-51a2-43f7-8d9c-123456789abc",
        "model": "gpt-5-codex"
    }

    response = client.post("/api/v1/chat/stream", json=request_codex)
    events = parse_sse_stream(response.text)
    done_event = events[-1]

    assert done_event['model'] == 'gpt-5-codex', "Should use gpt-5-codex model"


@pytest.mark.integration
def test_stream_with_conversation_history(
    client: TestClient,
    sample_chat_stream_request_with_history: dict
):
    """
    Test streaming with conversation history context.

    Verifies:
    - Request with history is accepted
    - Stream completes successfully
    - History is used for context (verified by response relevance in manual testing)
    """
    response = client.post(
        "/api/v1/chat/stream",
        json=sample_chat_stream_request_with_history
    )

    assert response.status_code == 200, "Should accept request with history"

    events = parse_sse_stream(response.text)

    # Should complete successfully
    assert len(events) >= 3, "Should return complete stream"
    assert events[-1]['type'] == 'done', "Should complete with done event"


@pytest.mark.integration
def test_stream_generates_unique_message_ids(
    client: TestClient
):
    """
    Test that each stream generates a unique messageId.

    Verifies:
    - MessageId in start and done events match
    - Different streams get different messageIds
    """
    request1 = {
        "message": "First message",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000"
    }

    response1 = client.post("/api/v1/chat/stream", json=request1)
    events1 = parse_sse_stream(response1.text)

    message_id_1_start = events1[0]['messageId']
    message_id_1_done = events1[-1]['messageId']

    assert message_id_1_start == message_id_1_done, "Start and done messageId should match"

    # Second request
    request2 = {
        "message": "Second message",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000"
    }

    response2 = client.post("/api/v1/chat/stream", json=request2)
    events2 = parse_sse_stream(response2.text)

    message_id_2_start = events2[0]['messageId']

    assert message_id_1_start != message_id_2_start, "Different streams should have different messageIds"


@pytest.mark.integration
def test_stream_error_handling(
    client: TestClient
):
    """
    Test that stream handles errors gracefully.

    Verifies:
    - Invalid requests return 400/422 errors
    - Errors are in JSON format (not SSE for validation errors)
    - Error messages are user-friendly
    """
    # Empty message - should return 422 validation error
    invalid_request = {
        "message": "",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000"
    }

    response = client.post("/api/v1/chat/stream", json=invalid_request)

    assert response.status_code == 422, f"Empty message should return 422, got {response.status_code}"

    data = response.json()
    assert data['status'] == 'error', "Error response should have status='error'"
    assert 'error' in data, "Error response should have error message"


@pytest.mark.integration
def test_stream_invalid_conversation_id_format(
    client: TestClient
):
    """
    Test that invalid conversationId format is rejected.

    Verifies:
    - Invalid UUID format returns 422
    - Missing conv- prefix returns 422
    """
    invalid_request = {
        "message": "Test",
        "conversationId": "invalid-id"
    }

    response = client.post("/api/v1/chat/stream", json=invalid_request)

    assert response.status_code == 422, "Invalid conversationId should return 422"


@pytest.mark.integration
def test_stream_invalid_model_rejected(
    client: TestClient
):
    """
    Test that invalid model name is rejected.

    Verifies:
    - Model not in enum (gpt-5, gpt-5-codex) returns 422
    """
    invalid_request = {
        "message": "Test",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "model": "gpt-4"
    }

    response = client.post("/api/v1/chat/stream", json=invalid_request)

    assert response.status_code == 422, "Invalid model should return 422"


@pytest.mark.integration
def test_stream_first_chunk_arrives_quickly(
    client: TestClient,
    sample_chat_stream_request: dict
):
    """
    Test that first chunk arrives quickly (Success Criteria SC-001).

    Success Criteria: First word appears within 3 seconds

    This is a basic test - actual timing will be verified in E2E tests.
    """
    response = client.post(
        "/api/v1/chat/stream",
        json=sample_chat_stream_request
    )

    # For now, just verify we get a stream
    assert response.status_code == 200

    events = parse_sse_stream(response.text)

    # Should have at least start and one chunk
    assert len(events) >= 2, "Should have start and at least one chunk"


# Helper function to parse SSE stream
def parse_sse_stream(stream_text: str) -> list:
    """
    Parse Server-Sent Events stream into list of event objects.

    Args:
        stream_text: Raw SSE text from response

    Returns:
        List of parsed event dictionaries
    """
    events = []
    current_event = {}
    current_data = []

    for line in stream_text.split('\n'):
        line = line.strip()

        if not line:
            # Blank line = end of event
            if current_event and current_data:
                # Join multi-line data and parse JSON
                data_str = '\n'.join(current_data)
                try:
                    event_data = json.loads(data_str)
                    events.append(event_data)
                except json.JSONDecodeError:
                    pass  # Skip malformed events

                current_event = {}
                current_data = []
            continue

        if line.startswith('event:'):
            current_event['event'] = line.split(':', 1)[1].strip()
        elif line.startswith('data:'):
            data_line = line.split(':', 1)[1].strip()
            current_data.append(data_line)

    return events
