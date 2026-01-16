"""
Tests for Provider Error Mapping Module

Tests for unified error mapping from provider-specific exceptions to LLMServiceError.

Feature: 012-modular-model-providers
User Story: US2 - Consolidated Error Handling
"""

import pytest
from unittest.mock import MagicMock


class TestOpenAIErrorMapping:
    """Tests for OpenAI exception to LLMServiceError mapping."""

    def test_map_openai_authentication_error(self):
        """Test that OpenAI AuthenticationError maps to LLMAuthenticationError."""
        from openai import AuthenticationError
        from src.services.providers.errors import map_openai_error
        from src.services.llm_service import LLMAuthenticationError

        # Create a mock OpenAI AuthenticationError
        mock_error = MagicMock(spec=AuthenticationError)
        mock_error.__class__ = AuthenticationError

        result = map_openai_error(mock_error)

        assert isinstance(result, LLMAuthenticationError)
        assert result.original_error is mock_error

    def test_map_openai_rate_limit_error(self):
        """Test that OpenAI RateLimitError maps to LLMRateLimitError."""
        from openai import RateLimitError
        from src.services.providers.errors import map_openai_error
        from src.services.llm_service import LLMRateLimitError

        mock_error = MagicMock(spec=RateLimitError)
        mock_error.__class__ = RateLimitError

        result = map_openai_error(mock_error)

        assert isinstance(result, LLMRateLimitError)
        assert result.original_error is mock_error

    def test_map_openai_connection_error(self):
        """Test that OpenAI APIConnectionError maps to LLMConnectionError."""
        from openai import APIConnectionError
        from src.services.providers.errors import map_openai_error
        from src.services.llm_service import LLMConnectionError

        mock_error = MagicMock(spec=APIConnectionError)
        mock_error.__class__ = APIConnectionError

        result = map_openai_error(mock_error)

        assert isinstance(result, LLMConnectionError)
        assert result.original_error is mock_error

    def test_map_openai_timeout_error(self):
        """Test that OpenAI APITimeoutError maps to LLMTimeoutError."""
        from openai import APITimeoutError
        from src.services.providers.errors import map_openai_error
        from src.services.llm_service import LLMTimeoutError

        mock_error = MagicMock(spec=APITimeoutError)
        mock_error.__class__ = APITimeoutError

        result = map_openai_error(mock_error)

        assert isinstance(result, LLMTimeoutError)
        assert result.original_error is mock_error

    def test_map_openai_bad_request_error(self):
        """Test that OpenAI BadRequestError maps to LLMBadRequestError."""
        from openai import BadRequestError
        from src.services.providers.errors import map_openai_error
        from src.services.llm_service import LLMBadRequestError

        mock_error = MagicMock(spec=BadRequestError)
        mock_error.__class__ = BadRequestError

        result = map_openai_error(mock_error)

        assert isinstance(result, LLMBadRequestError)
        assert result.original_error is mock_error

    def test_map_openai_unknown_error(self):
        """Test that unknown OpenAI errors map to generic LLMServiceError."""
        from src.services.providers.errors import map_openai_error
        from src.services.llm_service import LLMServiceError

        mock_error = Exception("Unknown error")

        result = map_openai_error(mock_error)

        assert isinstance(result, LLMServiceError)
        assert result.original_error is mock_error


class TestAnthropicErrorMapping:
    """Tests for Anthropic exception to LLMServiceError mapping."""

    def test_map_anthropic_authentication_error(self):
        """Test that Anthropic AuthenticationError maps to LLMAuthenticationError."""
        from anthropic import AuthenticationError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMAuthenticationError

        mock_error = MagicMock(spec=AuthenticationError)
        mock_error.__class__ = AuthenticationError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMAuthenticationError)
        assert result.original_error is mock_error

    def test_map_anthropic_rate_limit_error(self):
        """Test that Anthropic RateLimitError maps to LLMRateLimitError."""
        from anthropic import RateLimitError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMRateLimitError

        mock_error = MagicMock(spec=RateLimitError)
        mock_error.__class__ = RateLimitError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMRateLimitError)
        assert result.original_error is mock_error

    def test_map_anthropic_connection_error(self):
        """Test that Anthropic APIConnectionError maps to LLMConnectionError."""
        from anthropic import APIConnectionError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMConnectionError

        mock_error = MagicMock(spec=APIConnectionError)
        mock_error.__class__ = APIConnectionError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMConnectionError)
        assert result.original_error is mock_error

    def test_map_anthropic_timeout_error(self):
        """Test that Anthropic APITimeoutError maps to LLMTimeoutError."""
        from anthropic import APITimeoutError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMTimeoutError

        mock_error = MagicMock(spec=APITimeoutError)
        mock_error.__class__ = APITimeoutError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMTimeoutError)
        assert result.original_error is mock_error

    def test_map_anthropic_bad_request_error(self):
        """Test that Anthropic BadRequestError maps to LLMBadRequestError."""
        from anthropic import BadRequestError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMBadRequestError

        mock_error = MagicMock(spec=BadRequestError)
        mock_error.__class__ = BadRequestError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMBadRequestError)
        assert result.original_error is mock_error


class TestAnthropicSpecificErrors:
    """Tests for Anthropic-specific errors that don't exist in OpenAI."""

    def test_map_anthropic_not_found_error(self):
        """Test that Anthropic NotFoundError maps to LLMBadRequestError."""
        from anthropic import NotFoundError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMBadRequestError

        mock_error = MagicMock(spec=NotFoundError)
        mock_error.__class__ = NotFoundError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMBadRequestError)
        assert result.original_error is mock_error

    def test_map_anthropic_permission_denied_error(self):
        """Test that Anthropic PermissionDeniedError maps to LLMAuthenticationError."""
        from anthropic import PermissionDeniedError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMAuthenticationError

        mock_error = MagicMock(spec=PermissionDeniedError)
        mock_error.__class__ = PermissionDeniedError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMAuthenticationError)
        assert result.original_error is mock_error

    def test_map_anthropic_internal_server_error(self):
        """Test that Anthropic InternalServerError maps to LLMServiceError."""
        from anthropic import InternalServerError
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMServiceError

        mock_error = MagicMock(spec=InternalServerError)
        mock_error.__class__ = InternalServerError

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMServiceError)
        assert result.original_error is mock_error

    def test_map_anthropic_unknown_error(self):
        """Test that unknown Anthropic errors map to generic LLMServiceError."""
        from src.services.providers.errors import map_anthropic_error
        from src.services.llm_service import LLMServiceError

        mock_error = Exception("Unknown error")

        result = map_anthropic_error(mock_error)

        assert isinstance(result, LLMServiceError)
        assert result.original_error is mock_error


class TestGenericErrorMapping:
    """Tests for the generic map_provider_error function."""

    def test_map_provider_error_routes_to_openai(self):
        """Test that map_provider_error routes OpenAI errors correctly."""
        from openai import AuthenticationError
        from src.services.providers.errors import map_provider_error
        from src.services.llm_service import LLMAuthenticationError

        mock_error = MagicMock(spec=AuthenticationError)
        mock_error.__class__ = AuthenticationError

        result = map_provider_error(mock_error, "openai")

        assert isinstance(result, LLMAuthenticationError)

    def test_map_provider_error_routes_to_anthropic(self):
        """Test that map_provider_error routes Anthropic errors correctly."""
        from anthropic import AuthenticationError
        from src.services.providers.errors import map_provider_error
        from src.services.llm_service import LLMAuthenticationError

        mock_error = MagicMock(spec=AuthenticationError)
        mock_error.__class__ = AuthenticationError

        result = map_provider_error(mock_error, "anthropic")

        assert isinstance(result, LLMAuthenticationError)

    def test_map_provider_error_unknown_provider_returns_generic(self):
        """Test that unknown provider returns generic LLMServiceError."""
        from src.services.providers.errors import map_provider_error
        from src.services.llm_service import LLMServiceError

        mock_error = Exception("Unknown error")

        result = map_provider_error(mock_error, "unknown-provider")

        assert isinstance(result, LLMServiceError)
        assert result.original_error is mock_error
