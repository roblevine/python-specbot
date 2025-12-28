"""
Unit Tests for Message Service

Tests business logic for message processing in isolation.

Feature: 003-backend-api-loopback User Story 1
Tests: T027-T028 (TDD - these should FAIL before implementation)
"""

import pytest


@pytest.mark.unit
def test_loopback_message_adds_api_prefix():
    """
    T027: Unit test for loopback message creation with "api says: " prefix.

    Validates FR-002: Backend echoes messages with "api says: " prefix.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.message_service import create_loopback_message

    # Test basic message
    result = create_loopback_message("Hello world")
    assert result == "api says: Hello world"

    # Test empty-ish input (should still work at service level)
    result = create_loopback_message("Test")
    assert result == "api says: Test"


@pytest.mark.unit
def test_loopback_preserves_content():
    """
    T028: Unit test verifying message content is preserved exactly.

    Validates FR-011: No truncation or modification except prefix.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.message_service import create_loopback_message

    # Test with special characters
    msg_with_special = "Hello 🚀 World! @#$%^&*()"
    result = create_loopback_message(msg_with_special)
    assert result == f"api says: {msg_with_special}"

    # Test with newlines
    msg_with_newlines = "Line 1\nLine 2\nLine 3"
    result = create_loopback_message(msg_with_newlines)
    assert result == f"api says: {msg_with_newlines}"

    # Test with unicode
    msg_with_unicode = "Hello 世界 مرحبا שלום"
    result = create_loopback_message(msg_with_unicode)
    assert result == f"api says: {msg_with_unicode}"

    # Test with tabs and spaces
    msg_with_whitespace = "  Leading spaces\tand tabs  "
    result = create_loopback_message(msg_with_whitespace)
    assert result == f"api says: {msg_with_whitespace}"


@pytest.mark.unit
def test_message_validation_empty_string():
    """
    Test that empty strings are rejected by validation.

    Validates FR-012: Backend validates and rejects malformed requests.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.message_service import validate_message

    # Empty string should raise error
    with pytest.raises(ValueError, match="Message cannot be empty"):
        validate_message("")


@pytest.mark.unit
def test_message_validation_whitespace_only():
    """
    Test that whitespace-only messages are rejected.

    Validates FR-012: Backend validates and rejects malformed requests.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.message_service import validate_message

    # Whitespace-only should raise error
    with pytest.raises(ValueError, match="Message cannot be only whitespace"):
        validate_message("   ")

    with pytest.raises(ValueError, match="Message cannot be only whitespace"):
        validate_message("\n\n\n")

    with pytest.raises(ValueError, match="Message cannot be only whitespace"):
        validate_message("\t\t\t")


@pytest.mark.unit
def test_message_validation_too_long():
    """
    Test that messages exceeding 10,000 characters are rejected.

    Validates FR-007: Reject messages > 10,000 chars.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.message_service import validate_message

    # Create message > 10,000 chars
    long_message = "a" * 10001

    with pytest.raises(ValueError, match="Message exceeds maximum length"):
        validate_message(long_message)


@pytest.mark.unit
def test_message_validation_valid_messages():
    """
    Test that valid messages pass validation.

    Expected: FAIL (service not implemented yet)
    """
    from src.services.message_service import validate_message

    # Valid messages should not raise errors
    validate_message("Hello")
    validate_message("Hello world")
    validate_message("Hello 🚀")
    validate_message("Line 1\nLine 2")
    validate_message("a" * 10000)  # Exactly 10,000 chars (should be valid)
