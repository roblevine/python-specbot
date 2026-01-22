"""
Unit Tests for Ollama Provider

Tests for OllamaProvider class and Ollama-specific error mapping.

Feature: 020-add-ollama-support
User Story: US1 - Use Local Ollama Models
Tasks: T007, T008
"""

import pytest
from unittest.mock import patch, MagicMock


class TestOllamaProviderInitialization:
    """T007: Unit tests for OllamaProvider initialization."""

    def test_provider_id_returns_ollama(self):
        """Test that provider_id property returns 'ollama'."""
        from src.services.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        assert provider.provider_id == "ollama"

    def test_get_config_returns_correct_provider_config(self):
        """Test that get_config returns correctly configured ProviderConfig."""
        from src.services.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        config = provider.get_config()

        assert config.id == "ollama"
        assert config.name == "Ollama"
        assert config.api_key_env is None  # Ollama doesn't require API key
        assert config.models_env == "OLLAMA_MODELS"

    def test_provider_config_is_enabled_without_api_key(self):
        """Test that Ollama provider is enabled even without API key."""
        from src.services.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        config = provider.get_config()

        # Ollama should always be enabled since api_key_env is None
        assert config.is_enabled() is True


class TestOllamaProviderCreateLLM:
    """T008: Unit tests for OllamaProvider.create_llm() method."""

    @patch('src.services.providers.ollama.ChatOllama')
    def test_create_llm_returns_chat_ollama_instance(self, mock_chat_ollama):
        """Test that create_llm returns a ChatOllama instance."""
        from src.services.providers.ollama import OllamaProvider

        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        provider = OllamaProvider()
        result = provider.create_llm("llama2")

        assert result == mock_instance
        mock_chat_ollama.assert_called_once()

    @patch('src.services.providers.ollama.ChatOllama')
    def test_create_llm_passes_model_id(self, mock_chat_ollama):
        """Test that create_llm passes the model_id to ChatOllama."""
        from src.services.providers.ollama import OllamaProvider

        provider = OllamaProvider()
        provider.create_llm("codellama")

        # Verify model was passed to ChatOllama
        call_kwargs = mock_chat_ollama.call_args[1]
        assert call_kwargs['model'] == "codellama"

    @patch('src.services.providers.ollama.ChatOllama')
    def test_create_llm_uses_default_base_url(self, mock_chat_ollama, monkeypatch):
        """Test that create_llm uses default localhost URL when OLLAMA_BASE_URL not set."""
        from src.services.providers.ollama import OllamaProvider

        # Ensure OLLAMA_BASE_URL is not set
        monkeypatch.delenv('OLLAMA_BASE_URL', raising=False)

        provider = OllamaProvider()
        provider.create_llm("llama2")

        call_kwargs = mock_chat_ollama.call_args[1]
        assert call_kwargs['base_url'] == "http://localhost:11434"


# T026, T027: Tests for custom URL (Phase 5) - added here for completeness
class TestOllamaProviderCustomURL:
    """Tests for OLLAMA_BASE_URL configuration (User Story 3)."""

    @patch('src.services.providers.ollama.ChatOllama')
    def test_create_llm_uses_custom_base_url(self, mock_chat_ollama, monkeypatch):
        """T027: Test that create_llm uses custom URL from OLLAMA_BASE_URL."""
        from src.services.providers.ollama import OllamaProvider

        monkeypatch.setenv('OLLAMA_BASE_URL', 'http://192.168.1.100:11434')

        # Need to create new provider after setting env var
        provider = OllamaProvider()
        provider.create_llm("llama2")

        call_kwargs = mock_chat_ollama.call_args[1]
        assert call_kwargs['base_url'] == "http://192.168.1.100:11434"


# T017, T018, T019: Tests for error mapping (User Story 2)
class TestOllamaErrorMapping:
    """Tests for map_ollama_error() function."""

    def test_map_connect_error_to_connection_error(self):
        """T017: Test that httpx.ConnectError maps to LLMConnectionError."""
        import httpx
        from src.services.providers.errors import map_ollama_error
        from src.services.providers.base import LLMConnectionError

        error = httpx.ConnectError("Connection refused")
        result = map_ollama_error(error)

        assert isinstance(result, LLMConnectionError)
        assert "Ollama" in result.message
        assert "running" in result.message.lower()

    def test_map_timeout_error_to_timeout_error(self):
        """T018: Test that httpx.TimeoutException maps to LLMTimeoutError."""
        import httpx
        from src.services.providers.errors import map_ollama_error
        from src.services.providers.base import LLMTimeoutError

        error = httpx.ReadTimeout("Read timed out")
        result = map_ollama_error(error)

        assert isinstance(result, LLMTimeoutError)
        assert "timed out" in result.message.lower()

    def test_map_http_404_to_bad_request_error(self):
        """T019: Test that HTTP 404 (model not found) maps to LLMBadRequestError."""
        import httpx
        from src.services.providers.errors import map_ollama_error
        from src.services.providers.base import LLMBadRequestError

        # Create a mock response with 404 status
        request = httpx.Request("POST", "http://localhost:11434/api/chat")
        response = httpx.Response(404, request=request)
        error = httpx.HTTPStatusError("Not Found", request=request, response=response)

        result = map_ollama_error(error)

        assert isinstance(result, LLMBadRequestError)
        assert "not found" in result.message.lower()

    def test_map_generic_http_error_to_connection_error(self):
        """Test that generic httpx.HTTPError maps to LLMConnectionError."""
        import httpx
        from src.services.providers.errors import map_ollama_error
        from src.services.providers.base import LLMConnectionError

        error = httpx.HTTPError("Generic HTTP error")
        result = map_ollama_error(error)

        assert isinstance(result, LLMConnectionError)

    def test_map_unknown_error_to_generic_service_error(self):
        """Test that unknown errors map to generic LLMServiceError."""
        from src.services.providers.errors import map_ollama_error
        from src.services.providers.base import LLMServiceError, LLMConnectionError

        error = ValueError("Some unknown error")
        result = map_ollama_error(error)

        assert isinstance(result, LLMServiceError)
        assert not isinstance(result, LLMConnectionError)


class TestOllamaProviderMapError:
    """Test that OllamaProvider.map_error() uses map_ollama_error()."""

    def test_provider_map_error_delegates_to_map_ollama_error(self):
        """T025: Test that OllamaProvider.map_error() calls map_ollama_error()."""
        import httpx
        from src.services.providers.ollama import OllamaProvider
        from src.services.providers.base import LLMConnectionError

        provider = OllamaProvider()
        error = httpx.ConnectError("Connection refused")
        result = provider.map_error(error)

        assert isinstance(result, LLMConnectionError)


# Export test classes
__all__ = [
    'TestOllamaProviderInitialization',
    'TestOllamaProviderCreateLLM',
    'TestOllamaProviderCustomURL',
    'TestOllamaErrorMapping',
    'TestOllamaProviderMapError',
]
