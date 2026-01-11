"""
LLM Service - OpenAI ChatGPT Integration via LangChain

Manages LLM initialization, configuration, and message processing.

Feature: 006-openai-langchain-chat Phase 2 (Foundational)
Tasks: T006, T007
"""

import os
import asyncio
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from openai import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    BadRequestError,
    APITimeoutError
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Module-level cache for LLM instance (singleton pattern)
_llm_instance: Optional[ChatOpenAI] = None


# Custom exception classes for LLM errors (T034-T038)
class LLMServiceError(Exception):
    """Base exception for LLM service errors"""
    def __init__(self, message: str, status_code: int = 503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LLMAuthenticationError(LLMServiceError):
    """T034: Authentication/configuration error → 503"""
    def __init__(self, message: str = "AI service configuration error"):
        super().__init__(message, status_code=503)


class LLMRateLimitError(LLMServiceError):
    """T035: Rate limit error → 503"""
    def __init__(self, message: str = "AI service is busy"):
        super().__init__(message, status_code=503)


class LLMConnectionError(LLMServiceError):
    """T036: Connection error → 503"""
    def __init__(self, message: str = "Unable to reach AI service"):
        super().__init__(message, status_code=503)


class LLMTimeoutError(LLMServiceError):
    """T037: Timeout error → 504"""
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, status_code=504)


class LLMBadRequestError(LLMServiceError):
    """T038: Bad request error → 400"""
    def __init__(self, message: str = "Message could not be processed"):
        super().__init__(message, status_code=400)


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
        model=model
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


def convert_to_langchain_messages(message: str) -> list:
    """
    T006: Convert user message to LangChain message format.

    Converts a simple string message into the list format expected by
    LangChain's ChatOpenAI.ainvoke() method.

    Args:
        message: User message text

    Returns:
        List of message dictionaries in LangChain format

    Examples:
        >>> messages = convert_to_langchain_messages("Hello")
        >>> isinstance(messages, list)
        True
        >>> len(messages) > 0
        True
    """
    logger.debug(f"Converting message to LangChain format: {message[:50]}...")

    # LangChain expects a list of messages
    # For now, just convert the single message to proper format
    # Future: This will be extended to handle conversation history (User Story 2)
    messages = [
        {"role": "user", "content": message}
    ]

    logger.debug(f"Converted to {len(messages)} LangChain message(s)")
    return messages


async def get_ai_response(message: str) -> str:
    """
    T013, T034-T040: Get AI response for a user message with error handling.

    Sends the user message to OpenAI ChatGPT via LangChain and returns
    the AI-generated response. Maps OpenAI exceptions to user-friendly errors.

    Args:
        message: User message text

    Returns:
        AI-generated response text

    Raises:
        LLMAuthenticationError: If API key is invalid (T034) → 503
        LLMRateLimitError: If rate limit exceeded (T035) → 503
        LLMConnectionError: If cannot reach API (T036) → 503
        LLMTimeoutError: If request times out (T037) → 504
        LLMBadRequestError: If request is malformed (T038) → 400
        ValueError: If message is empty

    Examples:
        >>> import asyncio
        >>> response = asyncio.run(get_ai_response("Hello"))
        >>> len(response) > 0
        True
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    logger.info(f"Processing AI request for message: {message[:50]}...")

    try:
        # Get LLM instance
        llm = get_llm_instance()

        # Convert message to LangChain format
        langchain_messages = convert_to_langchain_messages(message)

        # Call LLM service
        logger.debug(f"Invoking ChatOpenAI with {len(langchain_messages)} message(s)")
        response = await llm.ainvoke(langchain_messages)

        # Extract content from response
        ai_response = response.content
        logger.info(f"AI response received: {len(ai_response)} characters")
        logger.debug(f"AI response preview: {ai_response[:100]}...")

        return ai_response

    except AuthenticationError as e:
        # T034, T040: Map AuthenticationError → 503 with sanitized message
        logger.error(f"LLM authentication failed: {type(e).__name__}")
        raise LLMAuthenticationError()

    except RateLimitError as e:
        # T035, T040: Map RateLimitError → 503 with sanitized message
        logger.error(f"LLM rate limit exceeded: {type(e).__name__}")
        raise LLMRateLimitError()

    except APIConnectionError as e:
        # T036, T040: Map APIConnectionError → 503 with sanitized message
        logger.error(f"LLM connection failed: {type(e).__name__}")
        raise LLMConnectionError()

    except (APITimeoutError, asyncio.TimeoutError) as e:
        # T037, T040: Map timeout errors → 504 with sanitized message
        logger.error(f"LLM request timed out: {type(e).__name__}")
        raise LLMTimeoutError()

    except BadRequestError as e:
        # T038, T040: Map BadRequestError → 400 with sanitized message
        logger.error(f"LLM bad request: {type(e).__name__}")
        raise LLMBadRequestError()

    except Exception as e:
        # T040: Log unexpected errors (sanitized)
        logger.error(f"Unexpected LLM error: {type(e).__name__}")
        # Re-raise as generic LLM error
        raise LLMServiceError("AI service error occurred")
