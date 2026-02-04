"""
General utilities for cyclic peptide scripts.

Common helper functions for file management, formatting, and other utilities.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

def create_output_dir(base_path: Union[str, Path], prefix: str = "output", timestamp: bool = True) -> Path:
    """
    Create output directory with optional timestamp.

    Args:
        base_path: Base directory or file path
        prefix: Directory name prefix
        timestamp: Whether to add timestamp to directory name

    Returns:
        Path to created directory
    """
    base_path = Path(base_path)

    if base_path.suffix:
        # It's a file path, use parent directory
        parent_dir = base_path.parent
        name_base = base_path.stem
    else:
        # It's a directory path
        parent_dir = base_path.parent
        name_base = base_path.name or prefix

    if timestamp:
        timestamp_str = generate_timestamp()
        dir_name = f"{name_base}_{timestamp_str}"
    else:
        dir_name = name_base

    output_dir = parent_dir / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir

def generate_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Generate timestamp string.

    Args:
        format_str: strftime format string

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_str)

def format_energy(energy: float, precision: int = 2) -> str:
    """
    Format energy value for display.

    Args:
        energy: Energy value
        precision: Number of decimal places

    Returns:
        Formatted energy string
    """
    return f"{energy:.{precision}f}"

def format_time(seconds: float) -> str:
    """
    Format time duration for display.

    Args:
        seconds: Duration in seconds

    Returns:
        Human-readable time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_size(size_bytes: int) -> str:
    """
    Format file size for display.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f}KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f}MB"
    else:
        return f"{size_bytes/(1024**3):.1f}GB"

def safe_filename(filename: str, replacement: str = "_") -> str:
    """
    Create safe filename by replacing problematic characters.

    Args:
        filename: Original filename
        replacement: Character to replace problematic chars with

    Returns:
        Safe filename string
    """
    # Characters that are problematic in filenames
    problematic_chars = '<>:"/\\|?*'

    safe_name = filename
    for char in problematic_chars:
        safe_name = safe_name.replace(char, replacement)

    # Remove multiple consecutive replacement characters
    while replacement + replacement in safe_name:
        safe_name = safe_name.replace(replacement + replacement, replacement)

    # Strip replacement characters from ends
    safe_name = safe_name.strip(replacement)

    return safe_name

def copy_file_with_backup(src_path: Union[str, Path], dst_path: Union[str, Path],
                         backup: bool = True) -> Path:
    """
    Copy file with optional backup of existing destination.

    Args:
        src_path: Source file path
        dst_path: Destination file path
        backup: Whether to backup existing destination

    Returns:
        Path to destination file
    """
    import shutil

    src_path = Path(src_path)
    dst_path = Path(dst_path)

    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")

    # Create destination directory if needed
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing file if requested
    if backup and dst_path.exists():
        timestamp = generate_timestamp()
        backup_path = dst_path.with_name(f"{dst_path.stem}_{timestamp}_backup{dst_path.suffix}")
        shutil.copy2(dst_path, backup_path)

    # Copy file
    shutil.copy2(src_path, dst_path)
    return dst_path

def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a file.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return {"exists": False, "path": str(file_path)}

    stat = file_path.stat()

    return {
        "exists": True,
        "path": str(file_path),
        "name": file_path.name,
        "size": stat.st_size,
        "size_formatted": format_size(stat.st_size),
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "modified_formatted": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "suffix": file_path.suffix,
        "parent": str(file_path.parent)
    }

def create_progress_tracker(total: int, desc: str = "Progress") -> callable:
    """
    Create a simple progress tracking function.

    Args:
        total: Total number of items
        desc: Description for progress display

    Returns:
        Function to call for progress updates
    """
    start_time = time.time()

    def update_progress(current: int, status: str = ""):
        elapsed = time.time() - start_time
        percent = (current / total) * 100 if total > 0 else 0

        if current > 0:
            rate = current / elapsed
            eta = (total - current) / rate if rate > 0 else 0
            print(f"\r{desc}: {current}/{total} ({percent:.1f}%) - {format_time(elapsed)} elapsed, {format_time(eta)} remaining {status}", end="", flush=True)
        else:
            print(f"\r{desc}: {current}/{total} ({percent:.1f}%) {status}", end="", flush=True)

        if current >= total:
            print()  # New line when complete

    return update_progress

def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    Later configs override earlier ones.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration dictionary
    """
    merged = {}

    for config in configs:
        if config:
            merged.update(config)

    return merged

def filter_dict(data: Dict[str, Any], keys: List[str], exclude: bool = False) -> Dict[str, Any]:
    """
    Filter dictionary by keys.

    Args:
        data: Dictionary to filter
        keys: List of keys to include/exclude
        exclude: If True, exclude the keys; if False, include only the keys

    Returns:
        Filtered dictionary
    """
    if exclude:
        return {k: v for k, v in data.items() if k not in keys}
    else:
        return {k: v for k, v in data.items() if k in keys}

def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten nested dictionary.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []

    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)

def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.

    Args:
        data: List to chunk
        chunk_size: Maximum size of each chunk

    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def retry_operation(func: callable, max_retries: int = 3, delay: float = 1.0,
                   backoff: float = 2.0) -> Any:
    """
    Retry operation with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    current_delay = delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed, retrying in {current_delay:.1f}s...")
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                raise last_exception

def log_execution(func: callable) -> callable:
    """
    Decorator to log function execution time and results.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__

        print(f"Starting {func_name}...")

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            print(f"Completed {func_name} in {format_time(elapsed)}")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"Failed {func_name} after {format_time(elapsed)}: {e}")
            raise

    return wrapper