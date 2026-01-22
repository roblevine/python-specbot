"""
Model Configuration Module

Manages model configuration from provider-specific environment variables.
Supports OpenAI and Anthropic providers with automatic filtering based on API key availability.

Feature: 018-separate-provider-configs (replaces 012-modular-model-providers)

Configuration format:
- OPENAI_MODELS: JSON array of models for OpenAI
- ANTHROPIC_MODELS: JSON array of models for Anthropic
- DEFAULT_MODEL: Model ID to use as default (optional, falls back to first available)

Each model in provider configs only needs: id, name, description
Provider is inferred from the env var name, default is set via DEFAULT_MODEL.
"""

import json
import os
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

from src.utils.logger import get_logger

logger = get_logger(__name__)


# Provider registry constant - maps provider IDs to their configuration
# Note: api_key_env can be None for local providers like Ollama that don't require API keys
PROVIDERS: Dict[str, Dict[str, Optional[str]]] = {
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
    },
    "anthropic": {
        "name": "Anthropic",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "ollama": {
        "name": "Ollama",
        "api_key_env": None,  # Ollama doesn't require an API key (local server)
    }
}

# Provider-specific model env var names (018-separate-provider-configs)
PROVIDER_ENV_VARS: Dict[str, str] = {
    "openai": "OPENAI_MODELS",
    "anthropic": "ANTHROPIC_MODELS",
    "ollama": "OLLAMA_MODELS",
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


class ProviderModelConfig(BaseModel):
    """
    Simplified model configuration for provider-specific env vars.

    Used when parsing OPENAI_MODELS or ANTHROPIC_MODELS.
    Does not include 'provider' (inferred from env var) or 'default' (set via DEFAULT_MODEL).
    """

    id: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-5-sonnet-20241022')")
    name: str = Field(..., max_length=50, description="Human-readable display name")
    description: str = Field(..., max_length=200, description="Brief model description")

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


class ModelConfig(BaseModel):
    """Configuration for a single model with provider support."""

    id: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3-5-sonnet-20241022')")
    name: str = Field(..., max_length=50, description="Human-readable display name")
    description: str = Field(..., max_length=200, description="Brief model description")
    provider: Literal["openai", "anthropic", "ollama"] = Field(
        ...,  # Required - no default
        description="Provider identifier: 'openai', 'anthropic', or 'ollama'"
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

        # Check exactly one default model across all providers
        default_count = sum(1 for model in v if model.default)
        if default_count == 0:
            raise ValueError("Exactly one model must be marked as default")
        if default_count > 1:
            raise ValueError("Only one model can be marked as default across all providers")

        return v


def check_provider_enabled(provider_id: str) -> bool:
    """
    Check if a provider is enabled.

    For providers with API keys: True if the API key environment variable is set.
    For providers without API keys (like Ollama): True if models are configured.

    Args:
        provider_id: Provider identifier ('openai', 'anthropic', or 'ollama')

    Returns:
        bool: True if the provider is enabled, False otherwise
    """
    if provider_id not in PROVIDERS:
        return False

    api_key_env = PROVIDERS[provider_id].get("api_key_env")

    # Providers without API key requirement (like Ollama) are enabled if models are configured
    if api_key_env is None:
        if provider_id in PROVIDER_ENV_VARS:
            models_json = os.getenv(PROVIDER_ENV_VARS[provider_id])
            return bool(models_json and models_json.strip())
        return False

    # Providers with API key requirement
    api_key = os.getenv(api_key_env)
    return bool(api_key and api_key.strip())


def load_provider_models(provider_id: str) -> List[ProviderModelConfig]:
    """
    Load models from a provider-specific environment variable.

    Args:
        provider_id: Provider identifier ('openai' or 'anthropic')

    Returns:
        List[ProviderModelConfig]: List of validated model configs for this provider

    Raises:
        ModelConfigurationError: If the env var contains invalid JSON or model data
    """
    if provider_id not in PROVIDER_ENV_VARS:
        return []

    env_var_name = PROVIDER_ENV_VARS[provider_id]
    models_json = os.getenv(env_var_name)

    if not models_json:
        return []

    try:
        models_data = json.loads(models_json)
        if not isinstance(models_data, list):
            raise ModelConfigurationError(
                f"{env_var_name} must be a JSON array",
                f'Set {env_var_name} to a JSON array: \'[{{"id": "model-id", "name": "...", "description": "..."}}]\''
            )
    except json.JSONDecodeError as e:
        raise ModelConfigurationError(
            f"Invalid JSON in {env_var_name}: {str(e)}",
            f"Ensure {env_var_name} contains valid JSON."
        ) from e

    models: List[ProviderModelConfig] = []
    for i, model_data in enumerate(models_data):
        try:
            model = ProviderModelConfig(**model_data)
            models.append(model)
        except ValueError as e:
            raise ModelConfigurationError(
                f"Invalid model configuration in {env_var_name} at index {i}: {str(e)}",
                f"Each model in {env_var_name} must have: id, name, description."
            ) from e

    return models


def load_model_configuration() -> ModelsConfiguration:
    """
    Load model configuration from provider-specific environment variables.

    Models are loaded from OPENAI_MODELS and ANTHROPIC_MODELS env vars.
    Each model only needs id, name, description - the provider is inferred from
    the env var source. The default model is specified via DEFAULT_MODEL env var.

    The legacy MODELS env var is silently ignored.

    Returns:
        ModelsConfiguration: Validated model configuration with all enabled models

    Raises:
        ModelConfigurationError: If configuration is invalid or no models available
    """
    # Check provider enablement status
    openai_enabled = check_provider_enabled("openai")
    anthropic_enabled = check_provider_enabled("anthropic")
    ollama_enabled = check_provider_enabled("ollama")

    # Log provider enablement status
    logger.info(f"Provider status: OpenAI={'enabled' if openai_enabled else 'disabled'}, "
                f"Anthropic={'enabled' if anthropic_enabled else 'disabled'}, "
                f"Ollama={'enabled' if ollama_enabled else 'disabled'}")

    # Validate at least one provider is configured
    if not openai_enabled and not anthropic_enabled and not ollama_enabled:
        raise ModelConfigurationError(
            "No AI providers configured",
            "At least one provider must be configured. Set either:\n"
            "- OPENAI_API_KEY for OpenAI, or\n"
            "- ANTHROPIC_API_KEY for Anthropic, or\n"
            "- OLLAMA_MODELS for Ollama (local server, no API key required)\n"
            "And configure models in the corresponding *_MODELS environment variable."
        )

    # Load models from provider-specific env vars (018-separate-provider-configs)
    all_models: List[ModelConfig] = []
    seen_ids: Dict[str, str] = {}  # model_id -> provider (for duplicate detection)

    # Process providers in alphabetical order for deterministic fallback behavior
    for provider_id in sorted(PROVIDER_ENV_VARS.keys()):
        if not check_provider_enabled(provider_id):
            logger.debug(f"Skipping {provider_id} models - provider not enabled")
            continue

        provider_models = load_provider_models(provider_id)

        for pmodel in provider_models:
            # Check for duplicate model IDs across providers
            if pmodel.id in seen_ids:
                other_provider = seen_ids[pmodel.id]
                raise ModelConfigurationError(
                    f"Duplicate model ID '{pmodel.id}' found in both {PROVIDER_ENV_VARS[other_provider]} and {PROVIDER_ENV_VARS[provider_id]}",
                    "Model IDs must be unique across all providers."
                )
            seen_ids[pmodel.id] = provider_id

            # Convert ProviderModelConfig to full ModelConfig with provider and default=False
            # (default will be set later based on DEFAULT_MODEL)
            full_model = ModelConfig(
                id=pmodel.id,
                name=pmodel.name,
                description=pmodel.description,
                provider=provider_id,
                default=False
            )
            all_models.append(full_model)

        logger.info(f"Loaded {len(provider_models)} model(s) from {PROVIDER_ENV_VARS[provider_id]}")

    # Validate we have at least one model after filtering
    if not all_models:
        raise ModelConfigurationError(
            "No models available for enabled providers",
            "Configure models in OPENAI_MODELS, ANTHROPIC_MODELS, or OLLAMA_MODELS for enabled providers."
        )

    # Resolve default model from DEFAULT_MODEL env var
    default_model_id = os.getenv("DEFAULT_MODEL")
    default_model_index: Optional[int] = None

    if default_model_id:
        default_model_id = default_model_id.strip()
        # Find the model with this ID
        for i, model in enumerate(all_models):
            if model.id == default_model_id:
                default_model_index = i
                break

        if default_model_index is None:
            # DEFAULT_MODEL references a model that doesn't exist or is filtered out
            # Check if it exists in any provider config but is filtered due to disabled provider
            model_exists_but_filtered = False
            for provider_id in PROVIDER_ENV_VARS.keys():
                if not check_provider_enabled(provider_id):
                    provider_models = load_provider_models(provider_id)
                    if any(m.id == default_model_id for m in provider_models):
                        model_exists_but_filtered = True
                        logger.warning(
                            f"DEFAULT_MODEL '{default_model_id}' references a model from "
                            f"provider '{provider_id}' which is disabled. Using fallback."
                        )
                        break

            if not model_exists_but_filtered:
                raise ModelConfigurationError(
                    f"Invalid DEFAULT_MODEL: '{default_model_id}' not found in any provider configuration",
                    f"Set DEFAULT_MODEL to a valid model ID from OPENAI_MODELS, ANTHROPIC_MODELS, or OLLAMA_MODELS."
                )

    # Set the default model (either from DEFAULT_MODEL or fallback to first available)
    if default_model_index is not None:
        # Mark the specified default model
        model = all_models[default_model_index]
        all_models[default_model_index] = ModelConfig(
            id=model.id,
            name=model.name,
            description=model.description,
            provider=model.provider,
            default=True
        )
        logger.info(f"Using '{default_model_id}' as default model (from DEFAULT_MODEL)")
    else:
        # Fallback to first model (alphabetical provider order ensures deterministic behavior)
        first_model = all_models[0]
        all_models[0] = ModelConfig(
            id=first_model.id,
            name=first_model.name,
            description=first_model.description,
            provider=first_model.provider,
            default=True
        )
        if default_model_id:
            logger.info(f"DEFAULT_MODEL provider disabled, using '{first_model.id}' as fallback default")
        else:
            logger.info(f"DEFAULT_MODEL not set, using '{first_model.id}' as default")

    try:
        return ModelsConfiguration(models=all_models)
    except ValueError as e:
        raise ModelConfigurationError(
            f"Invalid model configuration: {str(e)}",
            "Check your OPENAI_MODELS, ANTHROPIC_MODELS, and OLLAMA_MODELS configuration."
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
        Optional[str]: Provider ID ('openai', 'anthropic', or 'ollama') if found, None otherwise
    """
    model = get_model_by_id(model_id, config)
    return model.provider if model else None


# =============================================================================
# Title Model Configuration (Feature: 019-llm-conversation-titles)
# =============================================================================

# Title model env var names per provider
TITLE_MODEL_ENV_VARS: Dict[str, str] = {
    "openai": "OPENAI_TITLE_MODEL",
    "anthropic": "ANTHROPIC_TITLE_MODEL",
}


def load_title_model_config() -> Dict[str, str]:
    """
    Load title model configuration from environment variables.

    Returns:
        Dict[str, str]: Mapping of provider ID to title model ID
                       Empty dict if no title models are configured
    """
    config: Dict[str, str] = {}

    for provider_id, env_var in TITLE_MODEL_ENV_VARS.items():
        title_model = os.getenv(env_var)
        if title_model and title_model.strip():
            config[provider_id] = title_model.strip()
            logger.debug(f"Loaded title model for {provider_id}: {config[provider_id]}")

    if config:
        logger.info(f"Title model configuration loaded: {config}")
    else:
        logger.debug("No title models configured - will use conversation model")

    return config


def get_title_model_for_provider(provider_id: str) -> Optional[str]:
    """
    Get the configured title model for a provider.

    Args:
        provider_id: Provider identifier ('openai' or 'anthropic')

    Returns:
        Optional[str]: Title model ID if configured, None otherwise
    """
    if provider_id not in TITLE_MODEL_ENV_VARS:
        return None

    env_var = TITLE_MODEL_ENV_VARS[provider_id]
    title_model = os.getenv(env_var)

    if title_model and title_model.strip():
        return title_model.strip()

    return None
