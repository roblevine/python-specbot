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
    logger.info("Starting SpecBot Backend API Server")
    logger.info(f"Server configuration: host={API_HOST}, port={API_PORT}")
    logger.info(f"CORS allowed origins: {FRONTEND_URL}")
    if DEBUG:
        logger.warning("⚠️  DEBUG MODE ENABLED - Detailed error messages will be exposed in API responses")
        logger.warning("⚠️  Never use DEBUG mode in production!")
    else:
        logger.info("DEBUG mode disabled - Error details will be hidden in API responses")
    yield
    logger.info("Shutting down SpecBot Backend API Server")


# Initialize FastAPI application
app = FastAPI(
    title="SpecBot Backend API",
    version="1.0.0",
    description="Backend API for SpecBot chat interface with message loopback functionality",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(messages_router, prefix="/api/v1")


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
