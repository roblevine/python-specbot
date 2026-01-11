"""
Structured logging setup for SpecBot Backend API

Provides consistent logging across all modules with DEBUG, INFO, and ERROR levels.
Implements FR-014: Backend logs all incoming requests and responses for debugging.
"""

import logging
import os
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger with structured formatting.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    if level is None:
        level = os.getenv("LOG_LEVEL", "DEBUG").upper()

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.DEBUG))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level, logging.DEBUG))

    # Create formatter with timestamp, level, module, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False

    return logger


# Module-level logger for this file
logger = get_logger(__name__)


def llm_request_start(message: str, model: str) -> None:
    """
    T008: Log the start of an LLM request.

    Logs when a request is being sent to the LLM service,
    including the model and a preview of the message.

    Args:
        message: User message being sent
        model: LLM model being used

    Examples:
        >>> llm_request_start("Hello, how are you?", "gpt-3.5-turbo")
        # Logs: "LLM request starting: model=gpt-3.5-turbo, message_length=19"
    """
    logger.info(
        f"LLM request starting: model={model}, "
        f"message_length={len(message)}, "
        f"preview={message[:50]}..."
    )


def llm_request_complete(message: str, response: str, model: str, duration_ms: float) -> None:
    """
    T008: Log the successful completion of an LLM request.

    Logs when an LLM request completes successfully, including
    response metadata and timing information.

    Args:
        message: Original user message
        response: LLM response content
        model: LLM model used
        duration_ms: Request duration in milliseconds

    Examples:
        >>> llm_request_complete(
        ...     "Hello", "Hi there!", "gpt-3.5-turbo", 1234.5
        ... )
        # Logs: "LLM request completed: model=gpt-3.5-turbo, duration=1234.5ms, ..."
    """
    logger.info(
        f"LLM request completed: model={model}, "
        f"duration={duration_ms:.2f}ms, "
        f"message_length={len(message)}, "
        f"response_length={len(response)}"
    )
    logger.debug(f"LLM response preview: {response[:100]}...")


def llm_request_error(message: str, model: str, error: Exception) -> None:
    """
    T008: Log an error during LLM request processing.

    Logs when an LLM request fails, with sanitized error information
    that does not expose sensitive data (API keys, internal details).

    Args:
        message: Original user message
        model: LLM model being used
        error: Exception that occurred

    Examples:
        >>> llm_request_error("Hello", "gpt-3.5-turbo", ValueError("API key invalid"))
        # Logs: "LLM request failed: model=gpt-3.5-turbo, error_type=ValueError"
    """
    error_type = type(error).__name__
    error_message = str(error)

    # Sanitize error message to avoid exposing API keys or sensitive data
    # Replace any strings that look like API keys (sk-...)
    import re
    sanitized_error = re.sub(r'sk-[a-zA-Z0-9]+', 'sk-***REDACTED***', error_message)

    logger.error(
        f"LLM request failed: model={model}, "
        f"error_type={error_type}, "
        f"message_length={len(message)}, "
        f"error={sanitized_error}"
    )
    logger.debug(f"Failed message preview: {message[:50]}...")
