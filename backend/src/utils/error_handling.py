"""
Secure Error Handling Utilities

Provides safe error handling that prevents sensitive information exposure.
Logs detailed errors server-side but returns sanitized errors to clients.

Feature: Security Hardening
"""

import os
import traceback
from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


def is_debug_mode() -> bool:
    """
    Check if DEBUG mode is enabled.
    
    Returns:
        True if DEBUG mode is enabled
    """
    return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")


def is_production_environment() -> bool:
    """
    Check if running in production environment.
    
    Returns:
        True if ENVIRONMENT is set to "production"
    """
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def get_safe_error_response(
    error: Exception,
    user_message: str,
    error_code: str = "INTERNAL_ERROR",
    include_error_id: bool = True
) -> Dict[str, Any]:
    """
    Generate a safe error response for API clients.
    
    In production:
    - Never exposes stack traces or internal details
    - Returns generic error message with error ID for tracking
    - Logs full details server-side
    
    In development with DEBUG:
    - Can include debug_info if explicitly enabled
    - Still logs full details server-side
    
    Args:
        error: The exception that occurred
        user_message: User-friendly error message
        error_code: Error code for categorization
        include_error_id: Whether to include an error ID (default: True)
        
    Returns:
        Dict suitable for JSON response
    """
    from datetime import datetime
    import uuid
    
    # Generate error ID for tracking
    error_id = str(uuid.uuid4())[:8] if include_error_id else None
    
    # Get full error details for logging
    error_type = type(error).__name__
    error_message = str(error)
    original_error = getattr(error, 'original_error', None)
    tb = traceback.format_exc()
    
    # Always log full details server-side
    logger.error(
        f"Error ID {error_id}: {error_type}: {error_message}",
        extra={
            "error_id": error_id,
            "error_type": error_type,
            "error_message": error_message,
            "original_error": str(original_error) if original_error else None,
            "user_message": user_message,
            "error_code": error_code,
        }
    )
    logger.debug(f"Traceback for error ID {error_id}:\n{tb}")
    
    # Build response
    response: Dict[str, Any] = {
        "status": "error",
        "error": user_message,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    }
    
    if error_id:
        response["error_id"] = error_id
    
    # Only include debug info in development with DEBUG=true
    # NEVER in production
    if is_debug_mode() and not is_production_environment():
        response["debug_info"] = {
            "error_type": error_type,
            "error_message": error_message,
            "original_error": str(original_error) if original_error else None,
            "traceback": tb
        }
        logger.warning(
            f"DEBUG mode enabled (non-production) - including debug_info in response for error {error_id}"
        )
    elif is_debug_mode() and is_production_environment():
        # DEBUG is enabled but we're in production - block it!
        logger.error(
            "⚠️ SECURITY VIOLATION: DEBUG mode is enabled in PRODUCTION environment! "
            "Debug information will NOT be exposed. Set DEBUG=false immediately!"
        )
    
    return response


def validate_environment_security():
    """
    Validate that security settings are appropriate for the environment.
    
    Logs warnings for unsafe configurations.
    Should be called at application startup.
    """
    is_prod = is_production_environment()
    is_debug = is_debug_mode()
    
    if is_prod and is_debug:
        logger.error(
            "⚠️ CRITICAL SECURITY ISSUE: DEBUG mode is enabled in PRODUCTION! "
            "This is a security risk. Set DEBUG=false immediately!"
        )
        logger.error(
            "Debug information exposure has been blocked, but DEBUG mode should never be enabled in production."
        )
    elif is_debug:
        logger.warning(
            "⚠️ DEBUG MODE ENABLED - Detailed error messages will be exposed in API responses"
        )
        logger.warning(
            "⚠️ Never use DEBUG mode in production! Set ENVIRONMENT=production to prevent debug exposure."
        )
    elif is_prod:
        logger.info("✓ Running in production mode with DEBUG disabled (secure)")
    else:
        logger.info("Running in development mode with DEBUG disabled")
