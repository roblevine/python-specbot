"""
Unit Tests for LLM Service

Tests LLM service initialization, configuration, and core functionality in isolation.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Updated for: 011-anthropic-support multi-provider architecture
Tests: T004 (TDD - Updated for multi-provider)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock


@pytest.mark.unit
def test_chatgpt_initialization_with_api_key():
    """
    T004 (Updated): Unit test for ChatOpenAI initialization with valid API key.

    Validates that the LLM service properly initializes ChatOpenAI
    with the provided API key and model configuration.

    Updated for 011-anthropic-support multi-provider architecture.
    """
    from src.services.llm_service import get_llm_for_model
    from src.config.models import ModelsConfiguration, ModelConfig

    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance

            # Create test config
            config = ModelsConfiguration(models=[
                ModelConfig(
                    id="gpt-3.5-turbo",
                    name="GPT-3.5 Turbo",
                    description="Fast and efficient",
                    provider="openai",
                    default=True
                )
            ])

            # Initialize with config
            llm = get_llm_for_model("gpt-3.5-turbo", config)

            # Verify ChatOpenAI was called with correct params
            mock_chat.assert_called_once_with(
                api_key="test-key",
                model="gpt-3.5-turbo",
                timeout=120,
                request_timeout=120
            )
            assert llm == mock_instance


@pytest.mark.unit
def test_chatanthropic_initialization_with_api_key():
    """
    T010 (011-anthropic-support): Unit test for ChatAnthropic initialization.

    Validates that the LLM service properly initializes ChatAnthropic
    with the provided API key for Anthropic provider.
    """
    from src.services.llm_service import get_llm_for_model
    from src.config.models import ModelsConfiguration, ModelConfig

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-anthropic-key'}):
        with patch('src.services.llm_service.ChatAnthropic') as mock_chat:
            mock_instance = Mock()
            mock_chat.return_value = mock_instance

            # Create test config with Anthropic model
            config = ModelsConfiguration(models=[
                ModelConfig(
                    id="claude-3-5-sonnet-20241022",
                    name="Claude 3.5 Sonnet",
                    description="Most capable Claude model",
                    provider="anthropic",
                    default=True
                )
            ])

            # Initialize with config
            llm = get_llm_for_model("claude-3-5-sonnet-20241022", config)

            # Verify ChatAnthropic was called with correct params
            mock_chat.assert_called_once_with(
                api_key="test-anthropic-key",
                model="claude-3-5-sonnet-20241022",
                timeout=120
            )
            assert llm == mock_instance


@pytest.mark.unit
def test_provider_routing_openai():
    """
    T011 (011-anthropic-support): Unit test for provider routing to OpenAI.

    Validates that models with provider="openai" are routed to ChatOpenAI.
    """
    from src.services.llm_service import get_llm_for_model
    from src.config.models import ModelsConfiguration, ModelConfig

    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        with patch('src.services.llm_service.ChatOpenAI') as mock_openai, \
             patch('src.services.llm_service.ChatAnthropic') as mock_anthropic:

            mock_openai.return_value = Mock()
            mock_anthropic.return_value = Mock()

            config = ModelsConfiguration(models=[
                ModelConfig(
                    id="gpt-4",
                    name="GPT-4",
                    description="Most capable OpenAI model",
                    provider="openai",
                    default=True
                )
            ])

            get_llm_for_model("gpt-4", config)

            # OpenAI should be called, Anthropic should not
            mock_openai.assert_called_once()
            mock_anthropic.assert_not_called()


@pytest.mark.unit
def test_provider_routing_anthropic():
    """
    T011 (011-anthropic-support): Unit test for provider routing to Anthropic.

    Validates that models with provider="anthropic" are routed to ChatAnthropic.
    """
    from src.services.llm_service import get_llm_for_model
    from src.config.models import ModelsConfiguration, ModelConfig

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        with patch('src.services.llm_service.ChatOpenAI') as mock_openai, \
             patch('src.services.llm_service.ChatAnthropic') as mock_anthropic:

            mock_openai.return_value = Mock()
            mock_anthropic.return_value = Mock()

            config = ModelsConfiguration(models=[
                ModelConfig(
                    id="claude-3-5-sonnet-20241022",
                    name="Claude 3.5 Sonnet",
                    description="Most capable Claude model",
                    provider="anthropic",
                    default=True
                )
            ])

            get_llm_for_model("claude-3-5-sonnet-20241022", config)

            # Anthropic should be called, OpenAI should not
            mock_anthropic.assert_called_once()
            mock_openai.assert_not_called()


@pytest.mark.unit
def test_missing_openai_api_key_raises_error():
    """
    T004 (Updated): Unit test for error handling when OpenAI API key is missing.

    Updated for 011-anthropic-support multi-provider architecture.
    """
    from src.services.llm_service import get_llm_for_model, LLMAuthenticationError
    from src.config.models import ModelsConfiguration, ModelConfig

    # Mock environment without API key
    with patch.dict('os.environ', {}, clear=True):
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="Fast and efficient",
                provider="openai",
                default=True
            )
        ])

        with pytest.raises(LLMAuthenticationError, match="OpenAI API key not configured"):
            get_llm_for_model("gpt-3.5-turbo", config)


@pytest.mark.unit
def test_missing_anthropic_api_key_raises_error():
    """
    T017 (011-anthropic-support): Unit test for missing Anthropic API key.

    Validates that appropriate error is raised when ANTHROPIC_API_KEY
    is not configured for Anthropic models.
    """
    from src.services.llm_service import get_llm_for_model, LLMAuthenticationError
    from src.config.models import ModelsConfiguration, ModelConfig

    # Mock environment without Anthropic API key
    with patch.dict('os.environ', {}, clear=True):
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                description="Most capable Claude model",
                provider="anthropic",
                default=True
            )
        ])

        with pytest.raises(LLMAuthenticationError, match="Anthropic API key not configured"):
            get_llm_for_model("claude-3-5-sonnet-20241022", config)


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
    """
    from src.services.llm_service import get_ai_response

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_preserves_special_characters():
    """
    T010: Unit test for get_ai_response() with special characters.

    Validates that emoji and unicode are preserved through
    the AI response flow.

    Feature: 006-openai-langchain-chat User Story 1
    """
    from src.services.llm_service import get_ai_response

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_authentication_error_mapping():
    """
    T030: Unit test for AuthenticationError → 503 error mapping.

    Validates that OpenAI AuthenticationError exceptions are caught
    and mapped to LLMAuthenticationError with user-friendly message.
    """
    from src.services.llm_service import get_ai_response, LLMAuthenticationError
    from openai import AuthenticationError

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rate_limit_error_mapping():
    """
    T031: Unit test for RateLimitError → 503 error mapping.

    Validates that OpenAI RateLimitError exceptions are caught
    and mapped to LLMRateLimitError with user-friendly message.
    """
    from src.services.llm_service import get_ai_response, LLMRateLimitError
    from openai import RateLimitError

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_timeout_error_mapping():
    """
    T032: Unit test for TimeoutError → 504 error mapping.

    Validates that timeout exceptions are caught
    and mapped to LLMTimeoutError with user-friendly message.
    """
    from src.services.llm_service import get_ai_response, LLMTimeoutError
    import asyncio

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ai_response_validates_model_id():
    """
    T015: Unit test for model ID validation in get_ai_response().

    Validates that:
    - Invalid model IDs are rejected with error
    - Validation happens before calling OpenAI API
    """
    from src.services.llm_service import get_ai_response, LLMServiceError

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODELS': '[{"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient", "default": true}]'
    }):
        with patch('src.services.llm_service.ChatOpenAI') as mock_chat:
            # Should raise error for invalid model (not in config)
            with pytest.raises((ValueError, LLMServiceError)):
                await get_ai_response("Hello", model="invalid-model")

            # Verify ChatOpenAI was NOT called (validation failed first)
            mock_chat.assert_not_called()


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
    """
    from src.services.llm_service import stream_ai_response
    from src.schemas import TokenEvent

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
    from src.services.llm_service import stream_ai_response
    from src.schemas import CompleteEvent

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
    from src.services.llm_service import stream_ai_response
    from langchain_core.messages import HumanMessage, AIMessage

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
    from src.services.llm_service import stream_ai_response
    from src.schemas import ErrorEvent
    from openai import AuthenticationError

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_rate_limit_error():
    """
    T008: Unit test for stream_ai_response() error handling - RateLimitError.

    Validates that RateLimitError during streaming yields ErrorEvent
    with RATE_LIMIT code.

    Feature: 009-message-streaming User Story 3
    """
    from src.services.llm_service import stream_ai_response
    from src.schemas import ErrorEvent
    from openai import RateLimitError

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_timeout():
    """
    T008: Unit test for stream_ai_response() error handling - TimeoutError.

    Validates that timeout during streaming yields ErrorEvent
    with TIMEOUT code.

    Feature: 009-message-streaming User Story 3
    """
    from src.services.llm_service import stream_ai_response
    from src.schemas import ErrorEvent
    import asyncio

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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_stream_ai_response_handles_special_characters():
    """
    T008: Unit test for stream_ai_response() preserving special characters.

    Validates that emoji, unicode, and special characters are
    preserved through streaming.

    Feature: 009-message-streaming User Story 1
    """
    from src.services.llm_service import stream_ai_response
    from src.schemas import TokenEvent

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
