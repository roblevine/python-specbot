"""
OpenAI Provider Implementation

Implements the BaseProvider protocol for OpenAI models.

Feature: 012-modular-model-providers
User Story: US3 - Provider Factory Pattern
Task: T026
"""

import os
from typing import TYPE_CHECKING

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from src.services.providers.base import (
    ProviderConfig,
    AbstractProvider,
    LLMServiceError,
    LLMAuthenticationError
)
from src.services.providers.errors import map_openai_error


class OpenAIProvider(AbstractProvider):
    """
    OpenAI provider implementation.

    Provides LLM instances for OpenAI models (gpt-3.5-turbo, gpt-4, etc.)
    via LangChain's ChatOpenAI class.
    """

    def __init__(self):
        """Initialize the OpenAI provider with its configuration."""
        self._config = ProviderConfig(
            id="openai",
            name="OpenAI",
            api_key_env="OPENAI_API_KEY",
            models_env="OPENAI_MODELS"
        )

    @property
    def provider_id(self) -> str:
        """Return the provider identifier."""
        return self._config.id

    def create_llm(self, model_id: str) -> BaseChatModel:
        """
        Create a ChatOpenAI instance for the given model.

        Args:
            model_id: The model ID (e.g., 'gpt-4', 'gpt-3.5-turbo')

        Returns:
            Configured ChatOpenAI instance

        Raises:
            LLMAuthenticationError: If OPENAI_API_KEY is not configured
        """
        api_key = os.getenv(self._config.api_key_env)
        if not api_key:
            raise LLMAuthenticationError("OpenAI API key not configured")

        return ChatOpenAI(
            api_key=api_key,
            model=model_id,
            timeout=120,
            request_timeout=120
        )

    def map_error(self, error: Exception) -> LLMServiceError:
        """
        Map an OpenAI exception to an LLMServiceError.

        Args:
            error: The exception to map

        Returns:
            Appropriate LLMServiceError subclass
        """
        return map_openai_error(error)

    def get_config(self) -> ProviderConfig:
        """
        Return the provider configuration.

        Returns:
            ProviderConfig instance for OpenAI
        """
        return self._config


# Export public API
__all__ = ['OpenAIProvider']
