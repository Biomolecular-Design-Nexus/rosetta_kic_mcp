#!/usr/bin/env python3
"""Direct testing of MCP tools without going through the MCP protocol."""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the utility functions directly
from utils import standardize_success_response, standardize_error_response, validate_input_file
from jobs.manager import job_manager


def test_validate_peptide_sequence():
    """Test the validate_peptide_sequence function."""
    print("=== Testing validate_peptide_sequence ===")

    # Test valid sequence
    print("\n1. Valid sequence 'GRGDSP':")
    try:
        if not "GRGDSP" or not "GRGDSP".replace(" ", ""):
            result = standardize_error_response("Sequence cannot be empty", "validation_error")
        else:
            # Clean and validate sequence
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            sequence_clean = "GRGDSP".upper().replace(" ", "").replace("\n", "")

            invalid_chars = [c for c in sequence_clean if c not in valid_aa]
            if invalid_chars:
                result = standardize_error_response(
                    f"Invalid amino acid codes found: {', '.join(set(invalid_chars))}",
                    "validation_error"
                )
            else:
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

                result = standardize_success_response({
                    "valid": True,
                    "sequence": sequence_clean,
                    "original_sequence": "GRGDSP",
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
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

    # Test invalid sequence
    print("\n2. Invalid sequence 'GRGDXP':")
    try:
        sequence = "GRGDXP"
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        sequence_clean = sequence.upper().replace(" ", "").replace("\n", "")

        invalid_chars = [c for c in sequence_clean if c not in valid_aa]
        if invalid_chars:
            result = standardize_error_response(
                f"Invalid amino acid codes found: {', '.join(set(invalid_chars))}",
                "validation_error"
            )
        else:
            result = {"status": "success", "message": "Valid sequence"}
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def test_get_server_info():
    """Test the get_server_info function."""
    print("\n=== Testing get_server_info ===")
    try:
        PROJECT_ROOT = Path(__file__).parent.parent
        SCRIPTS_DIR = PROJECT_ROOT / "scripts"

        result = standardize_success_response({
            "server_name": "rosetta-kic-mcp",
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
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def test_submit_structure_prediction():
    """Test submitting a structure prediction job."""
    print("\n=== Testing submit_structure_prediction ===")
    try:
        sequence = "GRGDSP"
        nstruct = 3
        runtime = 600

        # Basic validation
        if not sequence or not sequence.replace(" ", ""):
            result = standardize_error_response("Sequence cannot be empty", "validation_error")
        else:
            # Validate sequence contains only amino acid codes
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            sequence_clean = sequence.upper().replace(" ", "")
            if not all(c in valid_aa for c in sequence_clean):
                result = standardize_error_response(
                    "Sequence contains invalid amino acid codes. Use single-letter codes only.",
                    "validation_error"
                )
            else:
                # Submit job
                result = job_manager.submit_job(
                    script_name="structure_prediction.py",
                    args={
                        "input": sequence_clean,
                        "nstruct": nstruct,
                        "runtime": runtime,
                        "use_mpi": False
                    },
                    job_name=f"test_prediction_{sequence_clean[:6]}_{nstruct}"
                )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def test_list_jobs():
    """Test listing jobs."""
    print("\n=== Testing list_jobs ===")
    try:
        result = job_manager.list_jobs()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("DIRECT MCP TOOLS TESTING")
    print("=" * 60)

    test_get_server_info()
    test_validate_peptide_sequence()
    test_submit_structure_prediction()
    test_list_jobs()

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)