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


# ============================================================================
# Streaming Logging Functions (Feature: 009-message-streaming)
# ============================================================================

def log_stream_start(message_id: str, model: str) -> None:
    """
    T010: Log the start of a streaming LLM response.

    Logs when a streaming request begins, including the message ID
    and model being used. Useful for tracking streaming session lifecycle.

    Feature: 009-message-streaming Task T010

    Args:
        message_id: Unique identifier for the message/stream
        model: LLM model being used for streaming

    Examples:
        >>> log_stream_start("msg-123", "gpt-4")
        # Logs: "Stream started: message_id=msg-123, model=gpt-4"
    """
    logger.info(
        f"Stream started: message_id={message_id}, "
        f"model={model}"
    )


def log_stream_token(message_id: str, token_count: int) -> None:
    """
    T010: Log streaming token progress.

    Logs periodic updates during streaming to track token generation progress.
    Should be called periodically (e.g., every 10 tokens) to avoid log spam.

    Feature: 009-message-streaming Task T010

    Args:
        message_id: Unique identifier for the message/stream
        token_count: Number of tokens streamed so far

    Examples:
        >>> log_stream_token("msg-123", 50)
        # Logs: "Stream progress: message_id=msg-123, tokens=50"
    """
    logger.debug(
        f"Stream progress: message_id={message_id}, "
        f"tokens={token_count}"
    )


def log_stream_complete(message_id: str, duration_ms: float, total_tokens: int) -> None:
    """
    T010: Log the successful completion of a streaming response.

    Logs when a streaming session completes successfully, including
    timing and token count information for performance monitoring.

    Feature: 009-message-streaming Task T010

    Args:
        message_id: Unique identifier for the message/stream
        duration_ms: Total streaming duration in milliseconds
        total_tokens: Total number of tokens streamed

    Examples:
        >>> log_stream_complete("msg-123", 2345.6, 150)
        # Logs: "Stream completed: message_id=msg-123, duration=2345.60ms, total_tokens=150"
    """
    logger.info(
        f"Stream completed: message_id={message_id}, "
        f"duration={duration_ms:.2f}ms, "
        f"total_tokens={total_tokens}"
    )


def log_stream_error(message_id: str, error: Exception, tokens_sent: int = 0) -> None:
    """
    T010: Log an error during streaming response.

    Logs when a streaming session fails, with sanitized error information
    and count of tokens successfully sent before the error.

    Feature: 009-message-streaming Task T010

    Args:
        message_id: Unique identifier for the message/stream
        error: Exception that occurred
        tokens_sent: Number of tokens successfully sent before error

    Examples:
        >>> log_stream_error("msg-123", TimeoutError("Connection lost"), 42)
        # Logs: "Stream failed: message_id=msg-123, error_type=TimeoutError, tokens_sent=42"
    """
    error_type = type(error).__name__
    error_message = str(error)

    # Sanitize error message to avoid exposing API keys or sensitive data
    import re
    sanitized_error = re.sub(r'sk-[a-zA-Z0-9]+', 'sk-***REDACTED***', error_message)

    logger.error(
        f"Stream failed: message_id={message_id}, "
        f"error_type={error_type}, "
        f"tokens_sent={tokens_sent}, "
        f"error={sanitized_error}"
    )
