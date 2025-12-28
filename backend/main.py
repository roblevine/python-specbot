"""
SpecBot Backend API Server

Feature: 003-backend-api-loopback
Framework: FastAPI 0.115.0
Python: 3.13+
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting SpecBot Backend API Server")
    logger.info(f"Server configuration: host={API_HOST}, port={API_PORT}")
    logger.info(f"CORS allowed origins: {FRONTEND_URL}")
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
