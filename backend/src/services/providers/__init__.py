"""
Provider Module

Centralized registry and management for LLM providers.
Supports modular addition of new providers without modifying core code.

Feature: 012-modular-model-providers
"""

import os
from typing import Dict, List, Optional

from .base import (
    BaseProvider,
    ProviderConfig,
    AbstractProvider,
    LLMServiceError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMBadRequestError
)


class ProviderRegistry:
    """
    Central registry for all available LLM providers.

    Manages provider registration, lookup, and enabled state.
    Providers are registered at module import time and can be
    queried based on their enabled status (API key availability).
    """

    def __init__(self):
        """Initialize an empty provider registry."""
        self._providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """
        Register a provider with the registry.

        Args:
            provider: Provider instance implementing BaseProvider protocol
        """
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> Optional[BaseProvider]:
        """
        Get a provider by ID.

        Args:
            provider_id: The provider identifier

        Returns:
            Provider instance if found, None otherwise
        """
        return self._providers.get(provider_id)

    def get_all(self) -> List[BaseProvider]:
        """
        Get all registered providers.

        Returns:
            List of all registered providers
        """
        return list(self._providers.values())

    def get_enabled(self) -> List[BaseProvider]:
        """
        Get only providers that are enabled (have API key configured).

        Returns:
            List of enabled providers
        """
        enabled = []
        for provider in self._providers.values():
            config = provider.get_config()
            api_key = os.getenv(config.api_key_env)
            if api_key and api_key.strip():
                enabled.append(provider)
        return enabled

    def is_enabled(self, provider_id: str) -> bool:
        """
        Check if a specific provider is enabled.

        Args:
            provider_id: The provider identifier

        Returns:
            True if provider exists and has API key configured
        """
        provider = self.get(provider_id)
        if not provider:
            return False
        config = provider.get_config()
        api_key = os.getenv(config.api_key_env)
        return bool(api_key and api_key.strip())

    def __contains__(self, provider_id: str) -> bool:
        """Check if a provider is registered."""
        return provider_id in self._providers

    def __len__(self) -> int:
        """Return number of registered providers."""
        return len(self._providers)


# Global provider registry instance
registry = ProviderRegistry()


# T028: Register providers at module import time
def _register_providers():
    """
    Register all available providers with the global registry.

    This is called at module import time to ensure all providers
    are available for use.
    """
    from .openai import OpenAIProvider
    from .anthropic import AnthropicProvider

    registry.register(OpenAIProvider())
    registry.register(AnthropicProvider())


# Register providers when module is imported
_register_providers()


# Export public API
__all__ = [
    'BaseProvider',
    'AbstractProvider',
    'ProviderConfig',
    'ProviderRegistry',
    'LLMServiceError',
    'LLMAuthenticationError',
    'LLMRateLimitError',
    'LLMConnectionError',
    'LLMTimeoutError',
    'LLMBadRequestError',
    'registry',
]
