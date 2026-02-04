#!/usr/bin/env python3
"""
Script: structure_prediction.py
Description: Predict cyclic peptide structures using Rosetta simple_cycpep_predict

Original Use Case: examples/use_case_2_cyclic_peptide_structure_prediction.py
Dependencies Removed: Complex subprocess handling simplified, executable finding logic inlined

Usage:
    python scripts/structure_prediction.py --input <sequence> --output <output_file>

Example:
    python scripts/structure_prediction.py --input "GRGDSP" --output results/prediction.out
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import os
import sys
import time
import subprocess
import random
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "nstruct": 10,  # Reduced for practical use
    "runtime": 900,  # seconds
    "use_mpi": False,
    "num_processors": 1,
    "scoring": {
        "ex1": True,
        "ex2": True,
        "rama_cutoff": 3.0,
        "min_genkic_hbonds": 2,
        "min_final_hbonds": 2,
    },
    "sampling": {
        "closure_attempts": 250,
        "min_solution_count": 1,
        "cis_pro_frequency": 0.3,
        "output_fraction": 0.001,
    },
    "mpi_settings": {
        "lambda": 1.25,
        "kbt": 0.62,
        "batchsize_by_level": 1,
        "auto_2level_distribution": True,
    }
}

# Common Rosetta executable locations
ROSETTA_SEARCH_PATHS = [
    "./rosetta/source/bin/",
    "../rosetta/source/bin/",
    "~/rosetta/source/bin/",
    "/usr/local/rosetta/source/bin/",
    "/opt/rosetta/source/bin/",
]

ROSETTA_EXTENSIONS = [
    ".default.linuxgccrelease",
    ".mpi.linuxgccrelease",
    ".static.linuxgccrelease",
    ".linuxgccrelease",
    ""  # No extension
]

# ==============================================================================
# Inlined Utility Functions (simplified from repo)
# ==============================================================================
def validate_sequence(sequence: str) -> bool:
    """Validate amino acid sequence using single letter codes."""
    valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
    return all(aa in valid_aa for aa in sequence.upper())

def find_rosetta_executable(executable_name: str = 'simple_cycpep_predict') -> Optional[str]:
    """Find Rosetta executable in common locations."""
    # Check if executable is in PATH first
    try:
        result = subprocess.run(['which', executable_name],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    # Check common paths with different extensions
    for path in ROSETTA_SEARCH_PATHS:
        for ext in ROSETTA_EXTENSIONS:
            full_path = os.path.expanduser(path + executable_name + ext)
            if os.path.isfile(full_path):
                return full_path

    return None

def create_sequence_file(sequence: str, output_path: Union[str, Path]) -> Path:
    """Create sequence file for Rosetta input."""
    output_path = Path(output_path)
    with open(output_path, 'w') as f:
        f.write(f"{sequence}\n")
    return output_path

def generate_demo_prediction(sequence: str, output_dir: str, nstruct: int) -> Dict[str, Any]:
    """Generate demonstration output when Rosetta is not available."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating demo prediction for sequence: {sequence}")

    # Create sequence file for demo
    sequence_file = output_dir / 'sequence.txt'
    create_sequence_file(sequence, sequence_file)

    # Create mock silent file (Rosetta format)
    silent_file = output_dir / 'cycpep_structures.out'
    structures = []

    with open(silent_file, 'w') as f:
        f.write("SEQUENCE: " + sequence + "\n")
        f.write("SCORE: score  fa_atr  fa_rep  fa_sol  fa_intra_rep  fa_intra_sol_xover4  lk_ball_wtd  fa_elec  pro_close  hbond_sr_bb  hbond_lr_bb  hbond_bb_sc  hbond_sc  dslf_fa13  omega  fa_dun  p_aa_pp  yhh_planarity  ref  rama_prepro  description\n")

        for i in range(min(nstruct, 10)):  # Limit demo output
            # Generate realistic mock scores for cyclic peptides
            total_score = round(random.uniform(-50.0, -20.0), 2)
            fa_atr = round(random.uniform(-45.0, -25.0), 2)  # Attractive
            fa_rep = round(random.uniform(2.0, 8.0), 2)      # Repulsive (positive)
            fa_sol = round(random.uniform(8.0, 15.0), 2)     # Solvation
            fa_elec = round(random.uniform(-5.0, 2.0), 2)    # Electrostatic

            structure_name = f"{sequence}_demo_{i+1:04d}"
            structures.append(structure_name)

            f.write(f"SCORE: {total_score:8.2f} {fa_atr:8.2f} {fa_rep:7.2f} {fa_sol:7.2f}   0.00   0.00   0.00 {fa_elec:7.2f}   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00 {structure_name}\n")

            # Simulate processing time
            if i % 5 == 0:
                print(f"  Generated {i+1} structures...")
                time.sleep(0.2)

    # Create energy analysis summary
    energy_file = output_dir / 'energy_analysis.txt'
    with open(energy_file, 'w') as f:
        f.write(f"# Cyclic Peptide Structure Prediction Results\n")
        f.write(f"# Sequence: {sequence} (Length: {len(sequence)})\n")
        f.write(f"# Generated structures: {min(nstruct, 10)}\n")
        f.write(f"# Demo mode - for actual predictions, install Rosetta\n")
        f.write(f"#\n")
        f.write(f"Structure\tTotal_Score\tFa_Atr\tFa_Rep\tFa_Sol\n")

        for i, structure in enumerate(structures):
            total_score = round(random.uniform(-50.0, -20.0), 2)
            fa_atr = round(random.uniform(-45.0, -25.0), 2)
            fa_rep = round(random.uniform(2.0, 8.0), 2)
            fa_sol = round(random.uniform(8.0, 15.0), 2)
            f.write(f"{structure}\t{total_score}\t{fa_atr}\t{fa_rep}\t{fa_sol}\n")

    return {
        'structures': structures,
        'silent_file': str(silent_file),
        'sequence_file': str(sequence_file),
        'energy_file': str(energy_file),
        'output_directory': str(output_dir)
    }

def build_rosetta_command(config: Dict[str, Any], database_path: str,
                         sequence_file: str, output_dir: str) -> List[str]:
    """Build command line for simple_cycpep_predict."""
    cmd = ['-database', database_path]

    # Add boolean flags
    if config['scoring']['ex1']:
        cmd.append('-ex1')
    if config['scoring']['ex2']:
        cmd.append('-ex2')

    # Add numerical parameters
    cmd.extend(['-nstruct', str(config['nstruct'])])
    cmd.extend(['-cyclic_peptide:rama_cutoff', str(config['scoring']['rama_cutoff'])])
    cmd.extend(['-cyclic_peptide:genkic_closure_attempts', str(config['sampling']['closure_attempts'])])
    cmd.extend(['-cyclic_peptide:genkic_min_solution_count', str(config['sampling']['min_solution_count'])])
    cmd.extend(['-cyclic_peptide:sample_cis_pro_frequency', str(config['sampling']['cis_pro_frequency'])])

    # Add file paths
    cmd.extend(['-cyclic_peptide:sequence_file', sequence_file])
    cmd.extend(['-out:file:silent', os.path.join(output_dir, 'out.silent')])
    cmd.extend(['-cyclic_peptide:MPI_stop_after_time', str(config['runtime'])])

    # Add boolean flags for various options
    cmd.append('-cyclic_peptide:use_rama_filter')
    cmd.append('-score_symmetric_gly_tables')
    cmd.append('-mute all')
    cmd.append('-no_color')

    return cmd

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_structure_prediction(
    input_sequence: str,
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for cyclic peptide structure prediction.

    Args:
        input_sequence: Amino acid sequence (single letter codes)
        output_file: Path to save output directory (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - result: Main computation result
            - output_file: Path to output directory (if created)
            - metadata: Execution metadata

    Example:
        >>> result = run_structure_prediction("GRGDSP", "output_dir")
        >>> print(result['output_file'])
    """
    # Setup and validation
    sequence = input_sequence.upper().strip()
    config = {**DEFAULT_CONFIG, **(config or {})}

    # Update config with kwargs
    for key, value in kwargs.items():
        if key in config:
            config[key] = value
        elif key in config.get('scoring', {}):
            config['scoring'][key] = value
        elif key in config.get('sampling', {}):
            config['sampling'][key] = value

    if not validate_sequence(sequence):
        raise ValueError(f"Invalid amino acid sequence: {sequence}")

    if len(sequence) < 3:
        raise ValueError("Sequence must be at least 3 residues long")

    # Set up output directory
    if output_file is None:
        output_dir = Path(f'prediction_{sequence}')
    else:
        output_dir = Path(output_file)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Try to find Rosetta executable
    executable = find_rosetta_executable('simple_cycpep_predict')

    if not executable:
        print("Rosetta executable not found - generating demonstration output")
        result = generate_demo_prediction(sequence, str(output_dir), config['nstruct'])
    else:
        print(f"Found Rosetta executable: {executable}")
        # Would execute real Rosetta here
        result = execute_real_prediction(executable, sequence, str(output_dir), config)

    return {
        "result": result,
        "output_file": str(output_dir),
        "metadata": {
            "sequence": sequence,
            "config": config,
            "rosetta_available": executable is not None
        }
    }

def execute_real_prediction(executable: str, sequence: str, output_dir: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute real Rosetta prediction (when executable is available)."""
    print("Executing actual Rosetta prediction...")

    # Create sequence file
    sequence_file = Path(output_dir) / 'sequence.txt'
    create_sequence_file(sequence, sequence_file)

    # Find database path (simplified)
    database_path = Path(executable).parent.parent / 'database'
    if not database_path.exists():
        raise FileNotFoundError("Could not find Rosetta database")

    # Build command
    cmd_args = build_rosetta_command(config, str(database_path), str(sequence_file), output_dir)

    if config['use_mpi'] and config['num_processors'] > 1:
        cmd = ['mpirun', '-np', str(config['num_processors']), executable] + cmd_args
    else:
        cmd = [executable] + cmd_args

    print(f"Running: {' '.join(cmd)}")

    # Execute
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=config['runtime'] + 300  # Buffer time
        )

        # Save logs
        (Path(output_dir) / 'stdout.log').write_text(result.stdout)
        (Path(output_dir) / 'stderr.log').write_text(result.stderr)

        if result.returncode == 0:
            elapsed = time.time() - start_time
            print(f"Prediction completed successfully in {elapsed:.1f} seconds")

            silent_file = Path(output_dir) / 'out.silent'
            return {
                'silent_file': str(silent_file),
                'sequence_file': str(sequence_file),
                'output_directory': output_dir,
                'runtime': elapsed
            }
        else:
            raise RuntimeError(f"Rosetta failed with exit code {result.returncode}")

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Prediction timed out after {config['runtime']} seconds")

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True, help='Amino acid sequence (single letter codes)')
    parser.add_argument('--output', '-o', help='Output directory path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--nstruct', '-n', type=int, default=10, help='Number of structures to generate')
    parser.add_argument('--runtime', '-t', type=int, default=900, help='Maximum runtime in seconds')
    parser.add_argument('--use_mpi', action='store_true', help='Use MPI for parallel execution')
    parser.add_argument('--num_processors', type=int, default=1, help='Number of MPI processors')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        import json
        with open(args.config) as f:
            config = json.load(f)

    # Run prediction
    try:
        result = run_structure_prediction(
            input_sequence=args.input,
            output_file=args.output,
            config=config,
            nstruct=args.nstruct,
            runtime=args.runtime,
            use_mpi=args.use_mpi,
            num_processors=args.num_processors
        )

        print(f"Success: {result.get('output_file', 'Completed')}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())