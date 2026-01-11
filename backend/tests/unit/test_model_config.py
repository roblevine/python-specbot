"""
Unit Tests for Model Configuration

Tests the model configuration schema, loader, and validation.

Feature: 008-openai-model-selector User Story 1
Task: T014 (TDD - these should FAIL before implementation is complete)
"""

import pytest
import json
import os
from pydantic import ValidationError

from src.config.models import (
    ModelConfig,
    ModelsConfiguration,
    load_model_configuration,
    get_default_model,
    validate_model_id,
    get_model_by_id
)


class TestModelConfig:
    """Tests for ModelConfig schema."""

    def test_valid_model_config(self):
        """Test creating a valid model configuration."""
        model = ModelConfig(
            id="gpt-4",
            name="GPT-4",
            description="Most capable model",
            default=False
        )

        assert model.id == "gpt-4"
        assert model.name == "GPT-4"
        assert model.description == "Most capable model"
        assert model.default is False

    def test_model_config_with_default_true(self):
        """Test model configuration with default=True."""
        model = ModelConfig(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            description="Fast and efficient",
            default=True
        )

        assert model.default is True

    def test_model_config_strips_whitespace(self):
        """Test that whitespace is stripped from string fields."""
        model = ModelConfig(
            id="  gpt-4  ",
            name="  GPT-4  ",
            description="  Description  ",
            default=False
        )

        assert model.id == "gpt-4"
        assert model.name == "GPT-4"
        assert model.description == "Description"

    def test_model_config_rejects_empty_id(self):
        """Test that empty model ID is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                id="",
                name="GPT-4",
                description="Description",
                default=False
            )

        assert "Model ID cannot be empty" in str(exc_info.value)

    def test_model_config_rejects_whitespace_only_id(self):
        """Test that whitespace-only model ID is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                id="   ",
                name="GPT-4",
                description="Description",
                default=False
            )

        assert "Model ID cannot be empty" in str(exc_info.value)

    def test_model_config_rejects_empty_name(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                id="gpt-4",
                name="",
                description="Description",
                default=False
            )

        assert "Model name cannot be empty" in str(exc_info.value)

    def test_model_config_rejects_empty_description(self):
        """Test that empty description is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="",
                default=False
            )

        assert "Model description cannot be empty" in str(exc_info.value)


class TestModelsConfiguration:
    """Tests for ModelsConfiguration schema."""

    def test_valid_configuration_single_model(self):
        """Test configuration with a single model."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=True
            )
        ])

        assert len(config.models) == 1
        assert config.models[0].id == "gpt-4"

    def test_valid_configuration_multiple_models(self):
        """Test configuration with multiple models."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=False
            ),
            ModelConfig(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="Description",
                default=True
            )
        ])

        assert len(config.models) == 2

    def test_rejects_empty_models_list(self):
        """Test that empty models list is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ModelsConfiguration(models=[])

        assert "At least one model must be configured" in str(exc_info.value)

    def test_rejects_duplicate_model_ids(self):
        """Test that duplicate model IDs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ModelsConfiguration(models=[
                ModelConfig(
                    id="gpt-4",
                    name="GPT-4",
                    description="Description",
                    default=True
                ),
                ModelConfig(
                    id="gpt-4",  # Duplicate
                    name="GPT-4 Duplicate",
                    description="Description",
                    default=False
                )
            ])

        assert "Duplicate model IDs found" in str(exc_info.value)

    def test_rejects_no_default_model(self):
        """Test that at least one default model is required."""
        with pytest.raises(ValidationError) as exc_info:
            ModelsConfiguration(models=[
                ModelConfig(
                    id="gpt-4",
                    name="GPT-4",
                    description="Description",
                    default=False
                )
            ])

        assert "Exactly one model must be marked as default" in str(exc_info.value)

    def test_rejects_multiple_default_models(self):
        """Test that only one default model is allowed."""
        with pytest.raises(ValidationError) as exc_info:
            ModelsConfiguration(models=[
                ModelConfig(
                    id="gpt-4",
                    name="GPT-4",
                    description="Description",
                    default=True
                ),
                ModelConfig(
                    id="gpt-3.5-turbo",
                    name="GPT-3.5 Turbo",
                    description="Description",
                    default=True  # Multiple defaults
                )
            ])

        assert "Only one model can be marked as default" in str(exc_info.value)


class TestLoadModelConfiguration:
    """Tests for load_model_configuration function."""

    def test_load_from_openai_models_env_var(self, monkeypatch):
        """Test loading configuration from OPENAI_MODELS environment variable."""
        models_json = json.dumps([
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Most capable",
                "default": False
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and efficient",
                "default": True
            }
        ])

        monkeypatch.setenv('OPENAI_MODELS', models_json)

        config = load_model_configuration()

        assert len(config.models) == 2
        assert config.models[0].id == "gpt-4"
        assert config.models[1].id == "gpt-3.5-turbo"

    def test_fallback_to_openai_model_env_var(self, monkeypatch):
        """Test fallback to OPENAI_MODEL when OPENAI_MODELS not set."""
        monkeypatch.delenv('OPENAI_MODELS', raising=False)
        monkeypatch.setenv('OPENAI_MODEL', 'gpt-4')

        config = load_model_configuration()

        assert len(config.models) == 1
        assert config.models[0].id == "gpt-4"
        assert config.models[0].name == "GPT-4"
        assert config.models[0].default is True

    def test_fallback_to_default_gpt35_turbo(self, monkeypatch):
        """Test fallback to gpt-3.5-turbo when no env vars set."""
        monkeypatch.delenv('OPENAI_MODELS', raising=False)
        monkeypatch.delenv('OPENAI_MODEL', raising=False)

        config = load_model_configuration()

        assert len(config.models) == 1
        assert config.models[0].id == "gpt-3.5-turbo"
        assert config.models[0].default is True

    def test_rejects_invalid_json(self, monkeypatch):
        """Test that invalid JSON in OPENAI_MODELS raises error."""
        monkeypatch.setenv('OPENAI_MODELS', 'not valid json')

        with pytest.raises(ValueError) as exc_info:
            load_model_configuration()

        assert "Invalid JSON in OPENAI_MODELS" in str(exc_info.value)

    def test_rejects_non_array_json(self, monkeypatch):
        """Test that non-array JSON is rejected."""
        monkeypatch.setenv('OPENAI_MODELS', '{"not": "an array"}')

        with pytest.raises(ValueError) as exc_info:
            load_model_configuration()

        assert "OPENAI_MODELS must be a JSON array" in str(exc_info.value)


class TestGetDefaultModel:
    """Tests for get_default_model function."""

    def test_returns_default_model_id(self):
        """Test that default model ID is returned."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=False
            ),
            ModelConfig(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="Description",
                default=True
            )
        ])

        default_id = get_default_model(config)
        assert default_id == "gpt-3.5-turbo"

    def test_returns_first_model_as_fallback(self):
        """Test fallback to first model (should never happen due to validation)."""
        # This bypasses validation to test the fallback logic
        config = ModelsConfiguration.__new__(ModelsConfiguration)
        config.models = [
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=False
            )
        ]

        default_id = get_default_model(config)
        assert default_id == "gpt-4"


class TestValidateModelId:
    """Tests for validate_model_id function."""

    def test_valid_model_id_returns_true(self):
        """Test that valid model ID returns True."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=True
            )
        ])

        assert validate_model_id("gpt-4", config) is True

    def test_invalid_model_id_returns_false(self):
        """Test that invalid model ID returns False."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=True
            )
        ])

        assert validate_model_id("gpt-5", config) is False

    def test_case_sensitive_validation(self):
        """Test that model ID validation is case-sensitive."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=True
            )
        ])

        assert validate_model_id("GPT-4", config) is False


class TestGetModelById:
    """Tests for get_model_by_id function."""

    def test_returns_model_when_found(self):
        """Test that model is returned when ID matches."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=True
            ),
            ModelConfig(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="Description",
                default=False
            )
        ])

        model = get_model_by_id("gpt-3.5-turbo", config)

        assert model is not None
        assert model.id == "gpt-3.5-turbo"
        assert model.name == "GPT-3.5 Turbo"

    def test_returns_none_when_not_found(self):
        """Test that None is returned when model ID not found."""
        config = ModelsConfiguration(models=[
            ModelConfig(
                id="gpt-4",
                name="GPT-4",
                description="Description",
                default=True
            )
        ])

        model = get_model_by_id("gpt-5", config)

        assert model is None
