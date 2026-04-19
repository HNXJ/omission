# Omission: Hierarchical Visual Prediction Pipeline

Canonical repository for the Omission project, implementing hierarchical V1-PFC (1-11) analysis.

## Repository Architecture
- **`src/`**: Modular analytical logic and figure generators.
  - `analysis/`: Functional core (LFP, Spiking, IO, Visualization).
  - `f001_theory/` through `f030_recurrence_dynamics/`: Canonical standardized analysis folders.
  - `scripts/`: Pipeline entrypoints (e.g., `run_pipeline.py`).
- **`context/`**: Foundational mandates and session-area mapping.

## Canonical Pipeline
The master pipeline generates publication-grade figures from raw NPY arrays.
```bash
python -m src.scripts.run_pipeline
```

## Core Standards
- **Timing**: Omission-Local alignment (0ms = Omission Onset; family-aware: p2, p3, or p4).
- **LFP**: Trial-wise STFT (98% overlap), linear power, Relative Power (dB) normalization to [-250, -50]ms baseline.
- **SFC**: Phase-Locking Value (PLV) using Mean Resultant Vector; Subsampling corrected to equate spike counts.
- **Filtering**: Units must pass Functional SNR > 1.0 and minimum firing rate (0.5 Hz) for spectral inclusion.
- **Plotting**: Interactive HTML (Kaleido-Free) with native 'Download to SVG' button.

## Figure Mapping (Canonical 1-30)
1-11: Core Spiking, Spectral, and Laminar Routing.
12-15: Functional Connectivity (MI) and Network Dynamics.
16: Impedance Tensor Estimation.
17-25: Surprise Scaling, Ghost Signals, PAC, Effective Connectivity, Pupil Decoding, Variability.
26-30: State Latency, Identity Coding, Cross-Area Manifolds, Info Bottleneck, Recurrence.
