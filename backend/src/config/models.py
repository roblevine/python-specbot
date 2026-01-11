"""
Model Configuration Module

Manages OpenAI model configuration from environment variables.
Supports both multi-model (OPENAI_MODELS) and single-model (OPENAI_MODEL) configurations.
"""

import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


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

    Priority:
    1. OPENAI_MODELS: JSON array of model configurations
    2. OPENAI_MODEL: Single model ID (fallback)

    Returns:
        ModelsConfiguration: Validated model configuration

    Raises:
        ValueError: If configuration is invalid or missing
        json.JSONDecodeError: If OPENAI_MODELS is not valid JSON
    """
    # Try OPENAI_MODELS first (multi-model configuration)
    openai_models_env = os.getenv('OPENAI_MODELS')
    if openai_models_env:
        try:
            models_data = json.loads(openai_models_env)
            if not isinstance(models_data, list):
                raise ValueError("OPENAI_MODELS must be a JSON array")

            models = [ModelConfig(**model_data) for model_data in models_data]
            return ModelsConfiguration(models=models)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in OPENAI_MODELS: {e}") from e

    # Fallback to OPENAI_MODEL (single-model configuration)
    openai_model_env = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    # Generate single model configuration with sensible defaults
    model_name_map = {
        'gpt-4': 'GPT-4',
        'gpt-4-turbo': 'GPT-4 Turbo',
        'gpt-3.5-turbo': 'GPT-3.5 Turbo',
        'gpt-4o': 'GPT-4o',
        'gpt-4o-mini': 'GPT-4o Mini',
    }

    model_description_map = {
        'gpt-4': 'Most capable model for complex reasoning tasks',
        'gpt-4-turbo': 'Faster GPT-4 with latest knowledge',
        'gpt-3.5-turbo': 'Fast and efficient for most tasks',
        'gpt-4o': 'High performance multimodal model',
        'gpt-4o-mini': 'Affordable and efficient model',
    }

    model_name = model_name_map.get(openai_model_env, openai_model_env.upper())
    model_description = model_description_map.get(
        openai_model_env,
        f"OpenAI model: {openai_model_env}"
    )

    single_model = ModelConfig(
        id=openai_model_env,
        name=model_name,
        description=model_description,
        default=True
    )

    return ModelsConfiguration(models=[single_model])


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
