"""
LLM Service - OpenAI ChatGPT Integration via LangChain

Manages LLM initialization, configuration, and message processing.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Tasks: T006, T007
"""

import os
import asyncio
from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from openai import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    BadRequestError,
    APITimeoutError
)
from src.utils.logger import get_logger
from src.config.models import (
    load_model_configuration,
    get_default_model,
    validate_model_id,
    ModelConfigurationError
)

logger = get_logger(__name__)

# Module-level cache for LLM instance (singleton pattern)
_llm_instance: Optional[ChatOpenAI] = None


# Custom exception classes for LLM errors (T034-T038)
class LLMServiceError(Exception):
    """Base exception for LLM service errors"""
    def __init__(self, message: str, status_code: int = 503, original_error: Optional[Exception] = None):
        self.message = message
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)


class LLMAuthenticationError(LLMServiceError):
    """T034: Authentication/configuration error → 503"""
    def __init__(self, message: str = "AI service configuration error", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMRateLimitError(LLMServiceError):
    """T035: Rate limit error → 503"""
    def __init__(self, message: str = "AI service is busy", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMConnectionError(LLMServiceError):
    """T036: Connection error → 503"""
    def __init__(self, message: str = "Unable to reach AI service", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMTimeoutError(LLMServiceError):
    """T037: Timeout error → 504"""
    def __init__(self, message: str = "Request timed out", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=504, original_error=original_error)


class LLMBadRequestError(LLMServiceError):
    """T038: Bad request error → 400"""
    def __init__(self, message: str = "Message could not be processed", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=400, original_error=original_error)


def load_config() -> Dict[str, str]:
    """
    T007: Load LLM configuration from environment variables.

    Loads OPENAI_API_KEY (required) and OPENAI_MODEL (optional, defaults to gpt-3.5-turbo).

    Returns:
        Dictionary with 'api_key' and 'model' keys

    Raises:
        ValueError: If OPENAI_API_KEY is not set

    Examples:
        >>> # With environment: OPENAI_API_KEY=sk-abc123, OPENAI_MODEL=gpt-4
        >>> config = load_config()
        >>> config['api_key']
        'sk-abc123'
        >>> config['model']
        'gpt-4'
    """
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        raise ValueError(
            "OPENAI_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )

    # Default to gpt-3.5-turbo if OPENAI_MODEL not specified
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    logger.info(f"Loaded LLM config: model={model}, api_key={'*' * 8}...{api_key[-4:]}")

    return {
        'api_key': api_key,
        'model': model
    }


def initialize_llm(api_key: str, model: str) -> ChatOpenAI:
    """
    T006: Initialize ChatOpenAI instance with provided configuration.

    Creates and configures a LangChain ChatOpenAI instance for message processing.

    Args:
        api_key: OpenAI API key
        model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')

    Returns:
        Configured ChatOpenAI instance

    Examples:
        >>> llm = initialize_llm(api_key="sk-test-key", model="gpt-3.5-turbo")
        >>> type(llm).__name__
        'ChatOpenAI'
    """
    logger.info(f"Initializing ChatOpenAI with model: {model}")

    llm = ChatOpenAI(
        api_key=api_key,
        model=model,
        timeout=120,  # 2 minutes - allows time for large responses while preventing infinite hangs
        request_timeout=120  # Alternative parameter for compatibility across SDK versions
    )

    logger.info("ChatOpenAI initialized successfully")
    return llm


def get_llm_instance() -> ChatOpenAI:
    """
    T006: Get or create singleton LLM instance.

    Returns cached LLM instance if available, otherwise creates new instance
    from environment configuration. This ensures we reuse the same instance
    across requests for better performance.

    Returns:
        ChatOpenAI instance

    Raises:
        ValueError: If configuration is missing or invalid

    Examples:
        >>> llm1 = get_llm_instance()
        >>> llm2 = get_llm_instance()
        >>> llm1 is llm2  # Same instance
        True
    """
    global _llm_instance

    if _llm_instance is None:
        logger.info("Creating new LLM instance from environment config")
        config = load_config()
        _llm_instance = initialize_llm(
            api_key=config['api_key'],
            model=config['model']
        )
    else:
        logger.debug("Returning cached LLM instance")

    return _llm_instance


def convert_to_langchain_messages(history: List[Dict[str, str]]) -> List[BaseMessage]:
    """
    T022: Convert conversation history to LangChain message format.

    Converts an array of message objects with sender/text fields into
    LangChain message types (HumanMessage for user, AIMessage for system).

    Args:
        history: List of message dictionaries with "sender" and "text" fields
                 sender can be "user" or "system"

    Returns:
        List of LangChain message objects (HumanMessage or AIMessage)

    Examples:
        >>> history = [
        ...     {"sender": "user", "text": "Hello"},
        ...     {"sender": "system", "text": "Hi there!"}
        ... ]
        >>> messages = convert_to_langchain_messages(history)
        >>> isinstance(messages[0], HumanMessage)
        True
        >>> isinstance(messages[1], AIMessage)
        True
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


async def get_ai_response(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    model: Optional[str] = None
) -> tuple[str, str]:
    """
    T013, T021-T023, T034-T040: Get AI response for a user message with error handling.

    Sends the user message to OpenAI ChatGPT via LangChain and returns
    the AI-generated response. Maps OpenAI exceptions to user-friendly errors.

    Feature 008: Extended to support per-request model selection (T021-T023).

    Args:
        message: User message text
        history: Optional list of previous messages with sender/text fields
                 for context-aware responses (T023)
        model: Optional model ID to use for this request (T021).
               If not provided, uses the configured default model.

    Returns:
        Tuple of (AI-generated response text, model ID used)

    Raises:
        LLMAuthenticationError: If API key is invalid (T034) → 503
        LLMRateLimitError: If rate limit exceeded (T035) → 503
        LLMConnectionError: If cannot reach API (T036) → 503
        LLMTimeoutError: If request times out (T037) → 504
        LLMBadRequestError: If request is malformed (T038) → 400
        ValueError: If message is empty or model is invalid (T022)

    Examples:
        >>> import asyncio
        >>> response, model_used = asyncio.run(get_ai_response("Hello"))
        >>> len(response) > 0
        True
        >>> model_used in ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        True

        >>> # With specific model
        >>> response, model_used = asyncio.run(get_ai_response("Hello", model="gpt-4"))
        >>> model_used
        'gpt-4'
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    logger.info(f"Processing AI request for message: {message[:50]}...")
    if history:
        logger.info(f"Including {len(history)} message(s) from conversation history")

    try:
        # Load model configuration (T022)
        config = load_model_configuration()

        # Determine which model to use (T021, T047)
        if model:
            model_to_use = model
            logger.info(f"User-selected model: {model_to_use}")
        else:
            model_to_use = get_default_model(config)
            logger.info(f"Using default model: {model_to_use}")

        # Validate model against configuration (T022)
        if not validate_model_id(model_to_use, config):
            available_models = [m.id for m in config.models]
            logger.error(f"Invalid model requested: {model_to_use}. Available: {', '.join(available_models)}")
            raise ValueError(
                f"Invalid model: {model_to_use}. "
                f"Available models: {', '.join(available_models)}"
            )

        # Load API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )

        # Create per-request ChatOpenAI instance with specified model (T023)
        # Note: We no longer use the singleton pattern to support per-request model selection
        logger.debug(f"Creating ChatOpenAI instance for model: {model_to_use}")
        llm = ChatOpenAI(
            api_key=api_key,
            model=model_to_use,
            timeout=120,  # 2 minutes - allows time for large responses while preventing infinite hangs
            request_timeout=120  # Alternative parameter for compatibility across SDK versions
        )

        # Build conversation history (T023: include previous messages if provided)
        conversation = history.copy() if history else []
        # Add current user message to conversation
        conversation.append({"sender": "user", "text": message})

        # Convert to LangChain format (T012, T022)
        langchain_messages = convert_to_langchain_messages(conversation)

        # Call LLM service
        logger.debug(f"Invoking ChatOpenAI with {len(langchain_messages)} message(s)")
        response = await llm.ainvoke(langchain_messages)

        # Extract content from response
        ai_response = response.content
        logger.info(f"AI response received: {len(ai_response)} characters")
        logger.debug(f"AI response preview: {ai_response[:100]}...")

        return ai_response, model_to_use

    except AuthenticationError as e:
        # T034, T040: Map AuthenticationError → 503 with sanitized message
        logger.error(f"LLM authentication failed: {type(e).__name__}")
        raise LLMAuthenticationError(original_error=e)

    except RateLimitError as e:
        # T035, T040: Map RateLimitError → 503 with sanitized message
        logger.error(f"LLM rate limit exceeded: {type(e).__name__}")
        raise LLMRateLimitError(original_error=e)

    except APIConnectionError as e:
        # T036, T040: Map APIConnectionError → 503 with sanitized message
        logger.error(f"LLM connection failed: {type(e).__name__}")
        raise LLMConnectionError(original_error=e)

    except (APITimeoutError, asyncio.TimeoutError) as e:
        # T037, T040: Map timeout errors → 504 with sanitized message
        logger.error(f"LLM request timed out: {type(e).__name__}")
        raise LLMTimeoutError(original_error=e)

    except BadRequestError as e:
        # T038, T040: Map BadRequestError → 400 with sanitized message
        logger.error(f"LLM bad request: {type(e).__name__}: {str(e)}")
        raise LLMBadRequestError(original_error=e)

    except Exception as e:
        # T040: Log unexpected errors (sanitized)
        logger.error(f"Unexpected LLM error: {type(e).__name__}: {str(e)}")
        # Re-raise as generic LLM error
        raise LLMServiceError("AI service error occurred", original_error=e)
