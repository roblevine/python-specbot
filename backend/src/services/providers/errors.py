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

    # Unknown provider: return generic error
    return LLMServiceError("AI service error occurred", original_error=error)


# Export public API
__all__ = [
    'map_openai_error',
    'map_anthropic_error',
    'map_provider_error',
]
