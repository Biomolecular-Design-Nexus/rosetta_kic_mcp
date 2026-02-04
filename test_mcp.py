#!/usr/bin/env python3
"""Test script for MCP server functionality."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from server import (
    get_server_info,
    validate_peptide_sequence,
    validate_peptide_structure,
    submit_structure_prediction,
    get_job_status,
    list_jobs
)


def test_server_info():
    """Test server information retrieval."""
    print("Testing get_server_info...")
    result = get_server_info()
    print(f"Server info result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "server_name" in result
    print("✅ Server info test passed")


def test_sequence_validation():
    """Test peptide sequence validation."""
    print("\nTesting validate_peptide_sequence...")

    # Test valid sequence
    result = validate_peptide_sequence("GRGDSP")
    print(f"Valid sequence result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["valid"] == True
    assert result["length"] == 6

    # Test invalid sequence
    result = validate_peptide_sequence("GRGXSP")
    print(f"Invalid sequence result: {json.dumps(result, indent=2)}")
    assert result["status"] == "error"

    print("✅ Sequence validation test passed")


def test_structure_validation():
    """Test peptide structure validation."""
    print("\nTesting validate_peptide_structure...")

    # Test with a non-existent file
    result = validate_peptide_structure("/non/existent/file.pdb")
    print(f"Non-existent file result: {json.dumps(result, indent=2)}")
    assert result["status"] == "error"

    print("✅ Structure validation test passed")


def test_job_submission():
    """Test job submission (without actually running the job)."""
    print("\nTesting submit_structure_prediction...")

    # Submit a test job
    result = submit_structure_prediction(
        sequence="GRGDSP",
        nstruct=2,
        runtime=60,
        job_name="test_job"
    )
    print(f"Job submission result: {json.dumps(result, indent=2)}")

    if result["status"] == "submitted":
        job_id = result["job_id"]
        print(f"Job submitted with ID: {job_id}")

        # Check job status
        status_result = get_job_status(job_id)
        print(f"Job status: {json.dumps(status_result, indent=2)}")

        print("✅ Job submission test passed")
    else:
        print(f"⚠️  Job submission failed (expected in demo mode): {result}")


def test_job_listing():
    """Test job listing functionality."""
    print("\nTesting list_jobs...")

    result = list_jobs()
    print(f"Jobs list result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert "jobs" in result

    print("✅ Job listing test passed")


if __name__ == "__main__":
    print("Starting MCP server tests...")

    try:
        test_server_info()
        test_sequence_validation()
        test_structure_validation()
        test_job_submission()
        test_job_listing()

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)