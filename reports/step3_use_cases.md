# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-31
- **Filter Applied**: cyclic peptide closure using KIC and GenKIC protocols, backbone sampling, physics-based scoring for cyclic peptides
- **Python Version**: 3.12.12
- **Environment Strategy**: Single environment
- **Repository**: Rosetta molecular modeling software

## Use Cases

### UC-001: Cyclic Peptide Closure using GeneralizedKIC
- **Description**: Uses Rosetta's GeneralizedKIC algorithm to close linear peptides into cyclic structures by extending termini and performing kinematic closure with physics-based scoring
- **Script Path**: `examples/use_case_1_genkic_cyclic_peptide_closure.py`
- **Complexity**: Medium
- **Priority**: High
- **Environment**: `./env`
- **Source**: `repo/rosetta/pyrosetta_scripts/pilot/apps/hssnzdh2/PeptideDesign/genKIC_wrapper.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_pdb | file | Linear peptide PDB structure | --input, -i |
| loop_length | int | Maximum loop length to close (3-20) | --length, -l |
| residue_type | string | Residue type for extension (default: GLY) | --resn, -r |
| num_structures | int | Number of structures to generate | --nstruct, -n |
| chain_id | int | Chain number to extend (default: 1) | --chain, -c |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| closed_structures | PDB files | Cyclic peptide structures with closure |
| energy_scores | numeric | Physics-based energy evaluations |
| geometric_validation | numeric | N-C terminal distance and bond quality |

**Example Usage:**
```bash
mamba run -p ./env python examples/use_case_1_genkic_cyclic_peptide_closure.py \
    --input examples/data/structures/linear_peptide_sample.pdb \
    --length 6 \
    --nstruct 5
```

**Example Data**: `examples/data/structures/linear_peptide_sample.pdb`

---

### UC-002: Cyclic Peptide Structure Prediction
- **Description**: Ab initio structure prediction of cyclic peptides using Rosetta's simple_cycpep_predict with MPI-based sampling, GenKIC closure, and comprehensive filtering including Ramachandran validation
- **Script Path**: `examples/use_case_2_cyclic_peptide_structure_prediction.py`
- **Complexity**: High
- **Priority**: High
- **Environment**: `./env`
- **Source**: `repo/rosetta/tests/scientific/tests/simple_cycpep_predict/1.submit.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Amino acid sequence (single letter codes) | --sequence, -s |
| output_dir | string | Output directory for results | --output_dir, -o |
| database_path | string | Rosetta database path (auto-detected) | --database |
| native_pdb | file | Optional native structure for RMSD | --native |
| runtime | int | Maximum runtime in seconds | --runtime |
| num_structures | int | Number of structures to generate | --nstruct |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| silent_file | file | Rosetta silent file with predicted structures |
| energy_metrics | file | Detailed energy breakdowns |
| rmsd_analysis | file | RMSD to lowest energy and native (if provided) |
| sasa_metrics | file | Solvent accessible surface area analysis |

**Example Usage:**
```bash
mamba run -p ./env python examples/use_case_2_cyclic_peptide_structure_prediction.py \
    --sequence "GRGDSP" \
    --output_dir results \
    --nstruct 1000
```

**Example Data**: `examples/data/sequences/sample_cyclic_peptide.txt`

---

### UC-003: KIC Loop Modeling
- **Description**: Models flexible loops in peptides and proteins using Kinematic Closure with Monte Carlo sampling and backbone perturbation for conformational exploration
- **Script Path**: `examples/use_case_3_kic_loop_modeling.py`
- **Complexity**: Medium
- **Priority**: Medium
- **Environment**: `./env`
- **Source**: `repo/rosetta/source/src/python/PyRosetta/src/demo/untested/loops_kic.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_pdb | file | Protein/peptide structure | --input, -i |
| loop_start | int | Starting residue of loop region | --loop_start |
| loop_end | int | Ending residue of loop region | --loop_end |
| loop_cut | int | Cut point for closure (auto-calculated) | --loop_cut |
| outer_cycles | int | Monte Carlo outer cycles | --outer_cycles |
| inner_cycles | int | Monte Carlo inner cycles | --inner_cycles |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| final_structure | PDB file | Remodeled structure with new loop |
| energy_trajectory | log | Energy during Monte Carlo simulation |
| rmsd_metrics | log | RMSD to starting conformation |

**Example Usage:**
```bash
mamba run -p ./env python examples/use_case_3_kic_loop_modeling.py \
    --input examples/data/structures/test_in.pdb \
    --loop_start 10 \
    --loop_end 20
```

**Example Data**: `examples/data/structures/test_in.pdb`

---

## Summary

| Metric | Count |
|--------|-------|
| Total Use Cases Found | 15+ (filtered to 3 core use cases) |
| Scripts Created | 3 |
| High Priority | 2 |
| Medium Priority | 1 |
| Low Priority | 0 |
| Demo Data Copied | Yes |

## Repository Analysis

### Key Findings
- **Rich KIC Implementation**: Rosetta contains comprehensive KIC and GenKIC implementations
- **Cyclic Peptide Focus**: Multiple scripts specifically for cyclic peptide modeling
- **Scientific Validation**: Well-tested protocols with scientific benchmarks
- **PyRosetta Integration**: Most functionality accessible through Python bindings

### Code Quality Assessment
- **Well-Documented**: Original scripts contain good documentation and parameter explanations
- **Modular Design**: Clear separation between different algorithmic approaches
- **Error Handling**: Robust error checking and validation in most scripts
- **Scientific Rigor**: Proper energy functions and geometric validation

### Dependencies Identified
- **Core Requirement**: PyRosetta bindings for full functionality
- **Database Dependency**: Rosetta database required for energy functions
- **Optional**: MPI for parallel execution in structure prediction
- **Scientific Libraries**: RDKit and BioPython for molecular manipulation

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/rosetta/source/test/core/io/pose_from_sfr/cyclic_pep_with_link.pdb` | `examples/data/structures/cyclic_pep_with_link.pdb` | Test cyclic peptide with declared bond |
| `repo/rosetta/source/src/python/PyRosetta/src/test/data/test_in.pdb` | `examples/data/structures/test_in.pdb` | Test protein structure for loop modeling |
| Created | `examples/data/structures/linear_peptide_sample.pdb` | Sample linear pentapeptide GRGDS for closure testing |
| Created | `examples/data/sequences/sample_cyclic_peptide.txt` | GRGDSP sequence |
| Created | `examples/data/sequences/sample_cyclic_hexapeptide.txt` | CRGDSC sequence with cysteine terminals |
| Created | `examples/data/sequences/sample_longer_peptide.txt` | GRGDSPKGAC sequence (10 residues) |

## Implementation Notes

### Script Features
- **Robust CLI**: All scripts have comprehensive command-line interfaces
- **Error Handling**: Graceful handling when PyRosetta is not available
- **Documentation**: Detailed help text and usage examples
- **Validation**: Input parameter validation and sanity checks

### Extensibility
- **Modular Functions**: Core functionality separated from CLI parsing
- **Configurable Parameters**: Extensive customization options
- **Output Flexibility**: Multiple output formats and detail levels
- **Integration Ready**: Designed for easy integration into workflows

### Performance Considerations
- **Scalability**: Support for both single-structure and high-throughput modes
- **Parallelization**: MPI support where applicable
- **Memory Management**: Efficient handling of large structure sets
- **Time Controls**: Timeout and iteration limits to prevent runaway processes

## Recommendations

### For Production Use
1. **Install Full Rosetta**: Compile Rosetta with PyRosetta bindings for complete functionality
2. **Database Setup**: Ensure proper Rosetta database configuration
3. **Resource Planning**: Cyclic peptide prediction can be computationally intensive
4. **Validation**: Test with known structures before production runs

### For Development
1. **Testing Framework**: Scripts include demonstration modes when PyRosetta unavailable
2. **Parameter Tuning**: Start with default parameters and adjust based on specific needs
3. **Output Analysis**: Implement post-processing for energy and geometric analysis
4. **Integration**: Consider MCP server integration for workflow automation

### For Scientific Applications
1. **Validation Studies**: Compare results with known cyclic peptide structures
2. **Parameter Optimization**: Tune sampling parameters for specific peptide classes
3. **Ensemble Analysis**: Use multiple predictions for conformational ensemble studies
4. **Experimental Correlation**: Validate predictions against experimental data when available