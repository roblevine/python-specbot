"""
LLM Service - Multi-Provider Chat Integration via LangChain

Manages LLM initialization, configuration, and message processing for both
OpenAI and Anthropic providers.

Features: 006-openai-langchain-chat, 011-anthropic-support
"""

import os
import asyncio
import traceback
from typing import Any, Dict, Optional, List, Union
from langchain_openai import ChatOpenAI
# T013: Import ChatAnthropic from langchain_anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from openai import (
    AuthenticationError as OpenAIAuthenticationError,
    RateLimitError as OpenAIRateLimitError,
    APIConnectionError as OpenAIAPIConnectionError,
    BadRequestError as OpenAIBadRequestError,
    APITimeoutError as OpenAIAPITimeoutError
)
# T017: Import Anthropic error types
from anthropic import (
    AuthenticationError as AnthropicAuthenticationError,
    RateLimitError as AnthropicRateLimitError,
    APIConnectionError as AnthropicAPIConnectionError,
    BadRequestError as AnthropicBadRequestError,
    APITimeoutError as AnthropicAPITimeoutError
)
from src.utils.logger import get_logger
from src.config.models import (
    load_model_configuration,
    get_default_model,
    validate_model_id,
    get_model_by_id,
    get_provider_for_model,
    ModelConfigurationError,
    PROVIDERS
)
from src.schemas import TokenEvent, CompleteEvent, ErrorEvent

logger = get_logger(__name__)


# Custom exception classes for LLM errors
class LLMServiceError(Exception):
    """Base exception for LLM service errors"""
    def __init__(self, message: str, status_code: int = 503, original_error: Optional[Exception] = None):
        self.message = message
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)


class LLMAuthenticationError(LLMServiceError):
    """Authentication/configuration error → 503"""
    def __init__(self, message: str = "AI service configuration error", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMRateLimitError(LLMServiceError):
    """Rate limit error → 503"""
    def __init__(self, message: str = "AI service is busy", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMConnectionError(LLMServiceError):
    """Connection error → 503"""
    def __init__(self, message: str = "Unable to reach AI service", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMTimeoutError(LLMServiceError):
    """Timeout error → 504"""
    def __init__(self, message: str = "Request timed out", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=504, original_error=original_error)


class LLMBadRequestError(LLMServiceError):
    """Bad request error → 400"""
    def __init__(self, message: str = "Message could not be processed", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=400, original_error=original_error)


def _is_debug_mode() -> bool:
    """Check if DEBUG mode is enabled."""
    return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')


def _build_debug_info(error: Exception, error_type: str) -> Optional[Dict[str, Any]]:
    """
    Build debug_info dict for streaming errors when DEBUG mode is enabled.

    Args:
        error: The exception that occurred
        error_type: The type/class name of the error

    Returns:
        Dict with debug info if DEBUG mode is enabled, None otherwise
    """
    if not _is_debug_mode():
        return None

    return {
        "error_type": error_type,
        "error_message": str(error),
        "original_error": str(getattr(error, 'original_error', error)),
        "traceback": traceback.format_exc()
    }


def get_llm_for_model(model_id: str, config=None) -> BaseChatModel:
    """
    T014: Factory function to get the appropriate LLM instance for a model.

    Creates either a ChatOpenAI or ChatAnthropic instance based on the model's
    provider configuration.

    Args:
        model_id: The model ID to create an LLM instance for
        config: Optional ModelsConfiguration (loads from env if not provided)

    Returns:
        BaseChatModel: Either ChatOpenAI or ChatAnthropic instance

    Raises:
        ValueError: If model not found or provider not supported
        LLMAuthenticationError: If provider API key not configured
    """
    if config is None:
        config = load_model_configuration()

    model = get_model_by_id(model_id, config)
    if not model:
        raise ValueError(f"Model not found: {model_id}")

    provider = model.provider

    if provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise LLMAuthenticationError("OpenAI API key not configured")

        logger.debug(f"Creating ChatOpenAI instance for model: {model_id}")
        return ChatOpenAI(
            api_key=api_key,
            model=model_id,
            timeout=120,
            request_timeout=120
        )

    elif provider == "anthropic":
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise LLMAuthenticationError("Anthropic API key not configured")

        logger.debug(f"Creating ChatAnthropic instance for model: {model_id}")
        return ChatAnthropic(
            api_key=api_key,
            model=model_id,
            timeout=120
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def convert_to_langchain_messages(history: List[Dict[str, str]]) -> List[BaseMessage]:
    """
    Convert conversation history to LangChain message format.

    Converts an array of message objects with sender/text fields into
    LangChain message types (HumanMessage for user, AIMessage for system).

    Args:
        history: List of message dictionaries with "sender" and "text" fields
                 sender can be "user" or "system"

    Returns:
        List of LangChain message objects (HumanMessage or AIMessage)
    """
    logger.debug(f"Converting {len(history)} message(s) to LangChain format")

    langchain_messages: List[BaseMessage] = []

    for msg in history:
        sender = msg.get("sender")
        text = msg.get("text", "")

        if sender == "user":
            langchain_messages.append(HumanMessage(content=text))
        elif sender == "system":
            langchain_messages.append(AIMessage(content=text))
        else:
            logger.warning(f"Unknown sender type: {sender}, skipping message")

    logger.debug(f"Converted to {len(langchain_messages)} LangChain message(s)")
    return langchain_messages


def _map_exception_to_llm_error(e: Exception) -> LLMServiceError:
    """
    T018: Map provider-specific exceptions to LLM service errors.

    Handles both OpenAI and Anthropic exception types.

    Args:
        e: The exception to map

    Returns:
        Appropriate LLMServiceError subclass
    """
    # OpenAI exceptions
    if isinstance(e, OpenAIAuthenticationError):
        return LLMAuthenticationError(original_error=e)
    if isinstance(e, OpenAIRateLimitError):
        return LLMRateLimitError(original_error=e)
    if isinstance(e, OpenAIAPIConnectionError):
        return LLMConnectionError(original_error=e)
    if isinstance(e, (OpenAIAPITimeoutError, asyncio.TimeoutError)):
        return LLMTimeoutError(original_error=e)
    if isinstance(e, OpenAIBadRequestError):
        return LLMBadRequestError(original_error=e)

    # Anthropic exceptions
    if isinstance(e, AnthropicAuthenticationError):
        return LLMAuthenticationError(original_error=e)
    if isinstance(e, AnthropicRateLimitError):
        return LLMRateLimitError(original_error=e)
    if isinstance(e, AnthropicAPIConnectionError):
        return LLMConnectionError(original_error=e)
    if isinstance(e, AnthropicAPITimeoutError):
        return LLMTimeoutError(original_error=e)
    if isinstance(e, AnthropicBadRequestError):
        return LLMBadRequestError(original_error=e)

    # Default: generic LLM error
    return LLMServiceError("AI service error occurred", original_error=e)


async def get_ai_response(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None
) -> tuple[str, str]:
    """
    T015: Get AI response for a user message with multi-provider support.

    Sends the user message to the appropriate LLM provider via LangChain and returns
    the AI-generated response.

    Args:
        message: User message text
        history: Optional list of previous messages with sender/text fields
        model: Optional model ID to use for this request.
               If not provided, uses the configured default model.

    Returns:
        Tuple of (AI-generated response text, model ID used)

    Raises:
        LLMAuthenticationError: If API key is invalid → 503
        LLMRateLimitError: If rate limit exceeded → 503
        LLMConnectionError: If cannot reach API → 503
        LLMTimeoutError: If request times out → 504
        LLMBadRequestError: If request is malformed → 400
        ValueError: If message is empty or model is invalid
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    logger.info(f"Processing AI request for message: {message[:50]}...")
    if history:
        logger.info(f"Including {len(history)} message(s) from conversation history")

    try:
        # Load model configuration
        config = load_model_configuration()

        # Determine which model to use
        if model:
            model_to_use = model
            logger.info(f"User-selected model: {model_to_use}")
        else:
            model_to_use = get_default_model(config)
            logger.info(f"Using default model: {model_to_use}")

        # Validate model against configuration
        if not validate_model_id(model_to_use, config):
            available_models = [m.id for m in config.models]
            logger.error(f"Invalid model requested: {model_to_use}. Available: {', '.join(available_models)}")
            raise ValueError(
                f"Invalid model: {model_to_use}. "
                f"Available models: {', '.join(available_models)}"
            )

        # Get provider for logging
        provider = get_provider_for_model(model_to_use, config)
        logger.info(f"Using provider: {provider}")

        # T015: Get LLM instance using factory function
        llm = get_llm_for_model(model_to_use, config)

        # Build conversation history
        conversation = history.copy() if history else []
        conversation.append({"sender": "user", "text": message})

        # Convert to LangChain format
        langchain_messages = convert_to_langchain_messages(conversation)

        # Call LLM service
        logger.debug(f"Invoking LLM with {len(langchain_messages)} message(s)")
        response = await llm.ainvoke(langchain_messages)

        # Extract content from response
        ai_response = response.content
        logger.info(f"AI response received: {len(ai_response)} characters")
        logger.debug(f"AI response preview: {ai_response[:100]}...")

        return ai_response, model_to_use

    except (OpenAIAuthenticationError, AnthropicAuthenticationError) as e:
        logger.error(f"LLM authentication failed: {type(e).__name__}")
        raise LLMAuthenticationError(original_error=e)

    except (OpenAIRateLimitError, AnthropicRateLimitError) as e:
        logger.error(f"LLM rate limit exceeded: {type(e).__name__}")
        raise LLMRateLimitError(original_error=e)

    except (OpenAIAPIConnectionError, AnthropicAPIConnectionError) as e:
        logger.error(f"LLM connection failed: {type(e).__name__}")
        raise LLMConnectionError(original_error=e)

    except (OpenAIAPITimeoutError, AnthropicAPITimeoutError, asyncio.TimeoutError) as e:
        logger.error(f"LLM request timed out: {type(e).__name__}")
        raise LLMTimeoutError(original_error=e)

    except (OpenAIBadRequestError, AnthropicBadRequestError) as e:
        logger.error(f"LLM bad request: {type(e).__name__}: {str(e)}")
        raise LLMBadRequestError(original_error=e)

    except LLMServiceError:
        # Re-raise LLM service errors as-is
        raise

    except Exception as e:
        logger.error(f"Unexpected LLM error: {type(e).__name__}: {str(e)}")
        raise LLMServiceError("AI service error occurred", original_error=e)


async def stream_ai_response(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None
):
    """
    T016: Stream AI response as token-by-token events with multi-provider support.

    Streams the AI response as a sequence of events using Server-Sent Events protocol.
    Uses LangChain's astream() for token-by-token streaming from the LLM.

    Args:
        message: User message text
        history: Optional list of previous messages with sender/text fields
        model: Optional model ID to use for this request.

    Yields:
        TokenEvent: For each token/chunk from the LLM
        CompleteEvent: Final event indicating stream completion with model info
        ErrorEvent: If an error occurs during streaming
    """
    if not message or not message.strip():
        yield ErrorEvent(
            error="Message cannot be empty",
            code="UNKNOWN"
        )
        return

    logger.info(f"Starting streaming for message: {message[:50]}...")
    if history:
        logger.info(f"Including {len(history)} message(s) from conversation history")

    try:
        # Load model configuration
        config = load_model_configuration()

        # Determine which model to use
        if model:
            model_to_use = model
            logger.info(f"User-selected model: {model_to_use}")
        else:
            model_to_use = get_default_model(config)
            logger.info(f"Using default model: {model_to_use}")

        # Validate model against configuration
        if not validate_model_id(model_to_use, config):
            available_models = [m.id for m in config.models]
            logger.error(f"Invalid model requested: {model_to_use}. Available: {', '.join(available_models)}")
            yield ErrorEvent(
                error=f"Invalid model: {model_to_use}",
                code="UNKNOWN"
            )
            return

        # Get provider for logging
        provider = get_provider_for_model(model_to_use, config)
        logger.info(f"Using provider: {provider}")

        # T016: Get LLM instance using factory function
        llm = get_llm_for_model(model_to_use, config)

        # Build conversation history
        conversation = history.copy() if history else []
        conversation.append({"sender": "user", "text": message})

        # Convert to LangChain format
        langchain_messages = convert_to_langchain_messages(conversation)

        # Stream LLM response
        logger.debug(f"Streaming from LLM with {len(langchain_messages)} message(s)")

        async for chunk in llm.astream(langchain_messages):
            # Extract content from chunk
            content = chunk.content

            # Skip empty chunks
            if content:
                yield TokenEvent(content=content)

        # Yield completion event
        logger.info(f"Stream completed successfully using model: {model_to_use}")
        yield CompleteEvent(model=model_to_use)

    except (OpenAIAuthenticationError, AnthropicAuthenticationError) as e:
        logger.error(f"LLM authentication failed during streaming: {type(e).__name__}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="AI service configuration error",
            code="AUTH_ERROR",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except (OpenAIRateLimitError, AnthropicRateLimitError) as e:
        logger.error(f"LLM rate limit exceeded during streaming: {type(e).__name__}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="AI service is busy",
            code="RATE_LIMIT",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except (OpenAIAPIConnectionError, AnthropicAPIConnectionError) as e:
        logger.error(f"LLM connection failed during streaming: {type(e).__name__}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="Unable to reach AI service",
            code="CONNECTION_ERROR",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except (OpenAIAPITimeoutError, AnthropicAPITimeoutError, asyncio.TimeoutError) as e:
        logger.error(f"LLM request timed out during streaming: {type(e).__name__}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="Request timed out",
            code="TIMEOUT",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except (OpenAIBadRequestError, AnthropicBadRequestError) as e:
        logger.error(f"LLM bad request during streaming: {type(e).__name__}: {str(e)}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="Message could not be processed",
            code="LLM_ERROR",
            debug_info=_build_debug_info(e, type(e).__name__)
        )

    except LLMAuthenticationError as e:
        logger.error(f"LLM authentication error: {e.message}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error=e.message,
            code="AUTH_ERROR",
            debug_info=_build_debug_info(e, "LLMAuthenticationError")
        )

    except Exception as e:
        logger.error(f"Unexpected error during streaming: {type(e).__name__}: {str(e)}")
        if _is_debug_mode():
            logger.warning("DEBUG mode enabled - including detailed error info in streaming response")
        yield ErrorEvent(
            error="AI service error occurred",
            code="UNKNOWN",
            debug_info=_build_debug_info(e, type(e).__name__)
        )
