"""
Base Provider Module

Defines the abstract base interface that all LLM providers must implement.
Part of the provider abstraction layer for modular, extensible provider support.

Feature: 012-modular-model-providers
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable, Optional
from pydantic import BaseModel, Field, field_validator
from langchain_core.language_models.chat_models import BaseChatModel


class ProviderConfig(BaseModel):
    """
    Configuration metadata for an LLM provider.

    Attributes:
        id: Unique identifier (e.g., "openai", "anthropic")
        name: Human-readable display name
        api_key_env: Environment variable name for API key
        models_env: Environment variable name for models list
    """
    id: str = Field(..., description="Unique provider identifier")
    name: str = Field(..., description="Human-readable display name")
    api_key_env: str = Field(..., description="Environment variable name for API key")
    models_env: str = Field(..., description="Environment variable name for models list")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate provider ID is lowercase alphanumeric with optional hyphens."""
        if not v or not v.strip():
            raise ValueError("Provider ID cannot be empty")
        v = v.strip().lower()
        if not all(c.isalnum() or c == '-' for c in v):
            raise ValueError("Provider ID must be lowercase alphanumeric with optional hyphens")
        return v

    @field_validator('api_key_env', 'models_env')
    @classmethod
    def validate_env_var(cls, v: str) -> str:
        """Validate environment variable name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Environment variable name cannot be empty")
        return v.strip()

    def is_enabled(self) -> bool:
        """
        Check if this provider is enabled (has API key configured).

        Returns:
            True if the API key environment variable is set and non-empty
        """
        import os
        api_key = os.getenv(self.api_key_env)
        return bool(api_key and api_key.strip())


# LLM Service Error Classes
# Centralized here to avoid circular imports between llm_service.py and providers

class LLMServiceError(Exception):
    """Base exception for LLM service errors."""
    def __init__(self, message: str = "AI service error occurred", status_code: int = 503, original_error: Optional[Exception] = None):
        self.message = message
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)


class LLMAuthenticationError(LLMServiceError):
    """Authentication/configuration error → 503"""
    def __init__(self, message: str = "AI service configuration error", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMRateLimitError(LLMServiceError):
    """Rate limit error → 503"""
    def __init__(self, message: str = "AI service is busy", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMConnectionError(LLMServiceError):
    """Connection error → 503"""
    def __init__(self, message: str = "Unable to reach AI service", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=503, original_error=original_error)


class LLMTimeoutError(LLMServiceError):
    """Timeout error → 504"""
    def __init__(self, message: str = "Request timed out", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=504, original_error=original_error)


class LLMBadRequestError(LLMServiceError):
    """Bad request error → 400"""
    def __init__(self, message: str = "Message could not be processed", original_error: Optional[Exception] = None):
        super().__init__(message, status_code=400, original_error=original_error)


@runtime_checkable
class BaseProvider(Protocol):
    """
    Protocol defining the interface that all LLM providers must implement.

    This uses Python's Protocol (PEP 544) for structural subtyping,
    allowing providers to implement the interface without explicit inheritance.
    """

    @property
    def provider_id(self) -> str:
        """Return the unique provider identifier."""
        ...

    def create_llm(self, model_id: str) -> BaseChatModel:
        """
        Create a configured LangChain chat model instance.

        Args:
            model_id: The model ID to create an instance for

        Returns:
            Configured BaseChatModel instance (e.g., ChatOpenAI, ChatAnthropic)

        Raises:
            LLMServiceError: If the provider cannot be initialized (e.g., missing API key)
        """
        ...

    def map_error(self, error: Exception) -> LLMServiceError:
        """
        Map a provider-specific exception to a unified LLMServiceError.

        Args:
            error: The provider-specific exception

        Returns:
            Appropriate LLMServiceError subclass
        """
        ...

    def get_config(self) -> ProviderConfig:
        """
        Return the provider's configuration metadata.

        Returns:
            ProviderConfig with provider details
        """
        ...


class AbstractProvider(ABC):
    """
    Abstract base class that providers can optionally extend.

    Provides a concrete base implementation with abstract methods.
    Use this if you prefer class-based inheritance over Protocol.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return the unique provider identifier."""
        pass

    @abstractmethod
    def create_llm(self, model_id: str) -> BaseChatModel:
        """Create a configured LangChain chat model instance."""
        pass

    @abstractmethod
    def map_error(self, error: Exception) -> LLMServiceError:
        """Map a provider-specific exception to LLMServiceError."""
        pass

    @abstractmethod
    def get_config(self) -> ProviderConfig:
        """Return the provider's configuration metadata."""
        pass
