"""
SpecBot Backend API Server

Feature: 003-backend-api-loopback
Framework: FastAPI 0.115.0
Python: 3.13+
"""

import os
from contextlib import asynccontextmanager

from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.utils.logger import get_logger
from src.middleware.logging_middleware import LoggingMiddleware

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Environment configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    from src.utils.error_handling import validate_environment_security
    
    logger.info("Starting SpecBot Backend API Server")
    logger.info(f"Server configuration: host={API_HOST}, port={API_PORT}")
    logger.info(f"CORS allowed origins: {FRONTEND_URL}")
    
    # Validate security configuration
    validate_environment_security()

    # T032: Load tool configuration at startup
    try:
        from src.config.tools import load_tool_configuration
        from src.services.tools import load_enabled_tools

        tool_configs = load_tool_configuration()
        config_dicts = [
            {"id": tc.id, "name": tc.name, "description": tc.description, "enabled": tc.enabled}
            for tc in tool_configs
        ]
        tools = load_enabled_tools(config_dicts)
        logger.info(f"Tool system initialized: {len(tools)} tool(s) available")
    except Exception as e:
        logger.warning(f"Tool system initialization failed: {e}. Continuing without tools.")

    yield
    logger.info("Shutting down SpecBot Backend API Server")


# Initialize FastAPI application
app = FastAPI(
    title="SpecBot Backend API",
    version="1.0.0",
    description="Backend API for SpecBot chat interface with message loopback functionality",
    lifespan=lifespan
)

# Configure CORS middleware with security best practices
# Only allow specific HTTP methods and headers needed for the API
from urllib.parse import urlparse

def validate_frontend_url(url: str) -> str:
    """
    Validate FRONTEND_URL format for security.
    
    Args:
        url: Frontend URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValueError: If URL is invalid
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid FRONTEND_URL format: {url}")
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"FRONTEND_URL must use http or https: {url}")
        return url
    except Exception as e:
        raise ValueError(f"Invalid FRONTEND_URL: {url}") from e

# Validate FRONTEND_URL
try:
    validated_frontend_url = validate_frontend_url(FRONTEND_URL)
    logger.info(f"FRONTEND_URL validated: {validated_frontend_url}")
except ValueError as e:
    logger.error(f"Invalid FRONTEND_URL configuration: {e}")
    logger.warning("Falling back to default localhost origins only")
    validated_frontend_url = None

# Build allowed origins list
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://0.0.0.0:5173",
]
if validated_frontend_url and validated_frontend_url not in allowed_origins:
    allowed_origins.append(validated_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    # Only allow specific HTTP methods needed by the API
    # Avoid wildcard "*" which allows all methods including dangerous ones
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # Only allow specific headers needed by the API
    # Avoid wildcard "*" which allows any custom headers
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)


# Custom exception handler for Pydantic validation errors
# Converts FastAPI's default 422 error format to our ErrorResponse schema
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors and return ErrorResponse format.

    This ensures ALL error responses match the OpenAPI contract,
    including 422 validation errors from Pydantic.
    """
    # Extract first error for user-friendly message
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = first_error.get("loc", ["unknown"])[-1]
    error_type = first_error.get("type", "validation_error")

    # Create user-friendly error message
    if error_type == "string_too_short":
        error_message = f"{field.capitalize()} cannot be empty"
    elif error_type == "missing":
        error_message = f"{field.capitalize()} is required"
    else:
        error_message = "Invalid request format"

    logger.warning(f"Validation error: {error_message}", extra={"errors": errors})

    # Return ErrorResponse format matching OpenAPI contract
    # Note: detail is optional and should be an object (not array) per OpenAPI schema
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": error_message,
            "detail": {
                "field": str(field),
                "issue": first_error.get("msg", "Validation error"),
                "type": error_type
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


# Health check endpoint
@app.get("/health", tags=["monitoring"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {"status": "ok"}


# T038: Register API routes
from src.api.routes.messages import router as messages_router
from src.api.routes.models import router as models_router
from src.api.routes.conversations import router as conversations_router
from src.api.routes.titles import router as titles_router  # Feature: 019-llm-conversation-titles

app.include_router(messages_router, prefix="/api/v1")
app.include_router(models_router, prefix="/api/v1")
app.include_router(conversations_router)  # Already has /api/v1 prefix
app.include_router(titles_router, prefix="/api/v1")  # Title generation endpoint


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server with uvicorn...")
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="debug"
    )
