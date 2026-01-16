"""
Models API Routes

Provides endpoints for retrieving available models from all configured providers.
Feature: 011-anthropic-support
"""

import os
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging

from src.config.models import load_model_configuration, ModelsConfiguration, ModelConfigurationError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["models"])


def is_debug_mode() -> bool:
    """Check if DEBUG mode is enabled (checked at runtime, not import time)."""
    return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


class ModelInfo(BaseModel):
    """Model information for API responses."""

    id: str = Field(..., description="Model identifier for API requests")
    name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="Brief model description")
    provider: str = Field(..., description="Provider identifier: 'openai' or 'anthropic'")
    default: bool = Field(..., description="Whether this is the default model")


class ModelsResponse(BaseModel):
    """Response containing available models."""

    models: List[ModelInfo] = Field(..., description="List of available models")


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """
    List available models from all configured providers.

    Returns the list of models configured in the system via environment variables.
    Frontend uses this to populate the model selector dropdown.

    Returns:
        ModelsResponse: List of available models with their metadata including provider

    Raises:
        HTTPException: 503 Service Unavailable if models cannot be loaded
    """
    try:
        config = load_model_configuration()
        logger.info(f"Loaded {len(config.models)} models from configuration")

        # T019: Include provider field in response
        model_infos = [
            ModelInfo(
                id=model.id,
                name=model.name,
                description=model.description,
                provider=model.provider,
                default=model.default
            )
            for model in config.models
        ]

        return ModelsResponse(models=model_infos)

    except ModelConfigurationError as e:
        logger.error(f"Model configuration error: {e}")

        # Build error detail
        error_detail: Dict[str, Any] = {
            "message": f"Service unavailable: {str(e)}"
        }

        # In debug mode, include detailed error information
        if is_debug_mode():
            error_detail["debug_info"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "help_text": getattr(e, 'help_text', None),
                "traceback": traceback.format_exc()
            }
            logger.warning("DEBUG mode enabled - exposing detailed error information in API response")

        raise HTTPException(status_code=503, detail=error_detail) from e

    except Exception as e:
        logger.error(f"Unexpected error loading model configuration: {e}", exc_info=True)

        # Build error detail
        error_detail: Dict[str, Any] = {
            "message": "Service unavailable: Unable to load model configuration"
        }

        # In debug mode, include detailed error information
        if is_debug_mode():
            error_detail["debug_info"] = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            logger.warning("DEBUG mode enabled - exposing detailed error information in API response")

        raise HTTPException(status_code=503, detail=error_detail) from e
