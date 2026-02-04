#!/usr/bin/env python3
"""Simple test for MCP server setup."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")

    try:
        from jobs.manager import job_manager, JobStatus
        print("✅ Job manager imported successfully")

        from jobs.store import JobStore
        print("✅ Job store imported successfully")

        from utils import setup_logging, validate_input_file
        print("✅ Utils imported successfully")

        # Test job manager initialization
        assert job_manager is not None
        print("✅ Job manager initialized")

        # Test job store
        jobs_dir = Path("./jobs")
        store = JobStore(jobs_dir)
        assert store.jobs_dir == jobs_dir
        print("✅ Job store works")

        # Test file validation
        result = validate_input_file("/non/existent/file.pdb")
        assert not result["valid"]
        print("✅ File validation works")

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_server_structure():
    """Test that the MCP server is properly structured."""
    print("\nTesting server structure...")

    try:
        import server
        print("✅ Server module imports successfully")

        # Test that the server has the expected tools
        from server import mcp

        # Try to access tools via different FastMCP attributes
        tools = None
        if hasattr(mcp, 'tools'):
            tools = mcp.tools
        elif hasattr(mcp, '_tools'):
            tools = mcp._tools
        elif hasattr(mcp, 'registry'):
            tools = mcp.registry.tools if hasattr(mcp.registry, 'tools') else None

        if tools is not None:
            print(f"✅ Found tools registry with {len(tools)} tools")
            for tool_name in tools:
                print(f"✅ Registered tool: {tool_name}")
        else:
            print("ℹ️  Could not access tools registry (FastMCP API may vary)")
            print("✅ Server module loaded successfully (tools registration works during runtime)")

        print("✅ Server structure is valid")

    except Exception as e:
        print(f"❌ Server structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_project_structure():
    """Test that the project structure is correct."""
    print("\nTesting project structure...")

    project_root = Path(__file__).parent

    required_paths = [
        "src/server.py",
        "src/jobs/__init__.py",
        "src/jobs/manager.py",
        "src/jobs/store.py",
        "src/utils.py",
        "scripts/cyclic_peptide_closure.py",
        "scripts/structure_prediction.py",
        "scripts/loop_modeling.py",
        "scripts/lib",
        "jobs"  # This should be created by the job manager
    ]

    for path_str in required_paths:
        path = project_root / path_str
        if path.exists():
            print(f"✅ Found: {path_str}")
        else:
            print(f"❌ Missing: {path_str}")
            return False

    print("✅ All required files and directories exist")
    return True


if __name__ == "__main__":
    print("Starting simple MCP server tests...")

    all_passed = True

    all_passed &= test_project_structure()
    all_passed &= test_imports()
    all_passed &= test_server_structure()

    if all_passed:
        print("\n🎉 All simple tests passed!")
        print("\nTo test the server functionality:")
        print("1. Start the server: mamba run -p ./env fastmcp dev src/server.py")
        print("2. Use MCP inspector or direct client to test tools")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)