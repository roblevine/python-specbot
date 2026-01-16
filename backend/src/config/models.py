"""
Model Configuration Module

Manages model configuration from environment variables with multi-provider support.
Supports OpenAI and Anthropic providers with backward compatibility for legacy configs.

Feature: 011-anthropic-support
"""

import json
import os
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

from src.utils.logger import get_logger

logger = get_logger(__name__)


# T006: Provider registry constant
PROVIDERS: Dict[str, Dict[str, str]] = {
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "models_env": "OPENAI_MODELS"
    },
    "anthropic": {
        "name": "Anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
        "models_env": "ANTHROPIC_MODELS"
    }
}


class ModelConfigurationError(Exception):
    """Custom exception for model configuration errors with helpful context."""

    def __init__(self, message: str, help_text: Optional[str] = None):
        self.message = message
        self.help_text = help_text
        full_message = message
        if help_text:
            full_message = f"{message}\n\nHow to fix:\n{help_text}"
        super().__init__(full_message)


class ModelConfig(BaseModel):
    """Configuration for a single model with provider support."""

    id: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-5-sonnet-20241022')")
    name: str = Field(..., max_length=50, description="Human-readable display name")
    description: str = Field(..., max_length=200, description="Brief model description")
    # T003: Add provider field with default for backward compatibility (T005)
    provider: Literal["openai", "anthropic"] = Field(
        default="openai",
        description="Provider identifier: 'openai' or 'anthropic'"
    )
    default: bool = Field(default=False, description="Whether this is the default model")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate model ID is non-empty."""
        if not v or not v.strip():
            raise ValueError("Model ID cannot be empty")
        return v.strip()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate model name is non-empty."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate model description is non-empty."""
        if not v or not v.strip():
            raise ValueError("Model description cannot be empty")
        return v.strip()

    # T004: Provider validation is handled by Literal type annotation


class ModelsConfiguration(BaseModel):
    """Root configuration for available models from all providers."""

    models: List[ModelConfig] = Field(..., min_length=1, description="List of available models")

    @field_validator('models')
    @classmethod
    def validate_models(cls, v: List[ModelConfig]) -> List[ModelConfig]:
        """Validate model list constraints."""
        if not v:
            raise ValueError("At least one model must be configured")

        # Check for duplicate IDs (across all providers)
        ids = [model.id for model in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate model IDs found")

        # T009: Check exactly one default model across all providers
        default_count = sum(1 for model in v if model.default)
        if default_count == 0:
            raise ValueError("Exactly one model must be marked as default")
        if default_count > 1:
            raise ValueError("Only one model can be marked as default across all providers")

        return v


def check_provider_enabled(provider_id: str) -> bool:
    """
    T027 (US3): Check if a provider is enabled (has API key configured).

    Args:
        provider_id: Provider identifier ('openai' or 'anthropic')

    Returns:
        bool: True if the provider's API key is set, False otherwise
    """
    if provider_id not in PROVIDERS:
        return False

    api_key_env = PROVIDERS[provider_id]["api_key_env"]
    api_key = os.getenv(api_key_env)
    return bool(api_key and api_key.strip())


def _load_models_from_env(env_var: str, provider_id: str) -> List[ModelConfig]:
    """
    Load and parse models from an environment variable.

    Args:
        env_var: Environment variable name containing JSON model config
        provider_id: Provider ID to assign to models (for backward compatibility)

    Returns:
        List of ModelConfig objects

    Raises:
        ModelConfigurationError: If JSON is invalid
    """
    models_env = os.getenv(env_var)

    if not models_env:
        return []

    try:
        models_data = json.loads(models_env)
        if not isinstance(models_data, list):
            raise ModelConfigurationError(
                f"{env_var} must be a JSON array",
                f"Set {env_var} to a JSON array: '[{{\"id\": \"model-id\", ...}}]'"
            )

        models = []
        for model_data in models_data:
            # T005: Add backward compatibility - default provider if not specified
            if "provider" not in model_data:
                model_data["provider"] = provider_id
            models.append(ModelConfig(**model_data))

        return models

    except json.JSONDecodeError as e:
        raise ModelConfigurationError(
            f"Invalid JSON in {env_var}: {str(e)}",
            f"Ensure {env_var} contains valid JSON."
        ) from e

    except ValueError as e:
        raise ModelConfigurationError(
            f"Invalid model configuration in {env_var}: {str(e)}",
            "Each model must have: id, name, description, provider, default (boolean)."
        ) from e


def load_openai_models() -> List[ModelConfig]:
    """
    Load OpenAI model configurations from OPENAI_MODELS environment variable.

    Returns:
        List of ModelConfig objects for OpenAI models
    """
    return _load_models_from_env("OPENAI_MODELS", "openai")


def load_anthropic_models() -> List[ModelConfig]:
    """
    T007: Load Anthropic model configurations from ANTHROPIC_MODELS environment variable.

    Returns:
        List of ModelConfig objects for Anthropic models
    """
    return _load_models_from_env("ANTHROPIC_MODELS", "anthropic")


def load_unified_models() -> List[ModelConfig]:
    """
    T049: Load model configurations from the unified MODELS environment variable.

    The unified MODELS variable contains all models from all providers in a single
    JSON array. Each model must have a 'provider' field to identify its provider.

    Returns:
        List of ModelConfig objects, or empty list if MODELS is not set

    Raises:
        ModelConfigurationError: If JSON is invalid or malformed
    """
    models_env = os.getenv("MODELS")

    if not models_env:
        return []

    try:
        models_data = json.loads(models_env)
        if not isinstance(models_data, list):
            raise ModelConfigurationError(
                "MODELS must be a JSON array",
                "Set MODELS to a JSON array: '[{\"id\": \"model-id\", \"provider\": \"openai\", ...}]'"
            )

        models = []
        for model_data in models_data:
            # Provider is required in unified format
            if "provider" not in model_data:
                raise ModelConfigurationError(
                    "Missing 'provider' field in MODELS configuration",
                    "Each model in MODELS must have a 'provider' field ('openai' or 'anthropic')"
                )
            models.append(ModelConfig(**model_data))

        return models

    except json.JSONDecodeError as e:
        raise ModelConfigurationError(
            f"Invalid JSON in MODELS: {str(e)}",
            "Ensure MODELS contains valid JSON."
        ) from e

    except ValueError as e:
        raise ModelConfigurationError(
            f"Invalid model configuration in MODELS: {str(e)}",
            "Each model must have: id, name, description, provider, default (boolean)."
        ) from e


def load_model_configuration() -> ModelsConfiguration:
    """
    T008/T050: Load and merge model configuration from all enabled providers.

    Prefers the unified MODELS environment variable if set. Falls back to
    legacy OPENAI_MODELS and ANTHROPIC_MODELS variables if MODELS is not set.

    Models are filtered to only include those from providers that have their
    API keys configured.

    Returns:
        ModelsConfiguration: Validated model configuration with all enabled models

    Raises:
        ModelConfigurationError: If configuration is invalid or no models available
    """
    all_models: List[ModelConfig] = []

    # T028 (US3): Check provider enablement status
    openai_enabled = check_provider_enabled("openai")
    anthropic_enabled = check_provider_enabled("anthropic")

    # T030 (US3): Log provider enablement status
    logger.info(f"Provider status: OpenAI={'enabled' if openai_enabled else 'disabled'}, "
                f"Anthropic={'enabled' if anthropic_enabled else 'disabled'}")

    # T029 (US3): Validate at least one provider is configured
    if not openai_enabled and not anthropic_enabled:
        raise ModelConfigurationError(
            "No AI providers configured",
            "At least one provider must be configured. Set either:\n"
            "- OPENAI_API_KEY and OPENAI_MODELS for OpenAI, or\n"
            "- ANTHROPIC_API_KEY and ANTHROPIC_MODELS for Anthropic"
        )

    # T050: Try unified MODELS first, fallback to legacy
    unified_models = load_unified_models()

    if unified_models:
        # T051: Filter models by enabled provider
        logger.info(f"Loading from unified MODELS configuration ({len(unified_models)} total models)")

        for model in unified_models:
            provider_enabled = check_provider_enabled(model.provider)
            if provider_enabled:
                all_models.append(model)
            else:
                logger.debug(f"Filtering out model '{model.id}' - provider '{model.provider}' not enabled")

        if all_models:
            logger.info(f"Loaded {len(all_models)} model(s) from unified MODELS (after filtering)")
    else:
        # Fallback to legacy env vars
        logger.debug("MODELS not set, falling back to legacy OPENAI_MODELS/ANTHROPIC_MODELS")

        # Load OpenAI models if enabled
        if openai_enabled:
            openai_models = load_openai_models()
            if openai_models:
                logger.info(f"Loaded {len(openai_models)} OpenAI model(s)")
                all_models.extend(openai_models)
            else:
                logger.warning("OpenAI API key set but no models configured in OPENAI_MODELS")

        # Load Anthropic models if enabled
        if anthropic_enabled:
            anthropic_models = load_anthropic_models()
            if anthropic_models:
                logger.info(f"Loaded {len(anthropic_models)} Anthropic model(s)")
                all_models.extend(anthropic_models)
            else:
                logger.warning("Anthropic API key set but no models configured in ANTHROPIC_MODELS")

    # Validate we have at least one model
    if not all_models:
        raise ModelConfigurationError(
            "No models configured for enabled providers",
            "Configure models for at least one enabled provider:\n"
            "- OPENAI_MODELS for OpenAI models\n"
            "- ANTHROPIC_MODELS for Anthropic models"
        )

    # T051: Handle case where the default model was filtered out
    has_default = any(model.default for model in all_models)
    if not has_default:
        # Make the first model the default
        logger.info(f"Default model was filtered out, making '{all_models[0].id}' the default")
        # Create a new model with default=True (ModelConfig is immutable)
        first_model = all_models[0]
        all_models[0] = ModelConfig(
            id=first_model.id,
            name=first_model.name,
            description=first_model.description,
            provider=first_model.provider,
            default=True
        )

    try:
        return ModelsConfiguration(models=all_models)
    except ValueError as e:
        raise ModelConfigurationError(
            f"Invalid model configuration: {str(e)}",
            "Ensure exactly one model has 'default': true across all providers."
        ) from e


def get_default_model(config: ModelsConfiguration) -> str:
    """
    Get the default model ID from configuration.

    Args:
        config: Model configuration

    Returns:
        str: Default model ID
    """
    for model in config.models:
        if model.default:
            return model.id

    # This should never happen due to validation, but provide fallback
    return config.models[0].id


def validate_model_id(model_id: str, config: ModelsConfiguration) -> bool:
    """
    Validate that a model ID exists in the configuration.

    Args:
        model_id: Model ID to validate
        config: Model configuration

    Returns:
        bool: True if model ID is valid, False otherwise
    """
    return any(model.id == model_id for model in config.models)


def get_model_by_id(model_id: str, config: ModelsConfiguration) -> Optional[ModelConfig]:
    """
    Get model configuration by ID.

    Args:
        model_id: Model ID to retrieve
        config: Model configuration

    Returns:
        Optional[ModelConfig]: Model configuration if found, None otherwise
    """
    for model in config.models:
        if model.id == model_id:
            return model
    return None


def get_provider_for_model(model_id: str, config: ModelsConfiguration) -> Optional[str]:
    """
    Get the provider ID for a given model.

    Args:
        model_id: Model ID to look up
        config: Model configuration

    Returns:
        Optional[str]: Provider ID ('openai' or 'anthropic') if found, None otherwise
    """
    model = get_model_by_id(model_id, config)
    return model.provider if model else None
