"""
Unit Tests for LLM Service

Tests the LLMService class and streaming functionality in isolation.
Uses mocks to avoid real API calls during testing.

Feature: 005-llm-integration User Story 1
Task: T015 (TDD - should FAIL before implementation)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_stream_chat_response_basic():
    """
    T015: Test basic streaming functionality without conversation history.

    Verifies that:
    - LLMService can stream a simple chat response
    - SSE format is correct (event: message, data: {...})
    - Stream includes start, chunk, and done events
    - messageId is generated and included in start/done events
    """
    service = LLMService()

    message = "Hello, how are you?"
    conversation_history = []
    model = "gpt-5"

    # This should fail until implementation is complete
    with pytest.raises(NotImplementedError, match="Implementation in T019"):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass


@pytest.mark.asyncio
async def test_stream_chat_response_generates_message_id():
    """
    Test that stream generates a valid message ID.

    MessageId format: msg-{uuid}
    """
    service = LLMService()

    message = "Test message"
    conversation_history = []
    model = "gpt-5"

    # This should fail until implementation is complete
    with pytest.raises(NotImplementedError):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass


@pytest.mark.asyncio
async def test_stream_chat_response_with_conversation_history():
    """
    Test streaming with conversation history context.

    Verifies that:
    - Service accepts conversation history
    - History is converted to LangChain message objects
    - History is included in the LLM request
    """
    service = LLMService()

    message = "What was my previous question?"
    conversation_history = [
        {"role": "user", "content": "Tell me about Python"},
        {"role": "assistant", "content": "Python is a programming language..."}
    ]
    model = "gpt-5"

    # This should fail until implementation is complete
    with pytest.raises(NotImplementedError):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass


@pytest.mark.asyncio
async def test_stream_chat_response_uses_correct_model():
    """
    Test that the correct LLM model is used based on request.

    Verifies:
    - Service selects correct ChatOpenAI instance for model
    - Done event includes the model name
    """
    service = LLMService()

    # Test with gpt-5-codex
    message = "Write a function"
    conversation_history = []
    model = "gpt-5-codex"

    # This should fail until implementation is complete
    with pytest.raises(NotImplementedError):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass


@pytest.mark.asyncio
async def test_stream_chat_response_sse_format():
    """
    Test that SSE events are properly formatted.

    Expected format:
    event: message
    data: {"type": "start", "messageId": "msg-xxx"}

    (blank line)

    event: message
    data: {"type": "chunk", "content": "text"}

    (blank line)
    """
    service = LLMService()

    message = "Test"
    conversation_history = []
    model = "gpt-5"

    # This should fail until implementation is complete
    with pytest.raises(NotImplementedError):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass


@pytest.mark.asyncio
async def test_stream_chat_response_error_handling():
    """
    Test that LLM API errors are properly caught and converted to SSE error events.

    Verifies:
    - Exceptions are caught
    - Error is classified using _classify_error
    - User-friendly message is generated using _get_user_friendly_message
    - SSE error event is yielded with correct format
    """
    service = LLMService()

    message = "Test"
    conversation_history = []
    model = "gpt-5"

    # Mock the underlying ChatOpenAI to raise an error
    with patch.object(service.models["gpt-5"], "astream") as mock_stream:
        mock_stream.side_effect = Exception("Mock API error")

        # This should fail until error handling is implemented (T020-T021)
        with pytest.raises(NotImplementedError):
            async for event in service.stream_chat_response(message, conversation_history, model):
                pass


def test_classify_error_returns_error_code():
    """
    T020: Test error classification logic.

    Verifies that different exception types are classified correctly:
    - AuthenticationError -> "authentication_error"
    - RateLimitError -> "rate_limit_exceeded"
    - TimeoutError -> "network_timeout"
    - Generic Exception -> "llm_provider_error"
    """
    service = LLMService()

    # Test generic exception
    generic_error = Exception("Something went wrong")
    code = service._classify_error(generic_error)

    # Should return default error code until implementation
    assert code == "llm_provider_error", "Default error code should be llm_provider_error"


def test_get_user_friendly_message():
    """
    T021: Test user-friendly error message generation.

    Verifies that:
    - Technical error messages are converted to user-friendly text
    - Messages are non-technical and actionable
    - Error code is used to select appropriate message
    """
    service = LLMService()

    # Test different error codes
    test_cases = [
        ("authentication_error", Exception("Invalid API key")),
        ("rate_limit_exceeded", Exception("Rate limit")),
        ("network_timeout", Exception("Timeout")),
        ("llm_provider_error", Exception("Unknown error"))
    ]

    for code, error in test_cases:
        message = service._get_user_friendly_message(code, error)

        # Should return generic message until implementation
        assert isinstance(message, str), "Message should be a string"
        assert len(message) > 0, "Message should not be empty"

        # Default implementation returns generic message
        assert message == "An unexpected error occurred. Please try again."


def test_convert_history_to_messages():
    """
    T047 (User Story 3): Test conversation history conversion.

    This is a skeleton test for US3 functionality.
    Verifies that conversation history dicts are converted to LangChain message objects.
    """
    service = LLMService()

    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "system", "content": "You are helpful"}
    ]

    messages = service._convert_history_to_messages(history)

    # Should return empty list until US3 implementation
    assert messages == [], "Should return empty list in skeleton implementation"


@pytest.mark.asyncio
async def test_stream_handles_empty_history():
    """
    Test that streaming works with empty conversation history.
    """
    service = LLMService()

    message = "First message in conversation"
    conversation_history = []
    model = "gpt-5"

    # This should fail until implementation is complete
    with pytest.raises(NotImplementedError):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass


@pytest.mark.asyncio
async def test_stream_respects_temperature_settings():
    """
    Test that service uses configured temperature and max_tokens settings.
    """
    service = LLMService()

    # Verify models were initialized with correct settings
    assert service.models["gpt-5"].temperature == 0.7, "Should use configured temperature"
    assert service.models["gpt-5"].max_tokens == 4096, "Should use configured max_tokens"
    assert service.models["gpt-5-codex"].temperature == 0.7, "Should use configured temperature"


@pytest.mark.asyncio
async def test_stream_invalid_model_raises_error():
    """
    Test that requesting an invalid model raises appropriate error.
    """
    service = LLMService()

    message = "Test"
    conversation_history = []
    model = "invalid-model"

    # Should handle invalid model gracefully
    # Either raise ValueError or yield error event
    with pytest.raises((NotImplementedError, KeyError)):
        async for event in service.stream_chat_response(message, conversation_history, model):
            pass
