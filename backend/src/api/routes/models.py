"""
Models API Routes

Provides endpoints for retrieving available OpenAI models.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging

from src.config.models import load_model_configuration, ModelsConfiguration, ModelConfigurationError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["models"])


class ModelInfo(BaseModel):
    """Model information for API responses."""

    id: str = Field(..., description="Model identifier for API requests")
    name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="Brief model description")
    default: bool = Field(..., description="Whether this is the default model")


class ModelsResponse(BaseModel):
    """Response containing available models."""

    models: List[ModelInfo] = Field(..., description="List of available models")


@router.get("/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """
    List available OpenAI models.

    Returns the list of models configured in the system via environment variables.
    Frontend uses this to populate the model selector dropdown.

    Returns:
        ModelsResponse: List of available models with their metadata

    Raises:
        HTTPException: 503 Service Unavailable if models cannot be loaded
    """
    try:
        config = load_model_configuration()
        logger.info(f"Loaded {len(config.models)} models from configuration")

        model_infos = [
            ModelInfo(
                id=model.id,
                name=model.name,
                description=model.description,
                default=model.default
            )
            for model in config.models
        ]

        return ModelsResponse(models=model_infos)

    except ModelConfigurationError as e:
        logger.error(f"Model configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error loading model configuration: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: Unable to load model configuration. {str(e)}"
        ) from e
