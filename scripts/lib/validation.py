"""
Validation utilities for cyclic peptide scripts.

Input validation functions to ensure data integrity and proper parameters.
"""

import os
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, Any, List

# Valid amino acid single letter codes
VALID_AMINO_ACIDS = set('ACDEFGHIKLMNPQRSTVWY')

def validate_pdb_file(file_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Validate PDB file exists and has basic structure.

    Args:
        file_path: Path to PDB file

    Returns:
        (is_valid, message) tuple
    """
    try:
        file_path = Path(file_path)

        # Check existence
        if not file_path.exists():
            return False, f"PDB file not found: {file_path}"

        # Check extension
        if file_path.suffix.lower() not in ['.pdb', '.ent']:
            return False, f"File must have .pdb or .ent extension: {file_path}"

        # Check file is not empty
        if file_path.stat().st_size == 0:
            return False, f"PDB file is empty: {file_path}"

        # Basic content validation
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Check for PDB record types
        has_atoms = any(line.startswith(('ATOM', 'HETATM')) for line in lines)
        if not has_atoms:
            return False, f"PDB file contains no ATOM or HETATM records: {file_path}"

        return True, "Valid PDB file"

    except Exception as e:
        return False, f"Error validating PDB file: {e}"

def validate_sequence(sequence: str, min_length: int = 1, max_length: int = 50) -> Tuple[bool, str]:
    """
    Validate amino acid sequence.

    Args:
        sequence: Amino acid sequence string
        min_length: Minimum sequence length
        max_length: Maximum sequence length

    Returns:
        (is_valid, message) tuple
    """
    try:
        if not sequence:
            return False, "Sequence cannot be empty"

        # Clean sequence
        clean_seq = sequence.strip().upper()

        # Check length
        if len(clean_seq) < min_length:
            return False, f"Sequence too short: {len(clean_seq)} < {min_length}"

        if len(clean_seq) > max_length:
            return False, f"Sequence too long: {len(clean_seq)} > {max_length}"

        # Check valid amino acids
        invalid_chars = set(clean_seq) - VALID_AMINO_ACIDS
        if invalid_chars:
            return False, f"Invalid amino acid codes: {sorted(invalid_chars)}"

        return True, "Valid sequence"

    except Exception as e:
        return False, f"Error validating sequence: {e}"

def validate_loop_parameters(loop_start: int, loop_end: int, loop_cut: Optional[int] = None,
                           structure_size: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validate loop modeling parameters.

    Args:
        loop_start: Starting residue number
        loop_end: Ending residue number
        loop_cut: Cut point (optional)
        structure_size: Total structure size (optional)

    Returns:
        (is_valid, message) tuple
    """
    try:
        # Basic range checks
        if loop_start < 1:
            return False, "Loop start must be >= 1"

        if loop_end <= loop_start:
            return False, f"Loop end ({loop_end}) must be greater than loop start ({loop_start})"

        # Minimum loop length
        if loop_end - loop_start + 1 < 3:
            return False, f"Loop too short: {loop_end - loop_start + 1} residues (minimum 3)"

        # Structure size validation
        if structure_size:
            if loop_start > structure_size:
                return False, f"Loop start ({loop_start}) beyond structure size ({structure_size})"

            if loop_end > structure_size:
                return False, f"Loop end ({loop_end}) beyond structure size ({structure_size})"

        # Cut point validation
        if loop_cut:
            if loop_cut <= loop_start:
                return False, f"Loop cut ({loop_cut}) must be after loop start ({loop_start})"

            if loop_cut >= loop_end:
                return False, f"Loop cut ({loop_cut}) must be before loop end ({loop_end})"

        return True, "Valid loop parameters"

    except Exception as e:
        return False, f"Error validating loop parameters: {e}"

def validate_energy_range(energy: float, min_energy: float = -1000.0, max_energy: float = 1000.0) -> Tuple[bool, str]:
    """
    Validate energy values are in reasonable range.

    Args:
        energy: Energy value
        min_energy: Minimum acceptable energy
        max_energy: Maximum acceptable energy

    Returns:
        (is_valid, message) tuple
    """
    try:
        if not isinstance(energy, (int, float)):
            return False, f"Energy must be numeric, got {type(energy)}"

        if energy < min_energy:
            return False, f"Energy too low: {energy} < {min_energy}"

        if energy > max_energy:
            return False, f"Energy too high: {energy} > {max_energy}"

        return True, "Valid energy"

    except Exception as e:
        return False, f"Error validating energy: {e}"

def validate_config(config: Dict[str, Any], required_keys: List[str] = None) -> Tuple[bool, str]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys (optional)

    Returns:
        (is_valid, message) tuple
    """
    try:
        if not isinstance(config, dict):
            return False, f"Config must be a dictionary, got {type(config)}"

        # Check required keys
        if required_keys:
            missing_keys = set(required_keys) - set(config.keys())
            if missing_keys:
                return False, f"Missing required config keys: {sorted(missing_keys)}"

        # Validate specific config values
        if 'nstruct' in config:
            nstruct = config['nstruct']
            if not isinstance(nstruct, int) or nstruct < 1:
                return False, f"nstruct must be positive integer, got {nstruct}"

        if 'runtime' in config:
            runtime = config['runtime']
            if not isinstance(runtime, (int, float)) or runtime <= 0:
                return False, f"runtime must be positive number, got {runtime}"

        if 'outer_cycles' in config:
            cycles = config['outer_cycles']
            if not isinstance(cycles, int) or cycles < 1:
                return False, f"outer_cycles must be positive integer, got {cycles}"

        if 'inner_cycles' in config:
            cycles = config['inner_cycles']
            if not isinstance(cycles, int) or cycles < 1:
                return False, f"inner_cycles must be positive integer, got {cycles}"

        return True, "Valid configuration"

    except Exception as e:
        return False, f"Error validating config: {e}"

def validate_output_path(output_path: Union[str, Path], create_if_missing: bool = True) -> Tuple[bool, str]:
    """
    Validate output path is writable.

    Args:
        output_path: Output path
        create_if_missing: Whether to create directory if it doesn't exist

    Returns:
        (is_valid, message) tuple
    """
    try:
        output_path = Path(output_path)

        # Check if parent directory exists or can be created
        parent_dir = output_path.parent if output_path.suffix else output_path

        if not parent_dir.exists():
            if create_if_missing:
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    return False, f"Cannot create directory: {parent_dir} (permission denied)"
                except Exception as e:
                    return False, f"Cannot create directory: {parent_dir} ({e})"
            else:
                return False, f"Output directory does not exist: {parent_dir}"

        # Check write permissions
        if not os.access(parent_dir, os.W_OK):
            return False, f"No write permission for directory: {parent_dir}"

        return True, "Valid output path"

    except Exception as e:
        return False, f"Error validating output path: {e}"

def validate_parameters(params: Dict[str, Any]) -> Dict[str, Tuple[bool, str]]:
    """
    Validate multiple parameters at once.

    Args:
        params: Dictionary of parameters to validate

    Returns:
        Dictionary mapping parameter names to (is_valid, message) tuples
    """
    results = {}

    # Input file validation
    if 'input_file' in params:
        results['input_file'] = validate_pdb_file(params['input_file'])

    # Sequence validation
    if 'sequence' in params:
        min_len = params.get('min_sequence_length', 1)
        max_len = params.get('max_sequence_length', 50)
        results['sequence'] = validate_sequence(params['sequence'], min_len, max_len)

    # Loop parameters validation
    if all(key in params for key in ['loop_start', 'loop_end']):
        results['loop_params'] = validate_loop_parameters(
            params['loop_start'],
            params['loop_end'],
            params.get('loop_cut'),
            params.get('structure_size')
        )

    # Output path validation
    if 'output_path' in params:
        results['output_path'] = validate_output_path(params['output_path'])

    # Config validation
    if 'config' in params:
        required_keys = params.get('required_config_keys', [])
        results['config'] = validate_config(params['config'], required_keys)

    return results

def check_dependencies() -> Dict[str, Tuple[bool, str]]:
    """
    Check availability of optional dependencies.

    Returns:
        Dictionary mapping dependency names to (is_available, message) tuples
    """
    results = {}

    # PyRosetta
    try:
        import pyrosetta
        results['pyrosetta'] = (True, f"PyRosetta available (version info not accessible)")
    except ImportError:
        results['pyrosetta'] = (False, "PyRosetta not installed")

    # Rosetta
    try:
        import subprocess
        result = subprocess.run(['which', 'simple_cycpep_predict'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            results['rosetta'] = (True, f"Rosetta executable found: {result.stdout.strip()}")
        else:
            results['rosetta'] = (False, "Rosetta executable not in PATH")
    except:
        results['rosetta'] = (False, "Cannot check for Rosetta executable")

    # MPI
    try:
        import subprocess
        result = subprocess.run(['which', 'mpirun'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            results['mpi'] = (True, "MPI available")
        else:
            results['mpi'] = (False, "MPI not available")
    except:
        results['mpi'] = (False, "Cannot check for MPI")

    return results