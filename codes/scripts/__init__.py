"""
Canonical Entrypoint Map for the Omission Hierarchy Analysis Package.

This module defines the canonical runners and orchestration scripts for the 
different analytical domains of the project. Since script filenames use hyphens 
by project convention, they are registered here as paths.
"""

import os
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

CANONICAL_ENTRYPOINTS = {
    # LFP Pipeline
    "lfp_pipeline": SCRIPTS_DIR / "pipelines" / "master-lfp-pipeline.py",
    
    # Spiking Dynamics
    "spiking_dynamics": SCRIPTS_DIR / "pipelines" / "run-spiking-dynamics-suite.py",
    
    # Eye/Behavior Analysis
    "eye_behavior": SCRIPTS_DIR / "pipelines" / "run-omission-dynamics-lfp-eye.py",
    
    # Decoding / Classification
    "decoding": SCRIPTS_DIR / "analysis" / "decode-omission-identity.py",
    
    # Figure Generation
    "figures": SCRIPTS_DIR / "figures" / "generate-figures.py",
    
    # QC / Validation
    "qc": SCRIPTS_DIR / "qc" / "verify-trial-counts.py",
}

def get_entrypoint(domain):
    """Retrieve the canonical script path for a given analytical domain."""
    return CANONICAL_ENTRYPOINTS.get(domain)

__all__ = ['CANONICAL_ENTRYPOINTS', 'get_entrypoint']
