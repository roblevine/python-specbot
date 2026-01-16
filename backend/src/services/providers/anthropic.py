"""
Anthropic Provider Implementation

Implements the BaseProvider protocol for Anthropic models.

Feature: 012-modular-model-providers
User Story: US3 - Provider Factory Pattern
Task: T027
"""

import os
from typing import TYPE_CHECKING

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

from src.services.providers.base import (
    ProviderConfig,
    AbstractProvider,
    LLMServiceError,
    LLMAuthenticationError
)
from src.services.providers.errors import map_anthropic_error


class AnthropicProvider(AbstractProvider):
    """
    Anthropic provider implementation.

    Provides LLM instances for Anthropic models (claude-3-5-sonnet, etc.)
    via LangChain's ChatAnthropic class.
    """

    def __init__(self):
        """Initialize the Anthropic provider with its configuration."""
        self._config = ProviderConfig(
            id="anthropic",
            name="Anthropic",
            api_key_env="ANTHROPIC_API_KEY",
            models_env="ANTHROPIC_MODELS"
        )

    @property
    def provider_id(self) -> str:
        """Return the provider identifier."""
        return self._config.id

    def create_llm(self, model_id: str) -> BaseChatModel:
        """
        Create a ChatAnthropic instance for the given model.

        Args:
            model_id: The model ID (e.g., 'claude-3-5-sonnet-20241022')

        Returns:
            Configured ChatAnthropic instance

        Raises:
            LLMAuthenticationError: If ANTHROPIC_API_KEY is not configured
        """
        api_key = os.getenv(self._config.api_key_env)
        if not api_key:
            raise LLMAuthenticationError("Anthropic API key not configured")

        return ChatAnthropic(
            api_key=api_key,
            model=model_id,
            timeout=120
        )

    def map_error(self, error: Exception) -> LLMServiceError:
        """
        Map an Anthropic exception to an LLMServiceError.

        Args:
            error: The exception to map

        Returns:
            Appropriate LLMServiceError subclass
        """
        return map_anthropic_error(error)

    def get_config(self) -> ProviderConfig:
        """
        Return the provider configuration.

        Returns:
            ProviderConfig instance for Anthropic
        """
        return self._config


# Export public API
__all__ = ['AnthropicProvider']
