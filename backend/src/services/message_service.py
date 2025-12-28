"""
Message Service - Business Logic for Message Processing

Implements loopback message creation and validation.

Feature: 003-backend-api-loopback User Story 1
Tasks: T033, T034
"""

from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_loopback_message(user_message: str) -> str:
    """
    T033: Create loopback message with "api says: " prefix.

    Implements FR-002: Backend echoes messages with "api says: " prefix.

    Args:
        user_message: The user's input message

    Returns:
        Message with "api says: " prefix

    Examples:
        >>> create_loopback_message("Hello world")
        'api says: Hello world'
        >>> create_loopback_message("Test 🚀")
        'api says: Test 🚀'
    """
    logger.debug(f"Creating loopback message for input: {user_message[:50]}...")
    return f"api says: {user_message}"


def validate_message(message: str) -> None:
    """
    T034: Validate message meets requirements.

    Implements FR-007, FR-012:
    - Rejects empty messages
    - Rejects whitespace-only messages
    - Rejects messages > 10,000 characters

    Args:
        message: The message to validate

    Raises:
        ValueError: If message fails validation

    Examples:
        >>> validate_message("Hello")  # OK
        >>> validate_message("")  # Raises ValueError
        >>> validate_message("   ")  # Raises ValueError
        >>> validate_message("a" * 10001)  # Raises ValueError
    """
    # Check if empty
    if not message:
        logger.warning("Validation failed: Empty message")
        raise ValueError("Message cannot be empty")

    # Check if whitespace-only
    if not message.strip():
        logger.warning("Validation failed: Whitespace-only message")
        raise ValueError("Message cannot be only whitespace")

    # Check length (max 10,000 characters per FR-007)
    if len(message) > 10000:
        logger.warning(f"Validation failed: Message too long ({len(message)} chars)")
        raise ValueError("Message exceeds maximum length of 10,000 characters")

    logger.debug(f"Message validation passed: {len(message)} chars")
