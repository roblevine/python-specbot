"""
Provider Error Mapping Module

Unified error mapping from provider-specific exceptions to LLMServiceError.
Consolidates duplicate exception handling across providers.

Feature: 012-modular-model-providers
User Story: US2 - Consolidated Error Handling
"""

from typing import Optional

# OpenAI exceptions
from openai import (
    AuthenticationError as OpenAIAuthenticationError,
    RateLimitError as OpenAIRateLimitError,
    APIConnectionError as OpenAIAPIConnectionError,
    BadRequestError as OpenAIBadRequestError,
    APITimeoutError as OpenAIAPITimeoutError
)

# Anthropic exceptions
from anthropic import (
    AuthenticationError as AnthropicAuthenticationError,
    RateLimitError as AnthropicRateLimitError,
    APIConnectionError as AnthropicAPIConnectionError,
    BadRequestError as AnthropicBadRequestError,
    APITimeoutError as AnthropicAPITimeoutError,
    NotFoundError as AnthropicNotFoundError,
    PermissionDeniedError as AnthropicPermissionDeniedError,
    InternalServerError as AnthropicInternalServerError
)

# Ollama uses httpx for HTTP connections (via langchain-ollama)
import httpx

# Import LLM service errors from base module (avoids circular imports)
from src.services.providers.base import (
    LLMServiceError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMBadRequestError
)


def map_openai_error(error: Exception) -> LLMServiceError:
    """
    Map an OpenAI-specific exception to an LLMServiceError.

    Args:
        error: The OpenAI exception

    Returns:
        Appropriate LLMServiceError subclass
    """
    if isinstance(error, OpenAIAuthenticationError):
        return LLMAuthenticationError(original_error=error)

    if isinstance(error, OpenAIRateLimitError):
        return LLMRateLimitError(original_error=error)

    # Check timeout BEFORE connection (APITimeoutError extends APIConnectionError)
    if isinstance(error, OpenAIAPITimeoutError):
        return LLMTimeoutError(original_error=error)

    if isinstance(error, OpenAIAPIConnectionError):
        return LLMConnectionError(original_error=error)

    if isinstance(error, OpenAIBadRequestError):
        return LLMBadRequestError(original_error=error)

    # Default: generic LLM error
    return LLMServiceError("AI service error occurred", original_error=error)


def map_anthropic_error(error: Exception) -> LLMServiceError:
    """
    Map an Anthropic-specific exception to an LLMServiceError.

    Args:
        error: The Anthropic exception

    Returns:
        Appropriate LLMServiceError subclass
    """
    if isinstance(error, AnthropicAuthenticationError):
        return LLMAuthenticationError(original_error=error)

    if isinstance(error, AnthropicRateLimitError):
        return LLMRateLimitError(original_error=error)

    # Check timeout BEFORE connection (APITimeoutError extends APIConnectionError)
    if isinstance(error, AnthropicAPITimeoutError):
        return LLMTimeoutError(original_error=error)

    if isinstance(error, AnthropicAPIConnectionError):
        return LLMConnectionError(original_error=error)

    if isinstance(error, AnthropicBadRequestError):
        return LLMBadRequestError(original_error=error)

    # Anthropic-specific errors
    if isinstance(error, AnthropicNotFoundError):
        return LLMBadRequestError(
            message="Model or resource not found",
            original_error=error
        )

    if isinstance(error, AnthropicPermissionDeniedError):
        return LLMAuthenticationError(
            message="AI service access denied",
            original_error=error
        )

    if isinstance(error, AnthropicInternalServerError):
        return LLMServiceError(
            message="AI service temporarily unavailable",
            original_error=error
        )

    # Default: generic LLM error
    return LLMServiceError("AI service error occurred", original_error=error)


def map_ollama_error(error: Exception) -> LLMServiceError:
    """
    Map an Ollama-specific exception to an LLMServiceError.

    Ollama uses httpx for HTTP connections, so we map httpx exceptions.

    Feature: 020-add-ollama-support
    User Story: US2 - Handle Ollama Server Unavailable
    Tasks: T020, T021, T022, T023

    Args:
        error: The Ollama/httpx exception

    Returns:
        Appropriate LLMServiceError subclass
    """
    # T022: Timeout errors (check before ConnectError as TimeoutException is more specific)
    if isinstance(error, httpx.TimeoutException):
        return LLMTimeoutError(
            message="Ollama server request timed out",
            original_error=error
        )

    # T021: Connection errors - server unreachable
    if isinstance(error, httpx.ConnectError):
        return LLMConnectionError(
            message="Unable to reach local Ollama server. Is Ollama running? (ollama serve)",
            original_error=error
        )

    # T023: HTTP status errors (404 = model not found)
    if isinstance(error, httpx.HTTPStatusError):
        if error.response.status_code == 404:
            return LLMBadRequestError(
                message="Model not found in Ollama. Have you pulled it? (ollama pull <model>)",
                original_error=error
            )
        # Other HTTP errors
        return LLMServiceError(
            message=f"Ollama server error (HTTP {error.response.status_code})",
            original_error=error
        )

    # Generic httpx errors
    if isinstance(error, httpx.HTTPError):
        return LLMConnectionError(
            message="Ollama connection error",
            original_error=error
        )

    # Default: generic LLM error
    return LLMServiceError("Ollama service error occurred", original_error=error)


def map_provider_error(error: Exception, provider_id: str) -> LLMServiceError:
    """
    Map a provider-specific exception to an LLMServiceError.

    Routes to the appropriate provider-specific mapper based on provider_id.

    Args:
        error: The provider exception
        provider_id: The provider identifier ('openai', 'anthropic', etc.)

    Returns:
        Appropriate LLMServiceError subclass
    """
    if provider_id == "openai":
        return map_openai_error(error)

    if provider_id == "anthropic":
        return map_anthropic_error(error)

    if provider_id == "ollama":
        return map_ollama_error(error)

    # Unknown provider: return generic error
    return LLMServiceError("AI service error occurred", original_error=error)


# Export public API
__all__ = [
    'map_openai_error',
    'map_anthropic_error',
    'map_ollama_error',
    'map_provider_error',
]
