# Rosetta KIC MCP

> MCP tools for cyclic peptide computational analysis using Rosetta KIC and GeneralizedKIC protocols

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

This MCP provides computational tools for cyclic peptide modeling using Rosetta's Kinematic Closure (KIC) and GeneralizedKIC protocols. It enables 3D structure prediction, peptide cyclization, loop modeling, and conformational analysis for cyclic peptides through both standalone scripts and an MCP server interface.

### Features
- **Cyclic peptide closure** using GeneralizedKIC algorithm
- **3D structure prediction** from amino acid sequences
- **Flexible loop modeling** with Monte Carlo sampling
- **Batch processing** for virtual screening workflows
- **Structure validation** and quality assessment
- **Job management** for long-running computations

## Installation

### Quick Setup

Run the automated setup script:

```bash
./quick_setup.sh
```

This will create the environment and install all dependencies automatically.

### Manual Setup (Advanced)

For manual installation or customization, follow these steps.

#### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- RDKit (installed automatically)
- Optional: PyRosetta for full Rosetta functionality

#### Create Environment

Based on the environment setup from `reports/step3_environment.md`:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/rosetta_kic_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.12 pip numpy pandas -y
# or: conda create -p ./env python=3.12 pip numpy pandas -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install core scientific packages
mamba install -p ./env -c conda-forge rdkit -y
mamba install -p ./env -c conda-forge biopython -y

# Install Python utilities
mamba run -p ./env pip install loguru click tqdm

# Install MCP framework
mamba run -p ./env pip install fastmcp

# Install PyRosetta
pip install pyrosetta --find-links https://west.rosettacommons.org/pyrosetta/quarterly/release
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/cyclic_peptide_closure.py` | Close linear peptides into cyclic structures using GeneralizedKIC | See below |
| `scripts/structure_prediction.py` | Predict 3D structures from amino acid sequences | See below |
| `scripts/loop_modeling.py` | Model flexible loops using Kinematic Closure | See below |

### Script Examples

#### Cyclic Peptide Closure

```bash
# Activate environment
mamba activate ./env

# Run peptide closure
mamba run -p ./env python scripts/cyclic_peptide_closure.py \
  --input examples/data/structures/linear_peptide_sample.pdb \
  --length 6 \
  --nstruct 5 \
  --output results/closed_peptides
```

**Parameters:**
- `--input, -i`: Input PDB file with linear peptide (required)
- `--length, -l`: Maximum loop length for closure (default: 6)
- `--nstruct, -n`: Number of cyclic structures to generate (default: 5)
- `--resn, -r`: Residue type for extension (default: GLY)
- `--output, -o`: Output directory (default: results/)

#### Structure Prediction

```bash
mamba run -p ./env python scripts/structure_prediction.py \
  --sequence "GRGDSP" \
  --output_dir results/structures \
  --nstruct 10 \
  --runtime 900
```

**Parameters:**
- `--sequence, -s`: Amino acid sequence (one-letter codes, required)
- `--output_dir, -o`: Output directory (default: results/)
- `--nstruct`: Number of structures to generate (default: 10)
- `--runtime`: Maximum runtime in seconds (default: 900)

#### Loop Modeling

```bash
mamba run -p ./env python scripts/loop_modeling.py \
  --input examples/data/structures/test_in.pdb \
  --loop_start 10 \
  --loop_end 20 \
  --output results/loop_models
```

**Parameters:**
- `--input, -i`: Input PDB structure file (required)
- `--loop_start`: Starting residue number (required)
- `--loop_end`: Ending residue number (required)
- `--loop_cut`: Cut point for closure (optional)
- `--outer_cycles`: Monte Carlo outer cycles (default: 10)
- `--inner_cycles`: Monte Carlo inner cycles (default: 30)

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name rosetta-kic-mcp
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add rosetta-kic-mcp -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "rosetta-kic-mcp": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/rosetta_kic_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/rosetta_kic_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from rosetta-kic-mcp?
```

#### Structure Validation (Fast)
```
Validate this peptide structure file: @examples/data/structures/linear_peptide_sample.pdb
```

#### Structure Prediction (Submit API)
```
Submit a 3D structure prediction job for the sequence GRGDSP with 10 structures and 15 minute runtime
```

#### Peptide Closure (Submit API)
```
Close this linear peptide into a cyclic structure: @examples/data/structures/linear_peptide_sample.pdb
Use 5 structures and GLY residues for closure
```

#### Check Job Status
```
Check the status of job abc12345
```

#### Batch Processing
```
Submit batch structure prediction for these sequences from @examples/data/sequences/sample_cyclic_peptide.txt:
- Generate 5 structures per sequence
- Set runtime to 10 minutes per sequence
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sequences/sample_cyclic_peptide.txt` | Reference a sequence file |
| `@examples/data/structures/linear_peptide_sample.pdb` | Reference a structure file |
| `@configs/default_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "rosetta-kic-mcp": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/rosetta_kic_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/rosetta_kic_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Validate peptide sequence GRGDSP
> Submit structure prediction for cyclic peptide CRGDSC
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 seconds):

| Tool | Description | Parameters |
|------|-------------|------------|
| `validate_peptide_structure` | Validate PDB structure file format | `input_file` |
| `validate_peptide_sequence` | Validate amino acid sequence format | `sequence` |
| `get_server_info` | Get server information and capabilities | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_cyclic_peptide_closure` | Close linear peptides into cycles | `input_file`, `length`, `nstruct`, `residue_type`, `job_name` |
| `submit_structure_prediction` | Predict 3D structure from sequence | `sequence`, `nstruct`, `runtime`, `use_mpi`, `job_name` |
| `submit_loop_modeling` | Model flexible loops with KIC | `input_file`, `loop_start`, `loop_end`, `loop_cut`, `outer_cycles`, `inner_cycles`, `fast_mode`, `job_name` |
| `submit_batch_cyclic_closure` | Batch peptide closure | `input_files`, `length`, `nstruct`, `residue_type`, `job_name` |
| `submit_batch_structure_prediction` | Batch structure prediction | `sequences`, `nstruct`, `runtime`, `job_name` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and status |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with filtering |
| `cleanup_old_jobs` | Clean up old completed jobs |

---

## Examples

### Example 1: Quick Structure Validation

**Goal:** Validate a peptide structure before expensive computations

**Using Script:**
```bash
# Check structure file format
mamba run -p ./env python scripts/cyclic_peptide_closure.py \
  --input examples/data/structures/linear_peptide_sample.pdb \
  --validate_only
```

**Using MCP (in Claude Code):**
```
Validate this peptide structure: @examples/data/structures/linear_peptide_sample.pdb
```

**Expected Output:**
- Structure validation results
- Chain information, residue count
- Basic geometric checks

### Example 2: Cyclic Peptide Closure

**Goal:** Close a linear peptide into a cyclic structure

**Using Script:**
```bash
mamba run -p ./env python scripts/cyclic_peptide_closure.py \
  --input examples/data/structures/linear_peptide_sample.pdb \
  --length 6 \
  --nstruct 5 \
  --output results/closure_test
```

**Using MCP (in Claude Code):**
```
Close this linear peptide into a cyclic structure: @examples/data/structures/linear_peptide_sample.pdb

Use these parameters:
- Maximum loop length: 6
- Number of structures: 5
- Residue type for closure: GLY
- Job name: "closure_demo"

Check the job status and show me the results when complete.
```

### Example 3: Structure Prediction from Sequence

**Goal:** Generate 3D conformers for a cyclic peptide sequence

**Using Script:**
```bash
mamba run -p ./env python scripts/structure_prediction.py \
  --sequence "GRGDSP" \
  --nstruct 10 \
  --runtime 900 \
  --output_dir results/grgdsp_prediction
```

**Using MCP (in Claude Code):**
```
Predict 3D structures for the cyclic peptide sequence GRGDSP:
- Generate 10 structures
- Set runtime limit to 15 minutes
- Name the job "grgdsp_prediction"

Monitor the progress and analyze the results when finished.
```

### Example 4: Batch Virtual Screening

**Goal:** Screen multiple cyclic peptide sequences for structural analysis

**Using MCP (in Claude Code):**
```
I want to screen these cyclic peptide sequences for structural diversity:

Read the sequences from @examples/data/sequences/sample_cyclic_peptide.txt and the other sequence files in that directory.

For each sequence:
1. First validate the sequence format
2. Submit structure prediction with 5 conformers each
3. Set runtime to 10 minutes per sequence
4. Name the batch job "diversity_screen"

Track all jobs and summarize the results when complete.
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

### Sequences

| File | Description | Content |
|------|-------------|---------|
| `sequences/sample_cyclic_peptide.txt` | Basic cyclic peptide | GRGDSP |
| `sequences/sample_cyclic_hexapeptide.txt` | Cysteine-cyclized peptide | CRGDSC |
| `sequences/sample_longer_peptide.txt` | 10-residue peptide | GRGDSPKGAC |

### Structures

| File | Description | Use With |
|------|-------------|----------|
| `structures/linear_peptide_sample.pdb` | Linear pentapeptide GRGDS | `submit_cyclic_peptide_closure` |
| `structures/cyclic_pep_with_link.pdb` | Cyclic peptide with declared bond | Validation tools |
| `structures/test_in.pdb` | Test protein structure | `submit_loop_modeling` |
| `structures/2cpl_min.pdb` | Minimized cyclic peptide | Validation tools |
| `structures/demo_peptide.pdb` | Demo structure | All tools |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `default_config.json` | Shared default settings | General, validation, performance |
| `cyclic_peptide_closure_config.json` | Peptide closure parameters | KIC settings, sampling |
| `structure_prediction_config.json` | Structure prediction settings | Conformers, optimization |
| `loop_modeling_config.json` | Loop modeling parameters | MC cycles, sampling |

### Config Example

From `configs/default_config.json`:
```json
{
  "general": {
    "output_format": "auto",
    "verbose": true,
    "create_backups": false
  },
  "validation": {
    "sequence_min_length": 3,
    "sequence_max_length": 50,
    "validate_inputs": true
  },
  "performance": {
    "max_memory_gb": 8,
    "timeout_seconds": 3600,
    "checkpoint_interval": 100
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.12 pip numpy pandas -y
mamba activate ./env
mamba install -p ./env -c conda-forge rdkit biopython -y
mamba run -p ./env pip install loguru click tqdm fastmcp
```

**Problem:** RDKit import errors
```bash
# Install RDKit from conda-forge
mamba install -p ./env -c conda-forge rdkit -y
```

**Problem:** Import errors
```bash
# Verify installation
mamba run -p ./env python -c "import rdkit; print('RDKit:', rdkit.__version__)"
mamba run -p ./env python -c "import fastmcp; print('FastMCP working')"
mamba run -p ./env python -c "from src.server import mcp; print('Server imports working')"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove rosetta-kic-mcp
fastmcp install src/server.py --name rosetta-kic-mcp
```

**Problem:** Invalid sequence error
```
Ensure your amino acid sequence uses standard single-letter codes (ACDEFGHIKLMNPQRSTVWY).
For cyclic peptides, the sequence represents the linear order before cyclization.
```

**Problem:** Tools not working
```bash
# Test server directly
mamba run -p ./env python src/server.py
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job logs through MCP
# Use get_job_log tool with job_id
```

**Problem:** Job failed
```
Use get_job_log with job_id and tail 100 to see error details.
Common causes:
- Invalid input file paths
- Insufficient disk space
- Memory limitations
- Missing PyRosetta installation
```

**Problem:** PyRosetta not available
```
Scripts run in demo mode when PyRosetta is not available.
For full functionality, install PyRosetta from Rosetta Commons.
Demo mode generates realistic example outputs for testing.
```

### Structure Issues

**Problem:** PDB validation failed
```
Check that your PDB file:
- Uses standard PDB format
- Contains valid amino acid residues
- Has proper chain identifiers
- Is readable and not corrupted
```

**Problem:** Closure fails
```
For peptide closure:
- Ensure termini are properly positioned
- Check for reasonable loop length (3-20 residues)
- Verify input peptide is linear (not already cyclic)
- Consider adjusting closure parameters
```

### Debug Tools

- `validate_peptide_structure()`: Pre-validate PDB files
- `validate_peptide_sequence()`: Pre-validate sequences
- `get_job_log()`: View execution logs with tail parameter
- `get_job_status()`: Check runtime and progress information
- `get_server_info()`: Verify server capabilities

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Run basic tests
mamba run -p ./env python test_simple.py

# Run MCP tests
mamba run -p ./env python test_mcp.py
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
mamba run -p ./env fastmcp dev src/server.py

# Or run directly
mamba run -p ./env python src/server.py
```

### Adding New Tools

To add new computational tools:
1. Add script to `scripts/` directory
2. Create submit_* tool in `src/server.py`
3. Follow established patterns for job management
4. Add validation functions if needed
5. Update documentation

---

## Performance Notes

### Runtime Estimates

| Operation | Typical Runtime | Factors |
|-----------|----------------|---------|
| Structure validation | < 1 sec | File size only |
| Sequence validation | < 1 sec | Sequence length |
| Peptide closure | 10-30 min | Length, nstruct, complexity |
| Structure prediction | 15-60 min | Sequence length, nstruct, runtime limit |
| Loop modeling | 20-90 min | Loop length, sampling cycles |
| Batch processing | scales linearly | Number of inputs × single runtime |

### Resource Requirements

| Operation | Memory | Disk Space |
|-----------|--------|------------|
| Small peptide (6-8 AA) | < 100 MB | < 10 MB |
| Medium peptide (10-15 AA) | 200-500 MB | 50-100 MB |
| Large peptide (>15 AA) | > 500 MB | > 100 MB |

### Optimization Tips

- Use `validate_*` tools before expensive computations
- Start with small `nstruct` values for testing
- Monitor job logs for progress updates
- Clean up old jobs regularly with `cleanup_old_jobs`
- Consider batch processing for multiple similar tasks

---

## Scientific Applications

### Use Cases

1. **Cyclic Peptide Design**
   - Close linear designs into stable cycles
   - Optimize backbone conformations
   - Validate cyclization feasibility

2. **Virtual Screening**
   - Batch process peptide libraries
   - Compare structural predictions
   - Filter by conformational flexibility

3. **Loop Engineering**
   - Model flexible binding regions
   - Optimize loop conformations
   - Study conformational dynamics

### Output Analysis

- **Energy Analysis**: Rosetta energy components and total scores
- **Geometric Validation**: Bond lengths, angles, and clashes
- **RMSD Metrics**: Structural similarity measures
- **Conformational Sampling**: Diversity and coverage analysis

---

## License

Based on Rosetta molecular modeling software. Please refer to original Rosetta licensing terms for academic and commercial use restrictions.

## Credits

Based on [Rosetta](https://github.com/RosettaCommons/rosetta) molecular modeling software from the RosettaCommons.

Implements computational protocols from:
- GeneralizedKIC for peptide closure
- simple_cycpep_predict for structure prediction
- Kinematic Closure for loop modeling