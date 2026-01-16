"""
Anthropic Provider Unit Tests

Tests for the Anthropic provider implementation.

Feature: 012-modular-model-providers
User Story: US3 - Provider Factory Pattern
Task: T024
"""

import pytest
from unittest.mock import Mock, patch
import os


@pytest.mark.unit
class TestAnthropicProviderCreateLLM:
    """Tests for AnthropicProvider.create_llm() method."""

    def test_create_llm_returns_chat_anthropic_instance(self):
        """
        T024: create_llm() returns a ChatAnthropic instance.

        Validates that:
        - create_llm() creates a ChatAnthropic instance
        - Correct model ID is passed
        - Correct API key is used
        """
        from src.services.providers.anthropic import AnthropicProvider

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('src.services.providers.anthropic.ChatAnthropic') as mock_chat:
                mock_instance = Mock()
                mock_chat.return_value = mock_instance

                provider = AnthropicProvider()
                llm = provider.create_llm("claude-3-5-sonnet-20241022")

                mock_chat.assert_called_once_with(
                    api_key="test-key",
                    model="claude-3-5-sonnet-20241022",
                    timeout=120
                )
                assert llm == mock_instance

    def test_create_llm_raises_error_when_api_key_missing(self):
        """
        T024: create_llm() raises LLMAuthenticationError when API key missing.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMAuthenticationError

        with patch.dict('os.environ', {}, clear=True):
            provider = AnthropicProvider()

            with pytest.raises(LLMAuthenticationError, match="Anthropic API key not configured"):
                provider.create_llm("claude-3-5-sonnet-20241022")

    def test_create_llm_with_different_models(self):
        """
        T024: create_llm() works with different model IDs.
        """
        from src.services.providers.anthropic import AnthropicProvider

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('src.services.providers.anthropic.ChatAnthropic') as mock_chat:
                mock_chat.return_value = Mock()

                provider = AnthropicProvider()

                # Test with claude-3-5-sonnet
                provider.create_llm("claude-3-5-sonnet-20241022")
                call_args = mock_chat.call_args
                assert call_args.kwargs['model'] == "claude-3-5-sonnet-20241022"

                mock_chat.reset_mock()

                # Test with claude-3-haiku
                provider.create_llm("claude-3-haiku-20240307")
                call_args = mock_chat.call_args
                assert call_args.kwargs['model'] == "claude-3-haiku-20240307"


@pytest.mark.unit
class TestAnthropicProviderMapError:
    """Tests for AnthropicProvider.map_error() method."""

    def test_map_error_authentication_error(self):
        """
        T024: map_error() maps AuthenticationError to LLMAuthenticationError.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMAuthenticationError
        from anthropic import AuthenticationError

        provider = AnthropicProvider()

        mock_response = Mock()
        mock_response.status_code = 401
        original = AuthenticationError(
            "Invalid API key",
            response=mock_response,
            body={"error": {"message": "Invalid"}}
        )

        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMAuthenticationError)
        assert mapped.original_error == original

    def test_map_error_rate_limit_error(self):
        """
        T024: map_error() maps RateLimitError to LLMRateLimitError.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMRateLimitError
        from anthropic import RateLimitError

        provider = AnthropicProvider()

        mock_response = Mock()
        mock_response.status_code = 429
        original = RateLimitError(
            "Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit"}}
        )

        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMRateLimitError)
        assert mapped.original_error == original

    def test_map_error_timeout_error(self):
        """
        T024: map_error() maps APITimeoutError to LLMTimeoutError.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMTimeoutError
        from anthropic import APITimeoutError

        provider = AnthropicProvider()

        original = APITimeoutError(request=Mock())
        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMTimeoutError)
        assert mapped.original_error == original

    def test_map_error_connection_error(self):
        """
        T024: map_error() maps APIConnectionError to LLMConnectionError.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMConnectionError
        from anthropic import APIConnectionError

        provider = AnthropicProvider()

        original = APIConnectionError(request=Mock())
        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMConnectionError)
        assert mapped.original_error == original

    def test_map_error_bad_request_error(self):
        """
        T024: map_error() maps BadRequestError to LLMBadRequestError.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMBadRequestError
        from anthropic import BadRequestError

        provider = AnthropicProvider()

        mock_response = Mock()
        mock_response.status_code = 400
        original = BadRequestError(
            "Bad request",
            response=mock_response,
            body={"error": {"message": "Bad"}}
        )

        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMBadRequestError)
        assert mapped.original_error == original

    def test_map_error_not_found_error(self):
        """
        T024: map_error() maps NotFoundError to LLMBadRequestError.

        NotFoundError (404) is typically a model not found, which is
        a client-side error (bad request).
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMBadRequestError
        from anthropic import NotFoundError

        provider = AnthropicProvider()

        mock_response = Mock()
        mock_response.status_code = 404
        original = NotFoundError(
            "Model not found",
            response=mock_response,
            body={"error": {"message": "Not found"}}
        )

        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMBadRequestError)
        assert "not found" in mapped.message.lower()
        assert mapped.original_error == original

    def test_map_error_permission_denied_error(self):
        """
        T024: map_error() maps PermissionDeniedError to LLMAuthenticationError.

        PermissionDeniedError (403) is an auth/permissions issue.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMAuthenticationError
        from anthropic import PermissionDeniedError

        provider = AnthropicProvider()

        mock_response = Mock()
        mock_response.status_code = 403
        original = PermissionDeniedError(
            "Permission denied",
            response=mock_response,
            body={"error": {"message": "Forbidden"}}
        )

        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMAuthenticationError)
        assert "denied" in mapped.message.lower()
        assert mapped.original_error == original

    def test_map_error_internal_server_error(self):
        """
        T024: map_error() maps InternalServerError to LLMServiceError.

        InternalServerError (500) is a server-side issue.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMServiceError
        from anthropic import InternalServerError

        provider = AnthropicProvider()

        mock_response = Mock()
        mock_response.status_code = 500
        original = InternalServerError(
            "Internal server error",
            response=mock_response,
            body={"error": {"message": "Server error"}}
        )

        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMServiceError)
        assert "unavailable" in mapped.message.lower()
        assert mapped.original_error == original

    def test_map_error_unknown_error(self):
        """
        T024: map_error() maps unknown errors to generic LLMServiceError.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.llm_service import LLMServiceError

        provider = AnthropicProvider()

        original = ValueError("Some unexpected error")
        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMServiceError)
        assert mapped.original_error == original


@pytest.mark.unit
class TestAnthropicProviderGetConfig:
    """Tests for AnthropicProvider.get_config() method."""

    def test_get_config_returns_provider_config(self):
        """
        T024: get_config() returns a ProviderConfig instance.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.providers.base import ProviderConfig

        provider = AnthropicProvider()
        config = provider.get_config()

        assert isinstance(config, ProviderConfig)
        assert config.id == "anthropic"
        assert config.name == "Anthropic"
        assert config.api_key_env == "ANTHROPIC_API_KEY"
        assert config.models_env == "ANTHROPIC_MODELS"

    def test_get_config_enabled_when_api_key_present(self):
        """
        T024: get_config().is_enabled() returns True when API key is set.
        """
        from src.services.providers.anthropic import AnthropicProvider

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            provider = AnthropicProvider()
            config = provider.get_config()

            assert config.is_enabled() is True

    def test_get_config_disabled_when_api_key_missing(self):
        """
        T024: get_config().is_enabled() returns False when API key is missing.
        """
        from src.services.providers.anthropic import AnthropicProvider

        with patch.dict('os.environ', {}, clear=True):
            provider = AnthropicProvider()
            config = provider.get_config()

            assert config.is_enabled() is False


@pytest.mark.unit
class TestAnthropicProviderProperties:
    """Tests for AnthropicProvider properties."""

    def test_provider_id_property(self):
        """
        T024: provider_id property returns 'anthropic'.
        """
        from src.services.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider()

        assert provider.provider_id == "anthropic"

    def test_implements_base_provider_protocol(self):
        """
        T024: AnthropicProvider implements BaseProvider protocol.
        """
        from src.services.providers.anthropic import AnthropicProvider
        from src.services.providers.base import BaseProvider

        provider = AnthropicProvider()

        # Check it has all required methods/properties
        assert hasattr(provider, 'provider_id')
        assert hasattr(provider, 'create_llm')
        assert hasattr(provider, 'map_error')
        assert hasattr(provider, 'get_config')

        # Verify it passes isinstance check with Protocol
        assert isinstance(provider, BaseProvider)
