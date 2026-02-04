"""
I/O utilities for cyclic peptide scripts.

Simplified file loading and saving functions extracted from repo code.
"""

import os
from pathlib import Path
from typing import Union, List, Optional, Dict, Any

def load_pdb(file_path: Union[str, Path]) -> str:
    """
    Load PDB file content.

    Args:
        file_path: Path to PDB file

    Returns:
        PDB file content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid PDB
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDB file not found: {file_path}")

    if file_path.suffix.lower() != '.pdb':
        raise ValueError(f"File must have .pdb extension: {file_path}")

    with open(file_path, 'r') as f:
        content = f.read()

    # Basic validation - check for PDB format
    if not any(line.startswith(('ATOM', 'HETATM')) for line in content.splitlines()):
        raise ValueError(f"File does not appear to contain PDB structure data: {file_path}")

    return content

def save_pdb(content: str, file_path: Union[str, Path]) -> Path:
    """
    Save PDB content to file.

    Args:
        content: PDB content string
        file_path: Output file path

    Returns:
        Path to saved file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(content)

    return file_path

def load_sequence(file_path: Union[str, Path]) -> str:
    """
    Load amino acid sequence from file.

    Args:
        file_path: Path to sequence file

    Returns:
        Cleaned amino acid sequence string
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Sequence file not found: {file_path}")

    with open(file_path, 'r') as f:
        content = f.read().strip()

    # Remove whitespace and convert to uppercase
    sequence = ''.join(content.split()).upper()

    return sequence

def save_sequence(sequence: str, file_path: Union[str, Path]) -> Path:
    """
    Save amino acid sequence to file.

    Args:
        sequence: Amino acid sequence
        file_path: Output file path

    Returns:
        Path to saved file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(sequence.strip() + '\n')

    return file_path

def save_results(results: Dict[str, Any], output_dir: Union[str, Path], prefix: str = "results") -> Dict[str, Path]:
    """
    Save computation results to files.

    Args:
        results: Dictionary containing results
        output_dir: Output directory
        prefix: File prefix

    Returns:
        Dictionary mapping result types to file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = {}

    # Save structures if present
    if 'structures' in results:
        for i, structure in enumerate(results['structures']):
            if isinstance(structure, str):
                # Assume it's a path - copy or create link
                struct_file = output_dir / f"{prefix}_structure_{i+1:03d}.pdb"
                try:
                    import shutil
                    shutil.copy2(structure, struct_file)
                    saved_files[f'structure_{i+1}'] = struct_file
                except:
                    pass

    # Save energy data if present
    if 'energies' in results:
        energy_file = output_dir / f"{prefix}_energies.txt"
        with open(energy_file, 'w') as f:
            f.write("# Energy Results\n")
            f.write("Structure\tEnergy\tRMSD\tDistance\n")
            for i, energy_data in enumerate(results['energies']):
                if isinstance(energy_data, dict):
                    energy = energy_data.get('energy', 0.0)
                    rmsd = energy_data.get('rmsd', 0.0)
                    distance = energy_data.get('distance', 0.0)
                    f.write(f"structure_{i+1:03d}\t{energy:.2f}\t{rmsd:.2f}\t{distance:.2f}\n")
        saved_files['energies'] = energy_file

    # Save trajectory if present
    if 'trajectory' in results:
        traj_file = output_dir / f"{prefix}_trajectory.log"
        with open(traj_file, 'w') as f:
            f.write("# Trajectory Data\n")
            f.write("Cycle\tScore\tRMSD\tTemperature\n")
            for entry in results['trajectory']:
                if isinstance(entry, dict):
                    cycle = entry.get('cycle', 0)
                    score = entry.get('score', 0.0)
                    rmsd = entry.get('rmsd', 0.0)
                    temp = entry.get('temperature', 1.0)
                    f.write(f"{cycle}\t{score:.2f}\t{rmsd:.2f}\t{temp:.2f}\n")
        saved_files['trajectory'] = traj_file

    return saved_files

def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    import json

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config

def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> Path:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Output file path

    Returns:
        Path to saved config file
    """
    import json

    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return config_path

def create_summary_report(results: Dict[str, Any], output_path: Union[str, Path]) -> Path:
    """
    Create a summary report of computation results.

    Args:
        results: Results dictionary
        output_path: Path to save report

    Returns:
        Path to saved report
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# Computation Summary Report\n")
        f.write("=" * 40 + "\n\n")

        # Basic metadata
        if 'metadata' in results:
            metadata = results['metadata']
            f.write("## Input Information\n")
            if 'input_file' in metadata:
                f.write(f"Input file: {metadata['input_file']}\n")
            if 'sequence' in metadata:
                f.write(f"Sequence: {metadata['sequence']}\n")
            if 'loop_region' in metadata:
                f.write(f"Loop region: {metadata['loop_region']}\n")
            f.write(f"\n")

        # Results summary
        f.write("## Results Summary\n")
        main_result = results.get('result', {})

        if 'structures' in main_result:
            f.write(f"Generated structures: {len(main_result['structures'])}\n")

        if 'final_score' in main_result:
            f.write(f"Final score: {main_result['final_score']:.2f}\n")

        if 'final_rmsd' in main_result:
            f.write(f"Final RMSD: {main_result['final_rmsd']:.2f}\n")

        if 'total_cycles' in main_result:
            f.write(f"Total cycles: {main_result['total_cycles']}\n")

        # Output files
        f.write("\n## Generated Files\n")
        if 'output_file' in results:
            f.write(f"Output directory: {results['output_file']}\n")

        if isinstance(main_result, dict):
            for key, value in main_result.items():
                if key.endswith('_file') and isinstance(value, str):
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")

    return output_path