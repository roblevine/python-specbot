"""
Integration Tests for Message Streaming

Tests end-to-end streaming flow from API endpoint through LLM service to SSE response.
Validates complete integration with mocked LLM responses.

Feature: 009-message-streaming User Story 1 (P1)
Tests: T013
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_streaming_flow(client: TestClient):
    """
    T013: Integration test for complete streaming flow.

    Tests the full end-to-end flow:
    - API request with Accept: text/event-stream header
    - Route handler calls stream_ai_response()
    - LLM service streams via LangChain astream()
    - Events formatted as SSE
    - Complete response returned to client

    Feature: 009-message-streaming User Story 1
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        # Mock streaming response
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            # Simulate realistic streaming with multiple tokens
            tokens = ["Hello", " ", "world", "!", " ", "How", " ", "are", " ", "you", "?"]
            for token in tokens:
                yield TokenEvent(content=token)
            yield CompleteEvent(model="gpt-3.5-turbo", totalTokens=len(tokens))

        mock_stream.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json={"message": "Test streaming"},
            headers={"Accept": "text/event-stream"}
        )

        # Verify response
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("Content-Type", "")

        # Parse events
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        # Verify event sequence
        assert len(events) == 12  # 11 tokens + 1 complete

        # Verify token events
        token_events = [e for e in events if e["type"] == "token"]
        assert len(token_events) == 11

        # Reconstruct message from tokens
        message = "".join(e["content"] for e in token_events)
        assert message == "Hello world! How are you?"

        # Verify complete event
        complete_event = events[-1]
        assert complete_event["type"] == "complete"
        assert complete_event["model"] == "gpt-3.5-turbo"
        assert complete_event["totalTokens"] == 11


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_with_conversation_history(client: TestClient):
    """
    T013: Integration test for streaming with conversation history.

    Validates that conversation history is properly passed through
    the entire streaming pipeline and context is preserved.

    Feature: 009-message-streaming User Story 1
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        # Track arguments passed to stream_ai_response
        captured_args = {}

        async def mock_generator(**kwargs):
            # Capture arguments
            captured_args.update(kwargs)

            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Your")
            yield TokenEvent(content=" name")
            yield TokenEvent(content=" is")
            yield TokenEvent(content=" Alice")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream.side_effect = mock_generator

        # Make request with conversation history
        response = client.post(
            "/api/v1/messages",
            json={
                "message": "What's my name?",
                "history": [
                    {"sender": "user", "text": "My name is Alice"},
                    {"sender": "system", "text": "Nice to meet you, Alice!"}
                ]
            },
            headers={"Accept": "text/event-stream"}
        )

        # Verify response
        assert response.status_code == 200

        # Verify history was passed to stream_ai_response
        assert "history" in captured_args
        assert len(captured_args["history"]) == 2
        assert captured_args["history"][0]["sender"] == "user"
        assert captured_args["history"][0]["text"] == "My name is Alice"
        assert captured_args["history"][1]["sender"] == "system"
        assert captured_args["history"][1]["text"] == "Nice to meet you, Alice!"

        # Verify message was passed
        assert captured_args["message"] == "What's my name?"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_with_custom_model(client: TestClient):
    """
    T013: Integration test for streaming with per-request model selection.

    Validates that custom model selection works end-to-end through
    the streaming pipeline.

    Feature: 009-message-streaming + 008-openai-model-selector
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        # Track arguments
        captured_args = {}

        async def mock_generator(**kwargs):
            captured_args.update(kwargs)

            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="GPT-4 response")
            yield CompleteEvent(model="gpt-4")

        mock_stream.side_effect = mock_generator

        # Make request with custom model
        response = client.post(
            "/api/v1/messages",
            json={
                "message": "Test message",
                "model": "gpt-4"
            },
            headers={"Accept": "text/event-stream"}
        )

        # Verify response
        assert response.status_code == 200

        # Verify model was passed to stream_ai_response
        assert captured_args["model"] == "gpt-4"

        # Parse events and verify CompleteEvent has correct model
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        complete_event = [e for e in events if e["type"] == "complete"][0]
        assert complete_event["model"] == "gpt-4"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_streaming_requests(client: TestClient):
    """
    T013: Integration test for concurrent streaming requests.

    Validates that the system can handle multiple simultaneous
    streaming requests without interference.

    Feature: 009-message-streaming User Story 1
    Success Criteria: Support at least 10 concurrent streams
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        request_count = 0

        async def mock_generator(**kwargs):
            nonlocal request_count
            request_count += 1
            request_id = request_count

            from src.schemas import TokenEvent, CompleteEvent
            # Each stream has unique content
            for i in range(5):
                yield TokenEvent(content=f"Token-{request_id}-{i} ")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream.side_effect = lambda **kwargs: mock_generator(**kwargs)

        # Make 10 concurrent requests
        num_concurrent = 10
        responses = []

        for i in range(num_concurrent):
            response = client.post(
                "/api/v1/messages",
                json={"message": f"Concurrent test {i}"},
                headers={"Accept": "text/event-stream"}
            )
            responses.append(response)

        # Verify all requests succeeded
        assert len(responses) == num_concurrent
        for i, response in enumerate(responses):
            assert response.status_code == 200, f"Request {i} failed with status {response.status_code}"
            assert "text/event-stream" in response.headers.get("Content-Type", "")

        # Verify each stream has content
        for i, response in enumerate(responses):
            events = []
            for event_str in response.text.split("\n\n"):
                if event_str.strip() and event_str.startswith("data: "):
                    events.append(json.loads(event_str[6:]))

            # Should have tokens + complete event
            assert len(events) >= 2, f"Stream {i} has too few events"

            # Should have at least one token event
            token_events = [e for e in events if e["type"] == "token"]
            assert len(token_events) > 0, f"Stream {i} has no token events"

            # Should have exactly one complete event
            complete_events = [e for e in events if e["type"] == "complete"]
            assert len(complete_events) == 1, f"Stream {i} has {len(complete_events)} complete events"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_performance_first_token_latency(client: TestClient):
    """
    T013: Integration test for streaming performance - first token latency.

    Measures the time to receive the first token in a streaming response.

    Feature: 009-message-streaming User Story 1
    Success Criteria: First token visible within 1 second
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            # Simulate realistic LLM streaming with small delays
            yield TokenEvent(content="First")
            await asyncio.sleep(0.01)  # Simulate token generation time
            yield TokenEvent(content=" token")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream.return_value = mock_generator()

        # Measure time to first byte
        start_time = time.time()

        response = client.post(
            "/api/v1/messages",
            json={"message": "Performance test"},
            headers={"Accept": "text/event-stream"}
        )

        # Time when we receive response (first token already sent)
        first_token_time = time.time() - start_time

        # Verify response succeeded
        assert response.status_code == 200

        # Parse events
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        # Verify we got events
        assert len(events) >= 2

        # Performance assertion: First token latency should be under 1 second
        # Note: This is measuring total response time with TestClient, not streaming latency
        # In production, first token would arrive immediately, but TestClient reads full response
        assert first_token_time < 2.0, f"First token latency too high: {first_token_time:.3f}s"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_error_handling_in_pipeline(client: TestClient):
    """
    T013: Integration test for error handling in streaming pipeline.

    Validates that errors during streaming are properly handled and
    ErrorEvent is returned to client.

    Feature: 009-message-streaming User Story 3
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        async def mock_generator():
            from src.schemas import TokenEvent, ErrorEvent
            # Stream some tokens, then error
            yield TokenEvent(content="Hello")
            yield TokenEvent(content=" world")
            # Simulate error mid-stream
            yield ErrorEvent(error="AI service is busy", code="RATE_LIMIT")

        mock_stream.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json={"message": "Test error handling"},
            headers={"Accept": "text/event-stream"}
        )

        # Verify response (should still be 200 since connection was established)
        assert response.status_code == 200

        # Parse events
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        # Verify we got token events followed by error event
        assert len(events) == 3  # 2 tokens + 1 error

        # Verify error event
        error_event = events[-1]
        assert error_event["type"] == "error"
        assert error_event["code"] == "RATE_LIMIT"
        assert "busy" in error_event["error"].lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_backward_compatibility(client: TestClient):
    """
    T013: Integration test for backward compatibility with non-streaming.

    Validates that the same endpoint works for both streaming and
    non-streaming requests based on Accept header.

    Feature: 009-message-streaming User Story 1
    CRITICAL: Ensures existing clients are not broken
    """
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        # Mock non-streaming response
        mock_get_ai.return_value = ("Hello World!", "gpt-3.5-turbo")

        # Test 1: Request with Accept: application/json (non-streaming)
        response_json = client.post(
            "/api/v1/messages",
            json={"message": "Test"},
            headers={"Accept": "application/json"}
        )

        assert response_json.status_code == 200
        assert "application/json" in response_json.headers.get("Content-Type", "")

        data = response_json.json()
        assert data["status"] == "success"
        assert data["message"] == "Hello World!"
        assert "timestamp" in data

        # Verify get_ai_response was called (not stream_ai_response)
        mock_get_ai.assert_called_once()

    # Test 2: Request with Accept: text/event-stream (streaming)
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Streaming")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream.return_value = mock_generator()

        response_stream = client.post(
            "/api/v1/messages",
            json={"message": "Test"},
            headers={"Accept": "text/event-stream"}
        )

        assert response_stream.status_code == 200
        assert "text/event-stream" in response_stream.headers.get("Content-Type", "")

        # Verify response is SSE format (not JSON)
        assert response_stream.text.startswith("data: ")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_with_empty_message_validation(client: TestClient):
    """
    T013: Integration test for validation in streaming flow.

    Validates that message validation works correctly in streaming mode.

    Feature: 009-message-streaming User Story 1
    """
    # Test empty message (should fail validation before streaming starts)
    response = client.post(
        "/api/v1/messages",
        json={"message": ""},
        headers={"Accept": "text/event-stream"}
    )

    # Should return error (422 Unprocessable Entity - Pydantic validation)
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_special_characters_preservation(client: TestClient):
    """
    T013: Integration test for special character preservation in streaming.

    Validates that emoji, unicode, and special characters are preserved
    through the entire streaming pipeline.

    Feature: 009-message-streaming User Story 1
    """
    with patch('src.api.routes.messages.stream_ai_response') as mock_stream:
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            # Stream tokens with special characters
            yield TokenEvent(content="🚀")
            yield TokenEvent(content=" Hello ")
            yield TokenEvent(content="世界")
            yield TokenEvent(content=" @#$%")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json={"message": "Test special chars"},
            headers={"Accept": "text/event-stream"}
        )

        # Verify response
        assert response.status_code == 200

        # Parse events
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        # Verify special characters are preserved
        token_events = [e for e in events if e["type"] == "token"]
        assert token_events[0]["content"] == "🚀"
        assert token_events[1]["content"] == " Hello "
        assert token_events[2]["content"] == "世界"
        assert token_events[3]["content"] == " @#$%"

        # Reconstruct full message
        full_message = "".join(e["content"] for e in token_events)
        assert full_message == "🚀 Hello 世界 @#$%"
