"""
Integration Tests for OpenAI Integration

Tests full OpenAI integration flow with mocked external API responses.
Validates that the LLM service correctly integrates with ChatOpenAI.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Tests: T005 (TDD - these should FAIL before implementation)
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_llm_service_initializes_on_startup():
    """
    T005: Integration test for LLM service initialization.

    Validates that the LLM service properly initializes during
    application startup with environment configuration.

    Expected: FAIL (service not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_llm_instance

    # Clear cached instance before test
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-integration-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance

            # Get LLM instance
            llm = get_llm_instance()

            # Verify initialization
            assert llm is not None
            mock_chat.assert_called_once()

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_api_response_mocking():
    """
    T005: Integration test with mocked OpenAI API response.

    Validates that the service correctly processes mocked AI responses
    from ChatOpenAI.ainvoke().

    Expected: FAIL (service not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_llm_instance

    # Clear cached instance before test
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Create mock LLM instance with async ainvoke
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock the ainvoke method to return a response
            mock_response = Mock()
            mock_response.content = "Hello! I'm doing well, thank you for asking."
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Get LLM instance and invoke
            llm = get_llm_instance()
            result = await llm.ainvoke("Hello, how are you?")

            # Verify response
            assert result.content == "Hello! I'm doing well, thank you for asking."
            mock_llm.ainvoke.assert_called_once()

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_service_handles_message_conversion():
    """
    T005: Integration test for message format conversion.

    Validates that user messages are converted to LangChain format
    before being sent to ChatOpenAI.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import convert_to_langchain_messages

    # Test simple message conversion
    user_message = "Hello, how are you?"
    langchain_messages = convert_to_langchain_messages(user_message)

    # Verify format (LangChain expects list of messages)
    assert isinstance(langchain_messages, list)
    assert len(langchain_messages) > 0


@pytest.mark.integration
def test_llm_config_loaded_from_environment():
    """
    T005: Integration test for environment-based configuration.

    Validates that the service loads configuration from environment
    variables in a realistic scenario.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'sk-integration-test-key-12345',
        'OPENAI_MODEL': 'gpt-4'
    }):
        config = load_config()

        assert config['api_key'] == 'sk-integration-test-key-12345'
        assert config['model'] == 'gpt-4'


@pytest.mark.integration
def test_llm_service_error_on_missing_config():
    """
    T005: Integration test for missing configuration error handling.

    Validates that appropriate errors are raised when required
    configuration is missing.

    Expected: FAIL (service not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_llm_instance

    # Clear cached instance before test
    llm_service._llm_instance = None

    # Clear environment
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            get_llm_instance()

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_response_preserves_special_characters():
    """
    T005: Integration test verifying special character handling.

    Validates that emoji, unicode, and special characters are
    preserved through the LLM service layer.

    Expected: FAIL (service not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_llm_instance

    # Clear cached instance before test
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock response with special characters
            mock_response = Mock()
            mock_response.content = "🚀 means rocket! Unicode: 世界"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Invoke with special characters
            llm = get_llm_instance()
            result = await llm.ainvoke("What does 🚀 mean?")

            # Verify special characters preserved
            assert "🚀" in result.content
            assert "世界" in result.content

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_single_message_ai_response_flow():
    """
    T011: Integration test for complete AI response flow.

    Validates that a single user message flows through the entire system:
    - Message is converted to LangChain format
    - LLM service processes the message
    - AI response is returned (no loopback prefix)
    - Response content matches mocked AI output

    Feature: 006-openai-langchain-chat User Story 1
    Expected: FAIL (get_ai_response not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-integration-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM with realistic AI response
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock realistic AI response
            mock_response = Mock()
            mock_response.content = "Hello! I'm an AI assistant. How can I help you today?"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Process message through AI service
            user_message = "Hello, how are you?"
            ai_response = await get_ai_response(user_message)

            # Verify AI response
            assert ai_response == "Hello! I'm an AI assistant. How can I help you today?"
            assert not ai_response.startswith("api says: "), \
                "AI response should not have loopback prefix"

            # Verify LLM was invoked
            mock_llm.ainvoke.assert_called_once()

            # Verify message was passed to LLM (check the call arguments)
            call_args = mock_llm.ainvoke.call_args
            assert call_args is not None, "LLM ainvoke should have been called with arguments"

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_no_sensitive_data_in_error_responses():
    """
    T033: Integration test verifying no sensitive data in error responses.

    Validates that LLM errors are sanitized and don't expose:
    - API keys
    - Raw exception messages
    - Stack traces
    - Internal implementation details

    Feature: 006-openai-langchain-chat User Story 3
    """
    from fastapi.testclient import TestClient
    from main import app
    from src.services.llm_service import (
        LLMAuthenticationError,
        LLMRateLimitError,
        LLMConnectionError
    )

    client = TestClient(app)

    # Test scenarios that should NOT expose sensitive data
    error_scenarios = [
        (LLMAuthenticationError("AI service configuration error"),
         "authentication error should be sanitized"),
        (LLMRateLimitError("AI service is busy"),
         "rate limit error should be sanitized"),
        (LLMConnectionError("Unable to reach AI service"),
         "connection error should be sanitized"),
    ]

    for error_exception, description in error_scenarios:
        with patch('src.api.routes.messages.load_config') as mock_load_config, \
             patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

            # Mock config
            mock_load_config.return_value = {
                'api_key': 'sk-secret-test-key-12345',
                'model': 'gpt-3.5-turbo'
            }

            # Mock get_ai_response to raise the error
            mock_get_ai.side_effect = error_exception

            # Make request
            response = client.post(
                "/api/v1/messages",
                json={"message": "Test message"}
            )

            # Verify error response exists
            assert response.status_code in [400, 503, 504], \
                f"Expected error status code, got {response.status_code}"

            data = response.json()
            # Error fields should be at top level, not wrapped in "detail"
            assert "error" in data, f"Error response must include 'error' field at top level. Got: {data}"
            assert "status" in data, f"Error response must include 'status' field. Got: {data}"
            assert data["status"] == "error", f"Status should be 'error'. Got: {data['status']}"

            error_msg = data["error"].lower()

            # CRITICAL: Must NOT expose API keys
            assert "sk-" not in data["error"], \
                f"Error must not expose API keys: {description}"

            # CRITICAL: Must NOT expose organization IDs
            assert "org-" not in data["error"], \
                f"Error must not expose org IDs: {description}"

            # CRITICAL: Must NOT expose raw URLs
            assert "https://" not in error_msg, \
                f"Error must not expose API URLs: {description}"

            # CRITICAL: Must NOT expose raw exception messages
            assert "exception" not in error_msg, \
                f"Error must not expose raw exceptions: {description}"

            # Verify message is user-friendly (not technical)
            assert any(word in error_msg for word in [
                "service", "unavailable", "error", "busy", "configuration", "timeout"
            ]), f"Error message should be user-friendly: {data['error']}"
