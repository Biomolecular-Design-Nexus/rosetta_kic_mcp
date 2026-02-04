#!/bin/bash
# Quick Setup Script for Rosetta KIC MCP
# Rosetta: Biomolecular Modeling Library with KIC and GeneralizedKIC protocols
# Supports cyclic peptide computational analysis using Rosetta's kinematic closure
# Source: https://github.com/RosettaCommons/rosetta

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up Rosetta KIC MCP ==="

# Step 1: Create Python environment
echo "[1/5] Creating Python 3.12 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.12 pip numpy pandas -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.12 pip numpy pandas -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env && ./env/bin/pip install numpy pandas)

# Step 2: Install RDKit
echo "[2/5] Installing RDKit..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env -c conda-forge rdkit -y) || \
./env/bin/pip install rdkit

# Step 3: Install BioPython
echo "[3/5] Installing BioPython..."
(command -v mamba >/dev/null 2>&1 && mamba install -p ./env -c conda-forge biopython -y) || \
./env/bin/pip install biopython

# Step 4: Install utility packages
echo "[4/5] Installing utility packages..."
./env/bin/pip install loguru click tqdm

# Step 5: Install fastmcp
echo "[5/5] Installing fastmcp..."
./env/bin/pip install --ignore-installed fastmcp

echo ""
echo "=== Rosetta KIC MCP Setup Complete ==="
echo ""
echo "Note: This MCP requires Rosetta to be installed separately."
echo "Rosetta installation options:"
echo "  1. Conda: Add RosettaCommons channel to ~/.condarc"
echo "     channels:"
echo "       - https://conda.rosettacommons.org"
echo "       - conda-forge"
echo "  2. Docker: https://hub.docker.com/r/rosettacommons/rosetta"
echo "  3. Build from source: https://www.rosettacommons.org/docs/latest/getting_started/Getting-Started"
echo ""
echo "To run the MCP server: ./env/bin/python src/server.py"
