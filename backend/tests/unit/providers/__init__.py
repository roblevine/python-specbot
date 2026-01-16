"""
Provider Tests Package

Tests for the provider abstraction layer.

Feature: 012-modular-model-providers
Task: T033 - Provider test template base class
"""

from abc import ABC, abstractmethod
from typing import Type
from unittest.mock import Mock, patch
import pytest


class BaseProviderTestMixin(ABC):
    """
    T033: Base test mixin for provider implementations.

    Provides a reusable template for testing provider implementations.
    Concrete test classes should inherit from this mixin and implement
    the abstract methods.

    Usage:
        class TestOpenAIProvider(BaseProviderTestMixin):
            provider_class = OpenAIProvider
            chat_class_path = 'src.services.providers.openai.ChatOpenAI'
            api_key_env = 'OPENAI_API_KEY'
            expected_provider_id = 'openai'
            expected_provider_name = 'OpenAI'
    """

    # Abstract properties that must be defined by subclasses
    @property
    @abstractmethod
    def provider_class(self) -> Type:
        """The provider class to test."""
        pass

    @property
    @abstractmethod
    def chat_class_path(self) -> str:
        """The path to the chat model class for mocking."""
        pass

    @property
    @abstractmethod
    def api_key_env(self) -> str:
        """The environment variable name for the API key."""
        pass

    @property
    @abstractmethod
    def expected_provider_id(self) -> str:
        """The expected provider ID."""
        pass

    @property
    @abstractmethod
    def expected_provider_name(self) -> str:
        """The expected provider display name."""
        pass

    @property
    @abstractmethod
    def sample_model_id(self) -> str:
        """A sample model ID for testing."""
        pass

    def test_provider_id_property(self):
        """Test that provider_id returns the expected value."""
        provider = self.provider_class()
        assert provider.provider_id == self.expected_provider_id

    def test_get_config_returns_provider_config(self):
        """Test that get_config returns a ProviderConfig instance."""
        from src.services.providers.base import ProviderConfig

        provider = self.provider_class()
        config = provider.get_config()

        assert isinstance(config, ProviderConfig)
        assert config.id == self.expected_provider_id
        assert config.name == self.expected_provider_name
        assert config.api_key_env == self.api_key_env

    def test_create_llm_raises_error_when_api_key_missing(self):
        """Test that create_llm raises error when API key is missing."""
        from src.services.providers.base import LLMAuthenticationError

        with patch.dict('os.environ', {}, clear=True):
            provider = self.provider_class()

            with pytest.raises(LLMAuthenticationError):
                provider.create_llm(self.sample_model_id)

    def test_implements_base_provider_protocol(self):
        """Test that provider implements BaseProvider protocol."""
        from src.services.providers.base import BaseProvider

        provider = self.provider_class()

        # Check all required attributes exist
        assert hasattr(provider, 'provider_id')
        assert hasattr(provider, 'create_llm')
        assert hasattr(provider, 'map_error')
        assert hasattr(provider, 'get_config')

        # Verify it passes isinstance check
        assert isinstance(provider, BaseProvider)


# Export for use in tests
__all__ = ['BaseProviderTestMixin']
