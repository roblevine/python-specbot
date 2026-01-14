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
            model="gpt-3.5-turbo",
            timeout=120,
            request_timeout=120
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
        'OPENAI_MODELS': '[{"id": "gpt-4", "name": "GPT-4", "description": "Most capable", "default": true}]'
    }):
        config = load_config()

        assert config['api_key'] == 'env-test-key'
        assert config['model'] == 'gpt-4'


@pytest.mark.unit
def test_config_loading_requires_openai_models():
    """
    T004: Unit test for error when OPENAI_MODELS not set.

    Validates that an error is raised when OPENAI_MODELS
    is not configured (required since removal of OPENAI_MODEL fallback).

    Expected: FAIL (service not implemented yet)
    """
    from src.services.llm_service import load_config
    from src.config.models import ModelConfigurationError

    # Mock environment with only API key (no OPENAI_MODELS)
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key'
    }, clear=True):
        with pytest.raises(ModelConfigurationError) as exc_info:
            load_config()

        assert "OPENAI_MODELS environment variable is required" in str(exc_info.value)


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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'  # Default model
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
                model='gpt-4',
                timeout=120,
                request_timeout=120
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
                model='gpt-3.5-turbo',
                timeout=120,
                request_timeout=120
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
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
                model='gpt-4',
                timeout=120,
                request_timeout=120
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


# ============================================================================
# Streaming Tests (Feature: 009-message-streaming)
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_yields_tokens():
    """
    T008: Unit test for stream_ai_response() yielding token events.

    Validates that stream_ai_response():
    - Returns an async generator
    - Yields TokenEvent objects for each LLM chunk
    - Properly converts LangChain chunks to TokenEvent format

    Feature: 009-message-streaming User Story 1
    Expected: FAIL (stream_ai_response not implemented yet)
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import TokenEvent

    # Clear cached instance
    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Setup mock LLM
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock astream to yield chunks
            async def mock_astream(messages):
                # Simulate LangChain AIMessageChunk objects
                chunks = [
                    Mock(content="Hello"),
                    Mock(content=" "),
                    Mock(content="world"),
                    Mock(content="!")
                ]
                for chunk in chunks:
                    yield chunk

            mock_llm.astream = mock_astream

            # Call stream_ai_response
            events = []
            async for event in stream_ai_response("Test message"):
                events.append(event)

            # Verify we got TokenEvents
            assert len(events) == 5  # 4 tokens + 1 complete event

            # First 4 should be TokenEvents
            for i in range(4):
                assert isinstance(events[i], TokenEvent)
                assert events[i].type == "token"

            # Verify content matches chunks
            assert events[0].content == "Hello"
            assert events[1].content == " "
            assert events[2].content == "world"
            assert events[3].content == "!"

    # Clean up
    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_yields_complete_event():
    """
    T008: Unit test for stream_ai_response() yielding CompleteEvent.

    Validates that after all token chunks:
    - A CompleteEvent is yielded as the final event
    - CompleteEvent includes the model ID
    - CompleteEvent marks end of stream

    Feature: 009-message-streaming User Story 1
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import CompleteEvent

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            async def mock_astream(messages):
                chunks = [Mock(content="Test")]
                for chunk in chunks:
                    yield chunk

            mock_llm.astream = mock_astream

            events = []
            async for event in stream_ai_response("Test"):
                events.append(event)

            # Last event should be CompleteEvent
            assert len(events) == 2  # 1 token + 1 complete
            assert isinstance(events[-1], CompleteEvent)
            assert events[-1].type == "complete"
            assert events[-1].model == "gpt-3.5-turbo"

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_with_conversation_history():
    """
    T008: Unit test for stream_ai_response() with conversation history.

    Validates that:
    - Conversation history is passed to LangChain astream()
    - History is converted to LangChain message format
    - New message is appended after history

    Feature: 009-message-streaming User Story 1
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from langchain_core.messages import HumanMessage, AIMessage

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Track what messages were passed to astream
            captured_messages = []

            async def mock_astream(messages):
                captured_messages.extend(messages)
                yield Mock(content="Response")

            mock_llm.astream = mock_astream

            # Call with history
            history = [
                {"sender": "user", "text": "First message"},
                {"sender": "system", "text": "First response"}
            ]

            events = []
            async for event in stream_ai_response("Second message", history=history):
                events.append(event)

            # Verify history was converted and passed
            assert len(captured_messages) == 3  # 2 history + 1 new
            assert isinstance(captured_messages[0], HumanMessage)
            assert captured_messages[0].content == "First message"
            assert isinstance(captured_messages[1], AIMessage)
            assert captured_messages[1].content == "First response"
            assert isinstance(captured_messages[2], HumanMessage)
            assert captured_messages[2].content == "Second message"

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_with_custom_model():
    """
    T008: Unit test for stream_ai_response() with per-request model selection.

    Validates that:
    - Custom model can be specified per request
    - ChatOpenAI is initialized with the specified model
    - CompleteEvent returns the model that was used

    Feature: 009-message-streaming + 008-openai-model-selector
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import CompleteEvent

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat, \
             patch('src.services.llm_service.load_model_configuration') as mock_load_config, \
             patch('src.services.llm_service.validate_model_id') as mock_validate:

            # Mock model configuration
            mock_config = Mock()
            mock_config.models = []
            mock_load_config.return_value = mock_config
            mock_validate.return_value = True

            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            async def mock_astream(messages):
                yield Mock(content="GPT-4 response")

            mock_llm.astream = mock_astream

            # Call with custom model
            events = []
            async for event in stream_ai_response("Test", model="gpt-4"):
                events.append(event)

            # Verify ChatOpenAI was created with requested model
            mock_chat.assert_called_with(
                api_key='test-key',
                model='gpt-4',
                timeout=120,
                request_timeout=120
            )

            # Verify CompleteEvent has correct model
            complete_event = events[-1]
            assert isinstance(complete_event, CompleteEvent)
            assert complete_event.model == "gpt-4"

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_authentication_error():
    """
    T008: Unit test for stream_ai_response() error handling - AuthenticationError.

    Validates that:
    - OpenAI AuthenticationError is caught during streaming
    - ErrorEvent is yielded with appropriate error code
    - Stream terminates after error event

    Feature: 009-message-streaming User Story 3
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import ErrorEvent
    from openai import AuthenticationError

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock astream to raise AuthenticationError
            async def mock_astream(messages):
                mock_response = Mock()
                mock_response.status_code = 401
                raise AuthenticationError(
                    "Invalid API key",
                    response=mock_response,
                    body={"error": {"message": "Invalid API key"}}
                )
                yield  # Make it a generator (unreachable)

            mock_llm.astream = mock_astream

            # Collect events
            events = []
            async for event in stream_ai_response("Test"):
                events.append(event)

            # Should yield exactly one ErrorEvent
            assert len(events) == 1
            assert isinstance(events[0], ErrorEvent)
            assert events[0].type == "error"
            assert events[0].code == "AUTH_ERROR"
            assert "authentication" in events[0].error.lower() or "configuration" in events[0].error.lower()

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_rate_limit_error():
    """
    T008: Unit test for stream_ai_response() error handling - RateLimitError.

    Validates that RateLimitError during streaming yields ErrorEvent
    with RATE_LIMIT code.

    Feature: 009-message-streaming User Story 3
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import ErrorEvent
    from openai import RateLimitError

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            async def mock_astream(messages):
                mock_response = Mock()
                mock_response.status_code = 429
                raise RateLimitError(
                    "Rate limit exceeded",
                    response=mock_response,
                    body={"error": {"message": "Rate limit"}}
                )
                yield

            mock_llm.astream = mock_astream

            events = []
            async for event in stream_ai_response("Test"):
                events.append(event)

            assert len(events) == 1
            assert isinstance(events[0], ErrorEvent)
            assert events[0].code == "RATE_LIMIT"

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_timeout():
    """
    T008: Unit test for stream_ai_response() error handling - TimeoutError.

    Validates that timeout during streaming yields ErrorEvent
    with TIMEOUT code.

    Feature: 009-message-streaming User Story 3
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import ErrorEvent
    import asyncio

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            async def mock_astream(messages):
                raise asyncio.TimeoutError("Request timed out")
                yield

            mock_llm.astream = mock_astream

            events = []
            async for event in stream_ai_response("Test"):
                events.append(event)

            assert len(events) == 1
            assert isinstance(events[0], ErrorEvent)
            assert events[0].code == "TIMEOUT"

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_empty_response():
    """
    T008: Unit test for stream_ai_response() with empty/no chunks.

    Validates that:
    - If LLM yields no chunks, still yields CompleteEvent
    - No TokenEvents are yielded for empty response
    - Stream completes gracefully

    Feature: 009-message-streaming User Story 1
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import CompleteEvent

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            # Mock astream that yields nothing
            async def mock_astream(messages):
                return
                yield  # Make it a generator

            mock_llm.astream = mock_astream

            events = []
            async for event in stream_ai_response("Test"):
                events.append(event)

            # Should only get CompleteEvent, no tokens
            assert len(events) == 1
            assert isinstance(events[0], CompleteEvent)
            assert events[0].model == "gpt-3.5-turbo"

    llm_service._llm_instance = None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_special_characters():
    """
    T008: Unit test for stream_ai_response() preserving special characters.

    Validates that emoji, unicode, and special characters are
    preserved through streaming.

    Feature: 009-message-streaming User Story 1
    """
    import src.services.llm_service as llm_service
    from src.services.llm_service import stream_ai_response
    from src.schemas import TokenEvent

    llm_service._llm_instance = None

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            async def mock_astream(messages):
                # Chunks with special characters
                chunks = [
                    Mock(content="🚀"),
                    Mock(content=" Hello "),
                    Mock(content="世界"),
                    Mock(content=" @#$%")
                ]
                for chunk in chunks:
                    yield chunk

            mock_llm.astream = mock_astream

            events = []
            async for event in stream_ai_response("Test"):
                if isinstance(event, TokenEvent):
                    events.append(event)

            # Verify special characters preserved
            assert events[0].content == "🚀"
            assert events[1].content == " Hello "
            assert events[2].content == "世界"
            assert events[3].content == " @#$%"

    llm_service._llm_instance = None
