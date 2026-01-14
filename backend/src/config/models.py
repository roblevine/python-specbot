"""
Model Configuration Module

Manages OpenAI model configuration from environment variables.
Supports both multi-model (OPENAI_MODELS) and single-model (OPENAI_MODEL) configurations.
"""

import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


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
    """Configuration for a single OpenAI model."""

    id: str = Field(..., description="OpenAI model identifier (e.g., 'gpt-4')")
    name: str = Field(..., max_length=50, description="Human-readable display name")
    description: str = Field(..., max_length=200, description="Brief model description")
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
    """Root configuration for available models."""

    models: List[ModelConfig] = Field(..., min_length=1, description="List of available models")

    @field_validator('models')
    @classmethod
    def validate_models(cls, v: List[ModelConfig]) -> List[ModelConfig]:
        """Validate model list constraints."""
        if not v:
            raise ValueError("At least one model must be configured")

        # Check for duplicate IDs
        ids = [model.id for model in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate model IDs found")

        # Check exactly one default model
        default_count = sum(1 for model in v if model.default)
        if default_count == 0:
            raise ValueError("Exactly one model must be marked as default")
        if default_count > 1:
            raise ValueError("Only one model can be marked as default")

        return v


def load_model_configuration() -> ModelsConfiguration:
    """
    Load model configuration from environment variables.

    Requires:
        OPENAI_MODELS: JSON array of model configurations

    Returns:
        ModelsConfiguration: Validated model configuration

    Raises:
        ModelConfigurationError: If configuration is invalid or missing
    """
    openai_models_env = os.getenv('OPENAI_MODELS')

    if not openai_models_env:
        raise ModelConfigurationError(
            "OPENAI_MODELS environment variable is required",
            "Set OPENAI_MODELS to a JSON array with at least one model:\n"
            "Example: OPENAI_MODELS='[{\"id\": \"gpt-3.5-turbo\", \"name\": \"GPT-3.5 Turbo\", "
            "\"description\": \"Fast and efficient for most tasks\", \"default\": true}]'"
        )

    try:
        models_data = json.loads(openai_models_env)
        if not isinstance(models_data, list):
            raise ModelConfigurationError(
                "OPENAI_MODELS must be a JSON array",
                "Set OPENAI_MODELS to a JSON array: '[{\"id\": \"gpt-4\", \"name\": \"GPT-4\", "
                "\"description\": \"Most capable\", \"default\": true}]'"
            )

        if len(models_data) == 0:
            raise ModelConfigurationError(
                "OPENAI_MODELS cannot be an empty array",
                "Add at least one model to the array"
            )

        try:
            models = [ModelConfig(**model_data) for model_data in models_data]
            return ModelsConfiguration(models=models)
        except ValueError as e:
            # Re-raise pydantic validation errors with context
            raise ModelConfigurationError(
                f"Invalid model configuration in OPENAI_MODELS: {str(e)}",
                "Each model must have: id (string), name (string), description (string), "
                "default (boolean). Exactly one model must have default=true."
            ) from e

    except json.JSONDecodeError as e:
        raise ModelConfigurationError(
            f"Invalid JSON in OPENAI_MODELS: {str(e)}",
            "Ensure OPENAI_MODELS contains valid JSON. Example: "
            "'[{\"id\": \"gpt-4\", \"name\": \"GPT-4\", \"description\": \"Most capable\", \"default\": true}]'"
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
