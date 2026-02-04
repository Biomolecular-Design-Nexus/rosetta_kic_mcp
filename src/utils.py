"""Shared utilities for MCP server."""

import sys
from pathlib import Path
from typing import Dict, Any, Union
from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>"
    )


def validate_input_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Validate that an input file exists and is readable.

    Args:
        file_path: Path to the file to validate

    Returns:
        Dictionary with validation result
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "valid": False,
                "error": f"File not found: {file_path}"
            }

        if not path.is_file():
            return {
                "valid": False,
                "error": f"Path is not a file: {file_path}"
            }

        if not path.stat().st_size > 0:
            return {
                "valid": False,
                "error": f"File is empty: {file_path}"
            }

        return {
            "valid": True,
            "path": str(path.resolve()),
            "size_bytes": path.stat().st_size
        }

    except Exception as e:
        return {
            "valid": False,
            "error": f"File validation error: {e}"
        }


def standardize_error_response(error_msg: str, error_type: str = "error") -> Dict[str, Any]:
    """Create a standardized error response.

    Args:
        error_msg: Error message
        error_type: Type of error

    Returns:
        Standardized error dictionary
    """
    return {
        "status": "error",
        "error": error_msg,
        "error_type": error_type
    }


def standardize_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a standardized success response.

    Args:
        data: Response data

    Returns:
        Standardized success dictionary
    """
    return {
        "status": "success",
        **data
    }