"""
OpenAI Provider Unit Tests

Tests for the OpenAI provider implementation.

Feature: 012-modular-model-providers
User Story: US3 - Provider Factory Pattern
Task: T023
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os


@pytest.mark.unit
class TestOpenAIProviderCreateLLM:
    """Tests for OpenAIProvider.create_llm() method."""

    def test_create_llm_returns_chat_openai_instance(self):
        """
        T023: create_llm() returns a ChatOpenAI instance.

        Validates that:
        - create_llm() creates a ChatOpenAI instance
        - Correct model ID is passed
        - Correct API key is used
        """
        from src.services.providers.openai import OpenAIProvider

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.services.providers.openai.ChatOpenAI') as mock_chat:
                mock_instance = Mock()
                mock_chat.return_value = mock_instance

                provider = OpenAIProvider()
                llm = provider.create_llm("gpt-4")

                mock_chat.assert_called_once_with(
                    api_key="test-key",
                    model="gpt-4",
                    timeout=120,
                    request_timeout=120
                )
                assert llm == mock_instance

    def test_create_llm_raises_error_when_api_key_missing(self):
        """
        T023: create_llm() raises LLMAuthenticationError when API key missing.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMAuthenticationError

        with patch.dict('os.environ', {}, clear=True):
            provider = OpenAIProvider()

            with pytest.raises(LLMAuthenticationError, match="OpenAI API key not configured"):
                provider.create_llm("gpt-4")

    def test_create_llm_with_different_models(self):
        """
        T023: create_llm() works with different model IDs.
        """
        from src.services.providers.openai import OpenAIProvider

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.services.providers.openai.ChatOpenAI') as mock_chat:
                mock_chat.return_value = Mock()

                provider = OpenAIProvider()

                # Test with gpt-3.5-turbo
                provider.create_llm("gpt-3.5-turbo")
                call_args = mock_chat.call_args
                assert call_args.kwargs['model'] == "gpt-3.5-turbo"

                mock_chat.reset_mock()

                # Test with gpt-4-turbo
                provider.create_llm("gpt-4-turbo")
                call_args = mock_chat.call_args
                assert call_args.kwargs['model'] == "gpt-4-turbo"


@pytest.mark.unit
class TestOpenAIProviderMapError:
    """Tests for OpenAIProvider.map_error() method."""

    def test_map_error_authentication_error(self):
        """
        T023: map_error() maps AuthenticationError to LLMAuthenticationError.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMAuthenticationError
        from openai import AuthenticationError

        provider = OpenAIProvider()

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
        T023: map_error() maps RateLimitError to LLMRateLimitError.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMRateLimitError
        from openai import RateLimitError

        provider = OpenAIProvider()

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
        T023: map_error() maps APITimeoutError to LLMTimeoutError.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMTimeoutError
        from openai import APITimeoutError

        provider = OpenAIProvider()

        original = APITimeoutError(request=Mock())
        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMTimeoutError)
        assert mapped.original_error == original

    def test_map_error_connection_error(self):
        """
        T023: map_error() maps APIConnectionError to LLMConnectionError.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMConnectionError
        from openai import APIConnectionError

        provider = OpenAIProvider()

        original = APIConnectionError(request=Mock())
        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMConnectionError)
        assert mapped.original_error == original

    def test_map_error_bad_request_error(self):
        """
        T023: map_error() maps BadRequestError to LLMBadRequestError.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMBadRequestError
        from openai import BadRequestError

        provider = OpenAIProvider()

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

    def test_map_error_unknown_error(self):
        """
        T023: map_error() maps unknown errors to generic LLMServiceError.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.llm_service import LLMServiceError

        provider = OpenAIProvider()

        original = ValueError("Some unexpected error")
        mapped = provider.map_error(original)

        assert isinstance(mapped, LLMServiceError)
        assert mapped.original_error == original


@pytest.mark.unit
class TestOpenAIProviderGetConfig:
    """Tests for OpenAIProvider.get_config() method."""

    def test_get_config_returns_provider_config(self):
        """
        T023: get_config() returns a ProviderConfig instance.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.providers.base import ProviderConfig

        provider = OpenAIProvider()
        config = provider.get_config()

        assert isinstance(config, ProviderConfig)
        assert config.id == "openai"
        assert config.name == "OpenAI"
        assert config.api_key_env == "OPENAI_API_KEY"
        assert config.models_env == "OPENAI_MODELS"

    def test_get_config_enabled_when_api_key_present(self):
        """
        T023: get_config().is_enabled() returns True when API key is set.
        """
        from src.services.providers.openai import OpenAIProvider

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()
            config = provider.get_config()

            assert config.is_enabled() is True

    def test_get_config_disabled_when_api_key_missing(self):
        """
        T023: get_config().is_enabled() returns False when API key is missing.
        """
        from src.services.providers.openai import OpenAIProvider

        with patch.dict('os.environ', {}, clear=True):
            provider = OpenAIProvider()
            config = provider.get_config()

            assert config.is_enabled() is False


@pytest.mark.unit
class TestOpenAIProviderProperties:
    """Tests for OpenAIProvider properties."""

    def test_provider_id_property(self):
        """
        T023: provider_id property returns 'openai'.
        """
        from src.services.providers.openai import OpenAIProvider

        provider = OpenAIProvider()

        assert provider.provider_id == "openai"

    def test_implements_base_provider_protocol(self):
        """
        T023: OpenAIProvider implements BaseProvider protocol.
        """
        from src.services.providers.openai import OpenAIProvider
        from src.services.providers.base import BaseProvider

        provider = OpenAIProvider()

        # Check it has all required methods/properties
        assert hasattr(provider, 'provider_id')
        assert hasattr(provider, 'create_llm')
        assert hasattr(provider, 'map_error')
        assert hasattr(provider, 'get_config')

        # Verify it passes isinstance check with Protocol
        assert isinstance(provider, BaseProvider)
