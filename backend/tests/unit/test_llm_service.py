"""
Unit Tests for LLM Service

Tests LLM service initialization, configuration, and core functionality in isolation.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Tests: T004 (TDD - these should FAIL before implementation)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock


@pytest.mark.unit
def test_chatgpt_initialization_with_api_key():
    """
    T004: Unit test for ChatOpenAI initialization with valid API key.

    Validates that the LLM service properly initializes ChatOpenAI
    with the provided API key and model configuration.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import initialize_llm

    with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
        mock_instance = Mock()
        mock_chat.return_value = mock_instance

        # Initialize with explicit config
        llm = initialize_llm(api_key="test-key", model="gpt-3.5-turbo")

        # Verify ChatOpenAI was called with correct params
        mock_chat.assert_called_once_with(
            api_key="test-key",
            model="gpt-3.5-turbo"
        )
        assert llm == mock_instance


@pytest.mark.unit
def test_config_loading_from_environment():
    """
    T004: Unit test for loading configuration from environment variables.

    Validates that the service loads OPENAI_API_KEY and OPENAI_MODEL
    from environment variables.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    # Mock environment variables
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'env-test-key',
        'OPENAI_MODEL': 'gpt-4'
    }):
        config = load_config()

        assert config['api_key'] == 'env-test-key'
        assert config['model'] == 'gpt-4'


@pytest.mark.unit
def test_config_loading_with_default_model():
    """
    T004: Unit test for default model when OPENAI_MODEL not set.

    Validates that gpt-3.5-turbo is used as default when OPENAI_MODEL
    is not provided in environment.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    # Mock environment with only API key (no model)
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key'
    }, clear=True):
        config = load_config()

        assert config['api_key'] == 'test-key'
        assert config['model'] == 'gpt-3.5-turbo'  # Default


@pytest.mark.unit
def test_config_loading_missing_api_key():
    """
    T004: Unit test for error handling when API key is missing.

    Validates that appropriate error is raised when OPENAI_API_KEY
    is not configured.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config

    # Mock environment without API key
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            load_config()


@pytest.mark.unit
def test_llm_service_singleton_pattern():
    """
    T004: Unit test for LLM service singleton/caching behavior.

    Validates that the LLM instance is reused rather than recreated
    on every call (performance optimization).

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
            mock_instance = Mock()
            mock_chat.return_value = mock_instance

            # Call twice
            llm1 = get_llm_instance()
            llm2 = get_llm_instance()

            # Should only initialize once
            assert mock_chat.call_count == 1
            assert llm1 is llm2

    # Clean up: clear cached instance after test
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_basic_invocation():
    """
    T010: Unit test for get_ai_response() with basic message.

    Validates that get_ai_response() correctly:
    - Converts message to LangChain format
    - Calls ChatOpenAI.ainvoke()
    - Returns AI response content

    Feature: 006-openai-langchain-chat User Story 1
    Expected: FAIL (get_ai_response not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock ainvoke response
            mock_response = Mock()
            mock_response.content = "This is an AI response."
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Call get_ai_response
            result = await get_ai_response("Hello")

            # Verify result
            assert result == "This is an AI response."

            # Verify ainvoke was called
            mock_llm.ainvoke.assert_called_once()

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_preserves_special_characters():
    """
    T010: Unit test for get_ai_response() with special characters.

    Validates that emoji and unicode are preserved through
    the AI response flow.

    Feature: 006-openai-langchain-chat User Story 1
    Expected: FAIL (get_ai_response not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock ainvoke with special characters
            mock_response = Mock()
            mock_response.content = "🚀 means rocket! 世界"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Call with message containing special characters
            result = await get_ai_response("What does 🚀 mean?")

            # Verify special characters preserved
            assert "🚀" in result
            assert "世界" in result

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authentication_error_mapping():
    """
    T030: Unit test for AuthenticationError → 503 error mapping.

    Validates that OpenAI AuthenticationError exceptions are caught
    and mapped to LLMAuthenticationError with user-friendly message.
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response, LLMAuthenticationError
    from openai import AuthenticationError

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Create mock response for AuthenticationError
            mock_response = Mock()
            mock_response.status_code = 401
            mock_body = {"error": {"message": "Invalid API key"}}

            # Mock ainvoke to raise AuthenticationError
            mock_llm.ainvoke = AsyncMock(
                side_effect=AuthenticationError(
                    "Invalid API key provided",
                    response=mock_response,
                    body=mock_body
                )
            )

            # Call should raise our custom LLMAuthenticationError
            with pytest.raises(LLMAuthenticationError) as exc_info:
                await get_ai_response("Hello")

            # Verify error message is sanitized
            assert exc_info.value.message == "AI service configuration error"
            assert exc_info.value.status_code == 503

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rate_limit_error_mapping():
    """
    T031: Unit test for RateLimitError → 503 error mapping.

    Validates that OpenAI RateLimitError exceptions are caught
    and mapped to LLMRateLimitError with user-friendly message.
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response, LLMRateLimitError
    from openai import RateLimitError

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Create mock response for RateLimitError
            mock_response = Mock()
            mock_response.status_code = 429
            mock_body = {"error": {"message": "Rate limit exceeded"}}

            # Mock ainvoke to raise RateLimitError
            mock_llm.ainvoke = AsyncMock(
                side_effect=RateLimitError(
                    "Rate limit exceeded",
                    response=mock_response,
                    body=mock_body
                )
            )

            # Call should raise our custom LLMRateLimitError
            with pytest.raises(LLMRateLimitError) as exc_info:
                await get_ai_response("Hello")

            # Verify error message is sanitized
            assert exc_info.value.message == "AI service is busy"
            assert exc_info.value.status_code == 503

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_timeout_error_mapping():
    """
    T032: Unit test for TimeoutError → 504 error mapping.

    Validates that timeout exceptions are caught
    and mapped to LLMTimeoutError with user-friendly message.
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response, LLMTimeoutError
    import asyncio

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock ainvoke to raise TimeoutError
            mock_llm.ainvoke = AsyncMock(
                side_effect=asyncio.TimeoutError("Request timed out")
            )

            # Call should raise our custom LLMTimeoutError
            with pytest.raises(LLMTimeoutError) as exc_info:
                await get_ai_response("Hello")

            # Verify error message is sanitized
            assert exc_info.value.message == "Request timed out"
            assert exc_info.value.status_code == 504

    # Clean up
    llm_service._llm_instance = None
