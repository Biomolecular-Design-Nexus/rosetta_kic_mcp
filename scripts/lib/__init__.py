"""
Shared library for cyclic peptide MCP scripts.

This library contains common utilities extracted and simplified from the original
repository code to minimize dependencies and provide clean, reusable functions.
"""

from .io import load_pdb, save_pdb, load_sequence, save_sequence
from .validation import validate_pdb_file, validate_sequence, validate_parameters
from .utils import create_output_dir, generate_timestamp, format_energy

__version__ = "1.0.0"
__all__ = [
    "load_pdb", "save_pdb", "load_sequence", "save_sequence",
    "validate_pdb_file", "validate_sequence", "validate_parameters",
    "create_output_dir", "generate_timestamp", "format_energy"
]