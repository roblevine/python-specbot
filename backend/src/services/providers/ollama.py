"""
Ollama Provider Implementation

Implements the BaseProvider protocol for local Ollama models.

Feature: 020-add-ollama-support
User Story: US1 - Use Local Ollama Models
Tasks: T010, T011, T012, T013, T016
"""

import os
from typing import TYPE_CHECKING

from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

from src.services.providers.base import (
    ProviderConfig,
    AbstractProvider,
    LLMServiceError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Default Ollama server URL
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaProvider(AbstractProvider):
    """
    Ollama provider implementation.

    Provides LLM instances for locally-hosted Ollama models (llama2, codellama, etc.)
    via LangChain's ChatOllama class.

    Ollama does not require an API key - it connects to a local server.
    The server URL can be configured via OLLAMA_BASE_URL environment variable.
    """

    def __init__(self):
        """Initialize the Ollama provider with its configuration."""
        self._config = ProviderConfig(
            id="ollama",
            name="Ollama",
            api_key_env=None,  # Ollama doesn't require an API key
            models_env="OLLAMA_MODELS"
        )
        # T016: Log provider initialization
        logger.info(f"OllamaProvider initialized (base_url will be resolved at LLM creation time)")

    @property
    def provider_id(self) -> str:
        """Return the provider identifier."""
        return self._config.id

    def create_llm(self, model_id: str) -> BaseChatModel:
        """
        Create a ChatOllama instance for the given model.

        Args:
            model_id: The model ID (e.g., 'llama2', 'codellama', 'mistral')

        Returns:
            Configured ChatOllama instance

        Note:
            Unlike OpenAI/Anthropic, Ollama doesn't require authentication.
            The base URL defaults to http://localhost:11434 but can be
            overridden via OLLAMA_BASE_URL environment variable.
        """
        # Resolve base URL at creation time (allows runtime configuration)
        base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

        logger.info(f"Creating ChatOllama for model '{model_id}' at {base_url}")

        return ChatOllama(
            model=model_id,
            base_url=base_url,
            timeout=120,
        )

    def map_error(self, error: Exception) -> LLMServiceError:
        """
        Map an Ollama exception to an LLMServiceError.

        Args:
            error: The exception to map

        Returns:
            Appropriate LLMServiceError subclass
        """
        # Import here to avoid circular imports
        from src.services.providers.errors import map_ollama_error
        return map_ollama_error(error)

    def get_config(self) -> ProviderConfig:
        """
        Return the provider configuration.

        Returns:
            ProviderConfig instance for Ollama
        """
        return self._config


# Export public API
__all__ = ['OllamaProvider']
