"""
Unit tests for streaming event schemas

Tests TokenEvent, CompleteEvent, ErrorEvent validation and SSE serialization.

Feature: 009-message-streaming
Task: T006
"""

import json
import pytest
from pydantic import ValidationError

from src.schemas import TokenEvent, CompleteEvent, ErrorEvent


class TestTokenEvent:
    """Test TokenEvent schema validation"""

    def test_token_event_valid(self):
        """Test valid TokenEvent creation"""
        event = TokenEvent(type="token", content="Hello")

        assert event.type == "token"
        assert event.content == "Hello"

    def test_token_event_missing_content(self):
        """Test TokenEvent requires content field"""
        with pytest.raises(ValidationError) as exc_info:
            TokenEvent(type="token")

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('content',) for e in errors)

    def test_token_event_empty_content_allowed(self):
        """Test TokenEvent allows empty string content"""
        event = TokenEvent(type="token", content="")
        assert event.content == ""

    def test_token_event_multiline_content(self):
        """Test TokenEvent handles multi-line content"""
        content = "Line 1\nLine 2\nLine 3"
        event = TokenEvent(type="token", content=content)
        assert event.content == content

    def test_token_event_special_characters(self):
        """Test TokenEvent handles special characters and emoji"""
        content = "Hello 🚀 World! @#$%^&*()"
        event = TokenEvent(type="token", content=content)
        assert event.content == content


class TestCompleteEvent:
    """Test CompleteEvent schema validation"""

    def test_complete_event_valid(self):
        """Test valid CompleteEvent creation"""
        event = CompleteEvent(type="complete", model="gpt-4")

        assert event.type == "complete"
        assert event.model == "gpt-4"

    def test_complete_event_with_total_tokens(self):
        """Test CompleteEvent with totalTokens field"""
        event = CompleteEvent(
            type="complete",
            model="gpt-3.5-turbo",
            totalTokens=150
        )

        assert event.type == "complete"
        assert event.model == "gpt-3.5-turbo"
        assert event.totalTokens == 150

    def test_complete_event_missing_model(self):
        """Test CompleteEvent requires model field"""
        with pytest.raises(ValidationError) as exc_info:
            CompleteEvent(type="complete")

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('model',) for e in errors)

    def test_complete_event_optional_total_tokens(self):
        """Test totalTokens is optional"""
        event = CompleteEvent(type="complete", model="gpt-4")
        assert event.totalTokens is None


class TestErrorEvent:
    """Test ErrorEvent schema validation"""

    def test_error_event_valid(self):
        """Test valid ErrorEvent creation"""
        event = ErrorEvent(
            type="error",
            error="Request timed out",
            code="TIMEOUT"
        )

        assert event.type == "error"
        assert event.error == "Request timed out"
        assert event.code == "TIMEOUT"

    def test_error_event_missing_error_message(self):
        """Test ErrorEvent requires error field"""
        with pytest.raises(ValidationError) as exc_info:
            ErrorEvent(type="error", code="TIMEOUT")

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('error',) for e in errors)

    def test_error_event_missing_code(self):
        """Test ErrorEvent requires code field"""
        with pytest.raises(ValidationError) as exc_info:
            ErrorEvent(type="error", error="Something went wrong")

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('code',) for e in errors)

    def test_error_event_valid_error_codes(self):
        """Test ErrorEvent accepts valid error codes"""
        valid_codes = [
            "TIMEOUT",
            "RATE_LIMIT",
            "LLM_ERROR",
            "AUTH_ERROR",
            "CONNECTION_ERROR",
            "UNKNOWN"
        ]

        for code in valid_codes:
            event = ErrorEvent(
                type="error",
                error="Test error",
                code=code
            )
            assert event.code == code


class TestSSESerialization:
    """Test SSE (Server-Sent Events) serialization format"""

    def test_token_event_sse_format(self):
        """Test TokenEvent serializes to SSE format"""
        event = TokenEvent(type="token", content="Hello")
        sse_string = event.to_sse_format()

        # SSE format: "data: <JSON>\n\n"
        assert sse_string.startswith("data: ")
        assert sse_string.endswith("\n\n")

        # Extract JSON and validate
        json_part = sse_string[6:-2]  # Remove "data: " and "\n\n"
        data = json.loads(json_part)
        assert data["type"] == "token"
        assert data["content"] == "Hello"

    def test_complete_event_sse_format(self):
        """Test CompleteEvent serializes to SSE format"""
        event = CompleteEvent(
            type="complete",
            model="gpt-4",
            totalTokens=100
        )
        sse_string = event.to_sse_format()

        assert sse_string.startswith("data: ")
        assert sse_string.endswith("\n\n")

        json_part = sse_string[6:-2]
        data = json.loads(json_part)
        assert data["type"] == "complete"
        assert data["model"] == "gpt-4"
        assert data["totalTokens"] == 100

    def test_error_event_sse_format(self):
        """Test ErrorEvent serializes to SSE format"""
        event = ErrorEvent(
            type="error",
            error="Connection lost",
            code="CONNECTION_ERROR"
        )
        sse_string = event.to_sse_format()

        assert sse_string.startswith("data: ")
        assert sse_string.endswith("\n\n")

        json_part = sse_string[6:-2]
        data = json.loads(json_part)
        assert data["type"] == "error"
        assert data["error"] == "Connection lost"
        assert data["code"] == "CONNECTION_ERROR"

    def test_sse_format_handles_newlines_in_content(self):
        """Test SSE format properly escapes newlines in JSON"""
        event = TokenEvent(type="token", content="Line 1\nLine 2")
        sse_string = event.to_sse_format()

        # JSON should escape newlines as \n
        assert "\\n" in sse_string

        # Validate it's valid SSE format
        json_part = sse_string[6:-2]
        data = json.loads(json_part)
        assert data["content"] == "Line 1\nLine 2"

    def test_sse_format_handles_special_characters(self):
        """Test SSE format handles special characters in JSON"""
        event = TokenEvent(
            type="token",
            content="Test \"quotes\" and 'apostrophes' and 🚀 emoji"
        )
        sse_string = event.to_sse_format()

        # Validate JSON is properly escaped
        json_part = sse_string[6:-2]
        data = json.loads(json_part)
        assert data["content"] == "Test \"quotes\" and 'apostrophes' and 🚀 emoji"
