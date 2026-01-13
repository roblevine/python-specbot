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
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'OPENAI_MODELS': ''  # Clear OPENAI_MODELS so OPENAI_MODEL fallback is used
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
            result, model_used = await get_ai_response("Hello")

            # Verify result
            assert result == "This is an AI response."
            assert model_used == "gpt-3.5-turbo"

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
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'OPENAI_MODELS': ''  # Clear OPENAI_MODELS so OPENAI_MODEL fallback is used
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
            result, model_used = await get_ai_response("What does 🚀 mean?")

            # Verify special characters preserved
            assert "🚀" in result
            assert "世界" in result
            assert model_used == "gpt-3.5-turbo"

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_with_specific_model():
    """
    T015: Unit test for get_ai_response() with per-request model selection.

    Validates that when a specific model is requested, the LLM service:
    - Creates ChatOpenAI instance with the specified model
    - Returns both the response and the model ID that was used
    - Does not use the default/cached model

    Feature: 008-openai-model-selector User Story 1
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'  # Default model
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat, \
             patch('src.services.llm_service.load_model_configuration') as mock_load_config, \
             patch('src.services.llm_service.validate_model_id') as mock_validate:

            # Mock model configuration
            mock_config = Mock()
            mock_config.models = []
            mock_load_config.return_value = mock_config
            mock_validate.return_value = True  # Model is valid

            # Setup mock LLM for requested model
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock ainvoke response
            mock_response = Mock()
            mock_response.content = "Response from GPT-4"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Call get_ai_response with specific model
            result, model_used = await get_ai_response("Hello", model="gpt-4")

            # Verify ChatOpenAI was created with requested model
            mock_chat.assert_called_with(
                api_key='test-key',
                model='gpt-4'
            )

            # Verify response and model are returned
            assert result == "Response from GPT-4"
            assert model_used == "gpt-4"

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_uses_default_model_when_not_specified():
    """
    T015: Unit test for get_ai_response() using default model.

    Validates that when no model is specified:
    - The default model from configuration is used
    - Returns the default model ID in the response tuple
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat, \
             patch('src.services.llm_service.load_model_configuration') as mock_load_config, \
             patch('src.services.llm_service.get_default_model') as mock_get_default, \
             patch('src.services.llm_service.validate_model_id') as mock_validate:

            # Mock model configuration with actual model
            mock_model = Mock()
            mock_model.id = "gpt-3.5-turbo"
            mock_config = Mock()
            mock_config.models = [mock_model]
            mock_load_config.return_value = mock_config
            mock_get_default.return_value = "gpt-3.5-turbo"
            mock_validate.return_value = True  # Validate default model

            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock ainvoke response
            mock_response = Mock()
            mock_response.content = "Response from default model"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Call get_ai_response WITHOUT specifying model
            result, model_used = await get_ai_response("Hello")

            # Verify default model was used
            mock_chat.assert_called_with(
                api_key='test-key',
                model='gpt-3.5-turbo'
            )

            # Verify response and default model are returned
            assert result == "Response from default model"
            assert model_used == "gpt-3.5-turbo"

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_validates_model_id():
    """
    T015: Unit test for model ID validation in get_ai_response().

    Validates that:
    - Invalid model IDs are rejected with LLMServiceError
    - Validation happens before calling OpenAI API
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response, LLMServiceError

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.load_model_configuration') as mock_load_config, \
             patch('src.services.llm_service.validate_model_id') as mock_validate, \
             patch('src.services.llm_service.ChatOpenAI') as mock_chat:

            # Mock model configuration
            mock_model = Mock()
            mock_model.id = "gpt-4"
            mock_config = Mock()
            mock_config.models = [mock_model]
            mock_load_config.return_value = mock_config

            # Model validation returns False for invalid model
            mock_validate.return_value = False

            # Should raise LLMServiceError (ValueError is wrapped)
            with pytest.raises(LLMServiceError):
                await get_ai_response("Hello", model="invalid-model")

            # Verify ChatOpenAI was NOT called (validation failed first)
            mock_chat.assert_not_called()

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_with_conversation_history_and_model():
    """
    T015: Unit test for get_ai_response() with history and model selection.

    Validates that both conversation history and model selection work together.
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import get_ai_response
    from langchain_core.messages import HumanMessage, AIMessage

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-3.5-turbo'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat, \
             patch('src.services.llm_service.load_model_configuration') as mock_load_config, \
             patch('src.services.llm_service.validate_model_id') as mock_validate:

            # Mock model configuration
            mock_config = Mock()
            mock_config.models = []
            mock_load_config.return_value = mock_config
            mock_validate.return_value = True

            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock ainvoke response
            mock_response = Mock()
            mock_response.content = "Context-aware response"
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)

            # Call with history and model
            history = [
                {"sender": "user", "text": "First message"},
                {"sender": "system", "text": "First response"}
            ]

            result, model_used = await get_ai_response(
                "Second message",
                history=history,
                model="gpt-4"
            )

            # Verify ChatOpenAI was created with requested model
            mock_chat.assert_called_with(
                api_key='test-key',
                model='gpt-4'
            )

            # Verify ainvoke was called with history + new message
            mock_llm.ainvoke.assert_called_once()
            call_args = mock_llm.ainvoke.call_args[0][0]

            # Should have 3 messages: history (2) + new message (1)
            assert len(call_args) == 3
            assert isinstance(call_args[0], HumanMessage)
            assert call_args[0].content == "First message"
            assert isinstance(call_args[1], AIMessage)
            assert call_args[1].content == "First response"
            assert isinstance(call_args[2], HumanMessage)
            assert call_args[2].content == "Second message"

            # Verify response
            assert result == "Context-aware response"
            assert model_used == "gpt-4"

    # Clean up
    llm_service._llm_instance = None
