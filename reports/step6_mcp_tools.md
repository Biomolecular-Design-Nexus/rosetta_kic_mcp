# Step 6: MCP Tools Documentation

## Server Information
- **Server Name**: cycpep-tools
- **Version**: 1.0.0
- **Created Date**: 2025-12-31
- **Server Path**: `src/server.py`
- **Technology**: FastMCP 2.14.1

## Architecture Overview

The MCP server implements a dual-API architecture:

### API Types

1. **Synchronous API** - For fast operations (<10 seconds)
   - Direct function call, immediate response
   - Used for validation, quick analysis, server information

2. **Submit API** - For long-running tasks (>10 minutes)
   - Submit job → get job_id → check status → retrieve results
   - Used for computational modeling tasks
   - Background execution with persistence

### Project Structure

```
rosetta_kic_mcp/
├── src/
│   ├── server.py              # Main MCP server
│   ├── utils.py              # Shared utilities
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── manager.py        # Job execution management
│   │   └── store.py          # Job persistence
│   └── tools/
│       └── __init__.py
├── scripts/                  # Source computational scripts
│   ├── cyclic_peptide_closure.py
│   ├── structure_prediction.py
│   ├── loop_modeling.py
│   └── lib/                  # Shared library functions
├── jobs/                     # Job storage directory
└── reports/
    └── step6_mcp_tools.md   # This documentation
```

## Job Management Tools

| Tool | Description | API Type |
|------|-------------|----------|
| `get_job_status` | Check job progress and status | Sync |
| `get_job_result` | Get completed job results | Sync |
| `get_job_log` | View job execution logs | Sync |
| `cancel_job` | Cancel running job | Sync |
| `list_jobs` | List all jobs with filtering | Sync |
| `cleanup_old_jobs` | Clean up old completed jobs | Sync |

## Computational Tools

### Submit Tools (Long Operations > 10 min)

| Tool | Description | Source Script | Est. Runtime | Batch Support |
|------|-------------|---------------|--------------|---------------|
| `submit_cyclic_peptide_closure` | Close linear peptides into cycles | `cyclic_peptide_closure.py` | 10-30 min | Yes |
| `submit_structure_prediction` | Predict 3D structures from sequence | `structure_prediction.py` | 15-60 min | Yes |
| `submit_loop_modeling` | Model flexible loops with KIC | `loop_modeling.py` | 20-90 min | No |
| `submit_batch_cyclic_closure` | Batch peptide closure | `cyclic_peptide_closure.py` | varies | Yes |
| `submit_batch_structure_prediction` | Batch structure prediction | `structure_prediction.py` | varies | Yes |

### Sync Tools (Fast Operations < 10 sec)

| Tool | Description | Est. Runtime |
|------|-------------|--------------|
| `validate_peptide_structure` | Validate PDB file format | < 1 sec |
| `validate_peptide_sequence` | Validate amino acid sequence | < 1 sec |
| `get_server_info` | Get server capabilities | < 1 sec |

---

## Tool Reference

### Job Management

#### get_job_status
```python
get_job_status(job_id: str) -> dict
```
**Purpose**: Get the status of a submitted job
**Parameters**:
- `job_id`: Job identifier from submit_* function
**Returns**: Status info with timestamps, runtime, and error details

#### get_job_result
```python
get_job_result(job_id: str) -> dict
```
**Purpose**: Get results of a completed job
**Parameters**:
- `job_id`: Job identifier
**Returns**: Output files list, results data, and completion info

#### get_job_log
```python
get_job_log(job_id: str, tail: int = 50) -> dict
```
**Purpose**: View job execution logs
**Parameters**:
- `job_id`: Job identifier
- `tail`: Number of lines from end (0 = all)
**Returns**: Log lines and file information

#### cancel_job
```python
cancel_job(job_id: str) -> dict
```
**Purpose**: Cancel a running job
**Parameters**:
- `job_id`: Job identifier
**Returns**: Success/error message

#### list_jobs
```python
list_jobs(status: Optional[str] = None) -> dict
```
**Purpose**: List all jobs with optional filtering
**Parameters**:
- `status`: Filter by status (pending, running, completed, failed, cancelled)
**Returns**: List of jobs with metadata

#### cleanup_old_jobs
```python
cleanup_old_jobs(max_age_days: int = 30) -> dict
```
**Purpose**: Clean up old completed jobs
**Parameters**:
- `max_age_days`: Maximum age for completed jobs
**Returns**: Cleanup summary

### Computational Tools

#### submit_cyclic_peptide_closure
```python
submit_cyclic_peptide_closure(
    input_file: str,
    length: int = 6,
    nstruct: int = 5,
    residue_type: str = "GLY",
    job_name: Optional[str] = None
) -> dict
```
**Purpose**: Close linear peptides into cyclic structures using GeneralizedKIC
**Runtime**: 10-30 minutes
**Parameters**:
- `input_file`: Path to PDB file with linear peptide
- `length`: Maximum loop length for closure
- `nstruct`: Number of cyclic structures to generate
- `residue_type`: Residue type for closure (GLY, ALA, etc.)
- `job_name`: Optional job name for tracking
**Returns**: Job submission response with job_id

#### submit_structure_prediction
```python
submit_structure_prediction(
    sequence: str,
    nstruct: int = 10,
    runtime: int = 900,
    use_mpi: bool = False,
    job_name: Optional[str] = None
) -> dict
```
**Purpose**: Predict 3D structures from amino acid sequence using Rosetta
**Runtime**: 15-60 minutes
**Parameters**:
- `sequence`: Amino acid sequence (one-letter codes)
- `nstruct`: Number of structures to generate
- `runtime`: Maximum runtime per sequence (seconds)
- `use_mpi`: Enable MPI parallel execution
- `job_name`: Optional job name
**Returns**: Job submission response with job_id

#### submit_loop_modeling
```python
submit_loop_modeling(
    input_file: str,
    loop_start: int,
    loop_end: int,
    loop_cut: Optional[int] = None,
    outer_cycles: int = 10,
    inner_cycles: int = 30,
    fast_mode: bool = False,
    job_name: Optional[str] = None
) -> dict
```
**Purpose**: Model flexible loops using Kinematic Closure
**Runtime**: 20-90 minutes
**Parameters**:
- `input_file`: Path to PDB structure file
- `loop_start`: Starting residue number
- `loop_end`: Ending residue number
- `loop_cut`: Cut point for closure (optional)
- `outer_cycles`: Monte Carlo outer cycles
- `inner_cycles`: Monte Carlo inner cycles
- `fast_mode`: Use reduced sampling
- `job_name`: Optional job name
**Returns**: Job submission response with job_id

#### submit_batch_cyclic_closure
```python
submit_batch_cyclic_closure(
    input_files: List[str],
    length: int = 6,
    nstruct: int = 3,
    residue_type: str = "GLY",
    job_name: Optional[str] = None
) -> dict
```
**Purpose**: Batch cyclic peptide closure for multiple structures
**Runtime**: varies with number of inputs
**Parameters**:
- `input_files`: List of PDB file paths
- Other parameters same as single closure
**Returns**: Job submission response for batch job

#### submit_batch_structure_prediction
```python
submit_batch_structure_prediction(
    sequences: List[str],
    nstruct: int = 5,
    runtime: int = 600,
    job_name: Optional[str] = None
) -> dict
```
**Purpose**: Batch structure prediction for multiple sequences
**Runtime**: varies with number of sequences
**Parameters**:
- `sequences`: List of amino acid sequences
- Other parameters same as single prediction
**Returns**: Job submission response for batch job

#### validate_peptide_structure
```python
validate_peptide_structure(input_file: str) -> dict
```
**Purpose**: Validate PDB structure file format
**Runtime**: < 1 second
**Parameters**:
- `input_file`: Path to PDB file
**Returns**: Validation results with structure information

#### validate_peptide_sequence
```python
validate_peptide_sequence(sequence: str) -> dict
```
**Purpose**: Validate amino acid sequence format
**Runtime**: < 1 second
**Parameters**:
- `sequence`: Amino acid sequence string
**Returns**: Validation results with sequence analysis

#### get_server_info
```python
get_server_info() -> dict
```
**Purpose**: Get server information and capabilities
**Runtime**: < 1 second
**Returns**: Server metadata and tool listings

---

## Workflow Examples

### Quick Validation (Sync API)
```python
# Validate a peptide sequence
result = validate_peptide_sequence("GRGDSP")
# Returns immediately with validation results

# Validate a structure file
result = validate_peptide_structure("/path/to/structure.pdb")
# Returns immediately with structure analysis
```

### Structure Prediction (Submit API)
```python
# 1. Submit prediction job
submit_result = submit_structure_prediction(
    sequence="GRGDSP",
    nstruct=10,
    runtime=900,
    job_name="test_prediction"
)
# Returns: {"status": "submitted", "job_id": "abc123", ...}

# 2. Check job status
status = get_job_status("abc123")
# Returns: {"job_status": "running", "current_runtime_seconds": 120, ...}

# 3. View logs (optional)
logs = get_job_log("abc123", tail=20)
# Returns recent log lines

# 4. Get results when completed
result = get_job_result("abc123")
# Returns: {"output_files": [...], "outputs_directory": "/path/to/outputs", ...}
```

### Batch Processing (Submit API)
```python
# Submit batch job for multiple sequences
sequences = ["GRGDSP", "ACDEFG", "ILVFYW"]
batch_result = submit_batch_structure_prediction(
    sequences=sequences,
    nstruct=5,
    job_name="batch_screening"
)
# Returns: {"status": "submitted", "job_id": "batch456", ...}

# Monitor batch progress
status = get_job_status("batch456")
# Check logs for detailed progress
logs = get_job_log("batch456")
```

### Job Management
```python
# List all jobs
all_jobs = list_jobs()

# List only running jobs
running_jobs = list_jobs(status="running")

# Cancel a job
cancel_result = cancel_job("abc123")

# Clean up old jobs
cleanup_result = cleanup_old_jobs(max_age_days=7)
```

---

## Job Lifecycle

### Job States
1. **pending**: Job submitted, waiting to start
2. **running**: Job executing in background
3. **completed**: Job finished successfully
4. **failed**: Job failed with error
5. **cancelled**: Job cancelled by user

### Job Data Structure
Each job creates a directory: `jobs/{job_id}/`
- `metadata.json`: Job metadata and status
- `job.log`: Execution logs
- `outputs/`: Output files from the computation

### Job Persistence
- Jobs survive server restarts
- Metadata tracked in JSON files
- Output files preserved until cleanup
- Automatic cleanup of old completed jobs

---

## Error Handling

### Validation Errors
- Invalid file paths
- Malformed sequences
- Invalid parameter ranges
- Missing dependencies

### Runtime Errors
- Script execution failures
- Memory/resource limitations
- Timeout errors
- PyRosetta/Rosetta unavailable

### Error Response Format
```json
{
  "status": "error",
  "error": "Description of the error",
  "error_type": "validation_error|runtime_error|system_error"
}
```

---

## Server Configuration

### Environment Requirements
- Python 3.8+
- FastMCP 2.14.1+
- Loguru for logging
- Optional: PyRosetta, Rosetta

### Starting the Server
```bash
# Development mode with inspector
mamba run -p ./env fastmcp dev src/server.py

# Production mode
mamba run -p ./env python src/server.py
```

### Environment Variables
- `PYTHONPATH`: Includes scripts directory
- Logging level configurable in utils.py

---

## Scientific Applications

### Use Cases

1. **Cyclic Peptide Design**
   - Close linear designs into cycles
   - Predict 3D structures
   - Optimize loop conformations

2. **Virtual Screening**
   - Batch process peptide libraries
   - Compare structural predictions
   - Filter by geometric constraints

3. **Loop Engineering**
   - Model flexible regions
   - Optimize binding loops
   - Study conformational dynamics

### Output Files

#### Cyclic Peptide Closure
- PDB files with closed structures
- Energy analysis summaries
- RMSD and distance metrics

#### Structure Prediction
- Rosetta silent files
- Energy component analysis
- Sequence-structure mappings

#### Loop Modeling
- Remodeled PDB structures
- Monte Carlo trajectories
- Conformational analysis

---

## Performance Characteristics

### Runtime Estimates

| Operation | Typical Runtime | Factors |
|-----------|----------------|---------|
| Validation | < 1 sec | File size only |
| Peptide Closure | 10-30 min | Length, nstruct, complexity |
| Structure Prediction | 15-60 min | Sequence length, nstruct, runtime limit |
| Loop Modeling | 20-90 min | Loop length, sampling cycles |
| Batch Processing | scales linearly | Number of inputs × single runtime |

### Resource Requirements

| Operation | Memory | Disk Space | CPU Usage |
|-----------|--------|------------|-----------|
| Small peptide (6-8 AA) | < 100 MB | < 10 MB | 1 core |
| Medium peptide (10-15 AA) | 200-500 MB | 50-100 MB | 1 core |
| Large peptide (>15 AA) | > 500 MB | > 100 MB | 1 core |
| Batch jobs | scales per item | scales per item | 1 core per job |

### Scalability Notes
- Jobs run sequentially (one at a time)
- For high throughput, consider multiple server instances
- Disk space grows with completed jobs (use cleanup)
- Memory usage is per-job, not cumulative

---

## Integration Examples

### LLM Agent Integration
```python
# The MCP server is designed for LLM agents to:

# 1. Validate inputs before expensive computations
result = validate_peptide_sequence("GRGDSP")
if result["status"] == "success":
    # Proceed with computation
    job = submit_structure_prediction(sequence="GRGDSP")

# 2. Monitor long-running tasks
job_id = "abc123"
while True:
    status = get_job_status(job_id)
    if status["job_status"] == "completed":
        results = get_job_result(job_id)
        break
    elif status["job_status"] == "failed":
        print("Job failed:", status.get("error"))
        break
    # Wait and check again

# 3. Process results for downstream analysis
output_files = results["output_files"]
for file_info in output_files:
    print(f"Generated: {file_info['name']} ({file_info['size_bytes']} bytes)")
```

### Workflow Orchestration
The server supports complex workflows:
1. Validate → Submit → Monitor → Results
2. Batch processing with progress tracking
3. Error handling and recovery
4. Resource cleanup and management

---

## Troubleshooting

### Common Issues

#### Server Won't Start
- Check Python environment activation
- Verify FastMCP installation
- Check log output for specific errors

#### Job Fails Immediately
- Verify input file paths exist and are readable
- Check sequence format for invalid characters
- Review parameter ranges (e.g., loop_start < loop_end)

#### Job Hangs
- Check available disk space
- Monitor system resources
- Use `get_job_log()` for debugging
- Consider cancelling and resubmitting with different parameters

#### Missing Results
- Ensure job completed successfully
- Check job log for script errors
- Verify output directory permissions

### Debug Tools
- `get_job_log()`: View execution logs
- `get_job_status()`: Check runtime information
- `validate_*()` functions: Pre-validate inputs
- Server logs: Check console output

---

## Future Enhancements

### Planned Features
- Parallel job execution
- GPU acceleration support
- Advanced progress reporting
- Job priority queuing
- Result visualization tools

### Extensibility
- New computational tools can be added by:
  1. Adding script to `scripts/` directory
  2. Creating submit_* tool in server.py
  3. Following the established patterns
- Job management system supports any computational script
- Validation framework extensible for new input types

---

## Success Criteria ✅

- [x] MCP server created at `src/server.py`
- [x] Job manager implemented for async operations
- [x] Submit tools created for long-running operations (>10 min)
- [x] Sync tools created for fast operations (<10 sec)
- [x] Batch processing support for applicable tools
- [x] Job management tools working (status, result, log, cancel, list)
- [x] All tools have clear descriptions for LLM use
- [x] Error handling returns structured responses
- [x] Server starts without errors
- [x] Comprehensive documentation with examples
- [x] Scientific validation of approach and outputs

The MCP server is now fully functional and ready for use with LLM agents for cyclic peptide computational workflows.