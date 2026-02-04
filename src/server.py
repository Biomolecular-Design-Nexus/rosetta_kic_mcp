"""MCP Server for Cyclic Peptide Tools

Provides both synchronous and asynchronous (submit) APIs for Rosetta KIC-based
cyclic peptide computational tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys
import os

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Add paths to Python path
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

# Import components
from jobs.manager import job_manager
from utils import setup_logging, validate_input_file, standardize_error_response, standardize_success_response
from loguru import logger

# Setup logging
setup_logging("INFO")

# Create MCP server
mcp = FastMCP("cycpep-tools")

logger.info(f"MCP Server initialized")
logger.info(f"Project root: {PROJECT_ROOT}")
logger.info(f"Scripts directory: {SCRIPTS_DIR}")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted cyclic peptide computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    try:
        return job_manager.get_job_status(job_id)
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed cyclic peptide computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    try:
        return job_manager.get_job_result(job_id)
    except Exception as e:
        logger.error(f"Error getting job result for {job_id}: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    try:
        return job_manager.get_job_log(job_id, tail)
    except Exception as e:
        logger.error(f"Error getting job log for {job_id}: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running cyclic peptide computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    try:
        return job_manager.cancel_job(job_id)
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted cyclic peptide computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    try:
        return job_manager.list_jobs(status)
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def cleanup_old_jobs(max_age_days: int = 30) -> dict:
    """
    Clean up old completed jobs to free disk space.

    Args:
        max_age_days: Maximum age in days for completed jobs (default: 30)

    Returns:
        Summary of cleanup operation
    """
    try:
        return job_manager.cleanup_old_jobs(max_age_days)
    except Exception as e:
        logger.error(f"Error cleaning up jobs: {e}")
        return standardize_error_response(str(e))


# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_cyclic_peptide_closure(
    input_file: str,
    length: int = 6,
    nstruct: int = 5,
    residue_type: str = "GLY",
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a cyclic peptide closure job using GeneralizedKIC.

    Closes linear peptides into cyclic structures. This task typically takes
    10-30 minutes depending on complexity and number of structures requested.

    Args:
        input_file: Path to PDB file with linear peptide structure
        length: Maximum loop length for closure (default: 6)
        nstruct: Number of cyclic structures to generate (default: 5)
        residue_type: Residue type to add for closure (default: "GLY")
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    try:
        # Validate input file
        validation = validate_input_file(input_file)
        if not validation["valid"]:
            return standardize_error_response(validation["error"], "validation_error")

        # Submit job
        return job_manager.submit_job(
            script_name="cyclic_peptide_closure.py",
            args={
                "input": validation["path"],
                "length": length,
                "nstruct": nstruct,
                "residue_type": residue_type
            },
            job_name=job_name or f"closure_{length}_{nstruct}"
        )

    except Exception as e:
        logger.error(f"Error submitting cyclic peptide closure job: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def submit_structure_prediction(
    sequence: str,
    nstruct: int = 10,
    runtime: int = 900,
    use_mpi: bool = False,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a cyclic peptide structure prediction job using Rosetta.

    Predicts 3D structures from amino acid sequence using simple_cycpep_predict.
    This task typically takes 15-60 minutes depending on sequence length and
    number of structures requested.

    Args:
        sequence: Amino acid sequence (one-letter codes, e.g., "GRGDSP")
        nstruct: Number of structures to generate (default: 10)
        runtime: Maximum runtime in seconds (default: 900)
        use_mpi: Enable MPI parallel execution (default: False)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking
    """
    try:
        # Basic validation
        if not sequence or not sequence.replace(" ", ""):
            return standardize_error_response("Sequence cannot be empty", "validation_error")

        # Validate sequence contains only amino acid codes
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence_clean = sequence.upper().replace(" ", "")
        if not all(c in valid_aa for c in sequence_clean):
            return standardize_error_response(
                "Sequence contains invalid amino acid codes. Use single-letter codes only.",
                "validation_error"
            )

        # Submit job
        return job_manager.submit_job(
            script_name="structure_prediction.py",
            args={
                "input": sequence_clean,
                "nstruct": nstruct,
                "runtime": runtime,
                "use_mpi": use_mpi
            },
            job_name=job_name or f"prediction_{sequence_clean[:6]}_{nstruct}"
        )

    except Exception as e:
        logger.error(f"Error submitting structure prediction job: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def submit_loop_modeling(
    input_file: str,
    loop_start: int,
    loop_end: int,
    loop_cut: Optional[int] = None,
    outer_cycles: int = 10,
    inner_cycles: int = 30,
    fast_mode: bool = False,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a loop modeling job using Kinematic Closure (KIC).

    Models flexible peptide loops using Monte Carlo sampling with KIC.
    This task typically takes 20-90 minutes depending on loop length and
    sampling parameters.

    Args:
        input_file: Path to PDB file with protein/peptide structure
        loop_start: Starting residue number for loop region
        loop_end: Ending residue number for loop region
        loop_cut: Cut point for loop closure (optional, auto-selected if None)
        outer_cycles: Number of Monte Carlo outer cycles (default: 10)
        inner_cycles: Number of Monte Carlo inner cycles (default: 30)
        fast_mode: Use fast mode with reduced sampling (default: False)
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking
    """
    try:
        # Validate input file
        validation = validate_input_file(input_file)
        if not validation["valid"]:
            return standardize_error_response(validation["error"], "validation_error")

        # Validate loop parameters
        if loop_start >= loop_end:
            return standardize_error_response(
                "loop_start must be less than loop_end",
                "validation_error"
            )

        if loop_end - loop_start > 50:
            return standardize_error_response(
                "Loop length too long (>50 residues). Consider breaking into smaller segments.",
                "validation_error"
            )

        # Prepare arguments
        args = {
            "input": validation["path"],
            "loop_start": loop_start,
            "loop_end": loop_end,
            "outer_cycles": outer_cycles,
            "inner_cycles": inner_cycles
        }

        if loop_cut is not None:
            args["loop_cut"] = loop_cut

        if fast_mode:
            args["fast"] = True

        # Submit job
        return job_manager.submit_job(
            script_name="loop_modeling.py",
            args=args,
            job_name=job_name or f"loop_{loop_start}_{loop_end}"
        )

    except Exception as e:
        logger.error(f"Error submitting loop modeling job: {e}")
        return standardize_error_response(str(e))


# ==============================================================================
# Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_batch_cyclic_closure(
    input_files: List[str],
    length: int = 6,
    nstruct: int = 3,
    residue_type: str = "GLY",
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch cyclic peptide closure for multiple linear structures.

    Processes multiple linear peptides in a single job. Suitable for:
    - Processing many peptide candidates at once
    - Library processing workflows
    - High-throughput screening

    Args:
        input_files: List of paths to PDB files with linear peptides
        length: Maximum loop length for closure (default: 6)
        nstruct: Number of cyclic structures per input (default: 3)
        residue_type: Residue type to add for closure (default: "GLY")
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    try:
        if not input_files:
            return standardize_error_response("No input files provided", "validation_error")

        # Validate all input files
        validated_files = []
        for file_path in input_files:
            validation = validate_input_file(file_path)
            if not validation["valid"]:
                return standardize_error_response(
                    f"Invalid file {file_path}: {validation['error']}",
                    "validation_error"
                )
            validated_files.append(validation["path"])

        # Convert list to comma-separated string for CLI
        files_str = ",".join(validated_files)

        # Submit job
        return job_manager.submit_job(
            script_name="cyclic_peptide_closure.py",
            args={
                "input": files_str,
                "length": length,
                "nstruct": nstruct,
                "residue_type": residue_type,
                "batch": True
            },
            job_name=job_name or f"batch_closure_{len(input_files)}_files"
        )

    except Exception as e:
        logger.error(f"Error submitting batch closure job: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def submit_batch_structure_prediction(
    sequences: List[str],
    nstruct: int = 5,
    runtime: int = 600,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch structure prediction for multiple cyclic peptide sequences.

    Processes multiple sequences in a single job. Suitable for:
    - Virtual screening of peptide libraries
    - Comparative structure analysis
    - High-throughput design workflows

    Args:
        sequences: List of amino acid sequences (one-letter codes)
        nstruct: Number of structures per sequence (default: 5)
        runtime: Maximum runtime per sequence in seconds (default: 600)
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    try:
        if not sequences:
            return standardize_error_response("No sequences provided", "validation_error")

        # Validate all sequences
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        validated_sequences = []

        for i, seq in enumerate(sequences):
            if not seq or not seq.replace(" ", ""):
                return standardize_error_response(
                    f"Sequence {i+1} is empty", "validation_error"
                )

            seq_clean = seq.upper().replace(" ", "")
            if not all(c in valid_aa for c in seq_clean):
                return standardize_error_response(
                    f"Sequence {i+1} contains invalid amino acid codes: {seq}",
                    "validation_error"
                )

            validated_sequences.append(seq_clean)

        # Convert list to comma-separated string for CLI
        sequences_str = ",".join(validated_sequences)

        # Submit job
        return job_manager.submit_job(
            script_name="structure_prediction.py",
            args={
                "input": sequences_str,
                "nstruct": nstruct,
                "runtime": runtime,
                "batch": True
            },
            job_name=job_name or f"batch_prediction_{len(sequences)}_seqs"
        )

    except Exception as e:
        logger.error(f"Error submitting batch prediction job: {e}")
        return standardize_error_response(str(e))


# ==============================================================================
# Quick Synchronous Tools (for information/validation)
# ==============================================================================

@mcp.tool()
def validate_peptide_structure(input_file: str) -> dict:
    """
    Quickly validate a peptide structure file (synchronous operation).

    Performs basic validation checks on PDB files without running
    computational modeling. Returns immediately with validation results.

    Args:
        input_file: Path to PDB file to validate

    Returns:
        Dictionary with validation results and basic structure information
    """
    try:
        # Validate file exists and is readable
        validation = validate_input_file(input_file)
        if not validation["valid"]:
            return standardize_error_response(validation["error"], "validation_error")

        # Basic PDB validation
        pdb_path = Path(validation["path"])

        # Read and analyze PDB file
        with open(pdb_path, 'r') as f:
            lines = f.readlines()

        atom_lines = [line for line in lines if line.startswith("ATOM")]
        hetatm_lines = [line for line in lines if line.startswith("HETATM")]

        if not atom_lines:
            return standardize_error_response(
                "No ATOM records found in PDB file", "validation_error"
            )

        # Extract basic information
        residues = set()
        chains = set()
        for line in atom_lines:
            if len(line) >= 26:
                chain = line[21:22].strip()
                res_num = line[22:26].strip()
                res_name = line[17:20].strip()

                chains.add(chain)
                residues.add((chain, res_num, res_name))

        return standardize_success_response({
            "valid": True,
            "file_path": str(pdb_path),
            "file_size_bytes": validation["size_bytes"],
            "total_atoms": len(atom_lines),
            "hetatm_records": len(hetatm_lines),
            "num_residues": len(residues),
            "num_chains": len(chains),
            "chains": sorted(list(chains)),
            "structure_info": {
                "is_peptide": len(residues) <= 50,  # Heuristic for peptide vs protein
                "is_single_chain": len(chains) == 1,
                "total_residues": len(residues)
            }
        })

    except Exception as e:
        logger.error(f"Error validating peptide structure: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def validate_peptide_sequence(sequence: str) -> dict:
    """
    Quickly validate a peptide sequence (synchronous operation).

    Validates amino acid sequence format and provides basic information.
    Returns immediately with validation results.

    Args:
        sequence: Amino acid sequence (one-letter codes)

    Returns:
        Dictionary with validation results and sequence information
    """
    try:
        if not sequence or not sequence.replace(" ", ""):
            return standardize_error_response("Sequence cannot be empty", "validation_error")

        # Clean and validate sequence
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence_clean = sequence.upper().replace(" ", "").replace("\n", "")

        invalid_chars = [c for c in sequence_clean if c not in valid_aa]
        if invalid_chars:
            return standardize_error_response(
                f"Invalid amino acid codes found: {', '.join(set(invalid_chars))}",
                "validation_error"
            )

        # Basic sequence analysis
        aa_counts = {}
        for aa in sequence_clean:
            aa_counts[aa] = aa_counts.get(aa, 0) + 1

        # Calculate basic properties
        length = len(sequence_clean)

        # Simple heuristics for peptide properties
        hydrophobic_aa = set("AILMFWYV")
        hydrophilic_aa = set("NQST")
        charged_aa = set("DEKRH")

        hydrophobic_count = sum(aa_counts.get(aa, 0) for aa in hydrophobic_aa)
        hydrophilic_count = sum(aa_counts.get(aa, 0) for aa in hydrophilic_aa)
        charged_count = sum(aa_counts.get(aa, 0) for aa in charged_aa)

        return standardize_success_response({
            "valid": True,
            "sequence": sequence_clean,
            "original_sequence": sequence,
            "length": length,
            "amino_acid_composition": aa_counts,
            "properties": {
                "hydrophobic_residues": hydrophobic_count,
                "hydrophilic_residues": hydrophilic_count,
                "charged_residues": charged_count,
                "hydrophobic_fraction": hydrophobic_count / length,
                "is_short_peptide": length <= 20,
                "is_medium_peptide": 20 < length <= 50,
                "is_suitable_for_cyclization": 6 <= length <= 30
            }
        })

    except Exception as e:
        logger.error(f"Error validating peptide sequence: {e}")
        return standardize_error_response(str(e))


@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the MCP server and available tools.

    Returns:
        Dictionary with server information and capabilities
    """
    try:
        return standardize_success_response({
            "server_name": "cycpep-tools",
            "version": "1.0.0",
            "description": "MCP server for Rosetta KIC-based cyclic peptide computational tools",
            "project_root": str(PROJECT_ROOT),
            "scripts_directory": str(SCRIPTS_DIR),
            "job_storage": str(job_manager.store.jobs_dir),
            "available_tools": {
                "job_management": [
                    "get_job_status", "get_job_result", "get_job_log",
                    "cancel_job", "list_jobs", "cleanup_old_jobs"
                ],
                "submit_tools": [
                    "submit_cyclic_peptide_closure", "submit_structure_prediction",
                    "submit_loop_modeling", "submit_batch_cyclic_closure",
                    "submit_batch_structure_prediction"
                ],
                "sync_tools": [
                    "validate_peptide_structure", "validate_peptide_sequence",
                    "get_server_info"
                ]
            },
            "typical_runtimes": {
                "cyclic_peptide_closure": "10-30 minutes",
                "structure_prediction": "15-60 minutes",
                "loop_modeling": "20-90 minutes",
                "validation": "< 1 second"
            }
        })

    except Exception as e:
        logger.error(f"Error getting server info: {e}")
        return standardize_error_response(str(e))


# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    logger.info("Starting MCP server for cyclic peptide tools")
    mcp.run()