"""
Tests for Provider Base Module

Tests for ProviderConfig validation and ProviderRegistry functionality.

Feature: 012-modular-model-providers
User Story: US1 - Unified Provider Configuration
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from src.services.providers.base import ProviderConfig, BaseProvider, AbstractProvider


class TestProviderConfig:
    """Tests for ProviderConfig Pydantic model."""

    def test_valid_provider_config(self):
        """Test creating a valid ProviderConfig."""
        config = ProviderConfig(
            id="openai",
            name="OpenAI",
            api_key_env="OPENAI_API_KEY",
            models_env="OPENAI_MODELS"
        )
        assert config.id == "openai"
        assert config.name == "OpenAI"
        assert config.api_key_env == "OPENAI_API_KEY"
        assert config.models_env == "OPENAI_MODELS"

    def test_provider_config_strips_whitespace(self):
        """Test that ProviderConfig strips whitespace from id."""
        config = ProviderConfig(
            id="  openai  ",
            name="OpenAI",
            api_key_env="OPENAI_API_KEY",
            models_env="OPENAI_MODELS"
        )
        assert config.id == "openai"

    def test_provider_config_lowercase_id(self):
        """Test that ProviderConfig converts id to lowercase."""
        config = ProviderConfig(
            id="OpenAI",
            name="OpenAI",
            api_key_env="OPENAI_API_KEY",
            models_env="OPENAI_MODELS"
        )
        assert config.id == "openai"

    def test_provider_config_allows_hyphen_in_id(self):
        """Test that ProviderConfig allows hyphens in id."""
        config = ProviderConfig(
            id="azure-openai",
            name="Azure OpenAI",
            api_key_env="AZURE_OPENAI_API_KEY",
            models_env="AZURE_OPENAI_MODELS"
        )
        assert config.id == "azure-openai"

    def test_provider_config_rejects_empty_id(self):
        """Test that ProviderConfig rejects empty id."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProviderConfig(
                id="",
                name="OpenAI",
                api_key_env="OPENAI_API_KEY",
                models_env="OPENAI_MODELS"
            )

    def test_provider_config_rejects_whitespace_only_id(self):
        """Test that ProviderConfig rejects whitespace-only id."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProviderConfig(
                id="   ",
                name="OpenAI",
                api_key_env="OPENAI_API_KEY",
                models_env="OPENAI_MODELS"
            )

    def test_provider_config_rejects_special_chars_in_id(self):
        """Test that ProviderConfig rejects special characters in id."""
        with pytest.raises(ValueError, match="must be lowercase alphanumeric"):
            ProviderConfig(
                id="open_ai",  # underscore not allowed
                name="OpenAI",
                api_key_env="OPENAI_API_KEY",
                models_env="OPENAI_MODELS"
            )

    def test_provider_config_rejects_empty_api_key_env(self):
        """Test that ProviderConfig rejects empty api_key_env."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProviderConfig(
                id="openai",
                name="OpenAI",
                api_key_env="",
                models_env="OPENAI_MODELS"
            )

    def test_provider_config_rejects_empty_models_env(self):
        """Test that ProviderConfig rejects empty models_env."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ProviderConfig(
                id="openai",
                name="OpenAI",
                api_key_env="OPENAI_API_KEY",
                models_env=""
            )


class TestProviderRegistry:
    """Tests for ProviderRegistry class."""

    def test_register_and_get_provider(self):
        """Test registering and retrieving a provider."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        # Create a mock provider
        mock_provider = MagicMock(spec=BaseProvider)
        mock_provider.provider_id = "test-provider"
        mock_provider.get_config.return_value = ProviderConfig(
            id="test-provider",
            name="Test Provider",
            api_key_env="TEST_API_KEY",
            models_env="TEST_MODELS"
        )

        registry.register(mock_provider)

        # Retrieve the provider
        retrieved = registry.get("test-provider")
        assert retrieved is mock_provider

    def test_get_nonexistent_provider_returns_none(self):
        """Test that getting a nonexistent provider returns None."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()
        assert registry.get("nonexistent") is None

    def test_get_all_providers(self):
        """Test getting all registered providers."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        # Register two mock providers
        mock1 = MagicMock(spec=BaseProvider)
        mock1.provider_id = "provider1"
        mock2 = MagicMock(spec=BaseProvider)
        mock2.provider_id = "provider2"

        registry.register(mock1)
        registry.register(mock2)

        all_providers = registry.get_all()
        assert len(all_providers) == 2
        assert mock1 in all_providers
        assert mock2 in all_providers

    @patch.dict(os.environ, {"TEST_API_KEY": "test-key"}, clear=False)
    def test_get_enabled_providers_with_api_key(self):
        """Test that providers with API keys are returned as enabled."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        mock_provider = MagicMock(spec=BaseProvider)
        mock_provider.provider_id = "test-provider"
        mock_provider.get_config.return_value = ProviderConfig(
            id="test-provider",
            name="Test Provider",
            api_key_env="TEST_API_KEY",
            models_env="TEST_MODELS"
        )

        registry.register(mock_provider)

        enabled = registry.get_enabled()
        assert len(enabled) == 1
        assert mock_provider in enabled

    @patch.dict(os.environ, {}, clear=True)
    def test_get_enabled_providers_without_api_key(self):
        """Test that providers without API keys are not returned as enabled."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        mock_provider = MagicMock(spec=BaseProvider)
        mock_provider.provider_id = "test-provider"
        mock_provider.get_config.return_value = ProviderConfig(
            id="test-provider",
            name="Test Provider",
            api_key_env="MISSING_API_KEY",
            models_env="TEST_MODELS"
        )

        registry.register(mock_provider)

        enabled = registry.get_enabled()
        assert len(enabled) == 0

    @patch.dict(os.environ, {"TEST_API_KEY": "test-key"}, clear=False)
    def test_is_enabled_with_api_key(self):
        """Test is_enabled returns True when API key is set."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        mock_provider = MagicMock(spec=BaseProvider)
        mock_provider.provider_id = "test-provider"
        mock_provider.get_config.return_value = ProviderConfig(
            id="test-provider",
            name="Test Provider",
            api_key_env="TEST_API_KEY",
            models_env="TEST_MODELS"
        )

        registry.register(mock_provider)

        assert registry.is_enabled("test-provider") is True

    def test_is_enabled_nonexistent_provider(self):
        """Test is_enabled returns False for nonexistent provider."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()
        assert registry.is_enabled("nonexistent") is False

    def test_registry_contains(self):
        """Test the __contains__ method."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        mock_provider = MagicMock(spec=BaseProvider)
        mock_provider.provider_id = "test-provider"

        registry.register(mock_provider)

        assert "test-provider" in registry
        assert "nonexistent" not in registry

    def test_registry_len(self):
        """Test the __len__ method."""
        from src.services.providers import ProviderRegistry

        registry = ProviderRegistry()

        mock1 = MagicMock(spec=BaseProvider)
        mock1.provider_id = "provider1"
        mock2 = MagicMock(spec=BaseProvider)
        mock2.provider_id = "provider2"

        assert len(registry) == 0
        registry.register(mock1)
        assert len(registry) == 1
        registry.register(mock2)
        assert len(registry) == 2
