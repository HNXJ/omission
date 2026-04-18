# Omission: Hierarchical Visual Prediction Pipeline

Canonical repository for the Omission project, implementing hierarchical V1-PFC (1-11) analysis.

## Repository Architecture (Strict 3-Folder)
- **`src/`**: Modular analytical logic and figure generators.
  - `analysis/`: Functional core (LFP, Spiking, IO, Visualization).
  - `figures/`: Thin wrappers for generating Figures 1-11.
  - `scripts/`: Pipeline entrypoints (e.g., `run_pipeline.py`).
- **`context/`**: Foundational mandates and session-area mapping.
- **`tests/`**: Unit and integration tests for signal processing.

## Canonical Pipeline
The master pipeline generates publication-grade figures from raw NPY arrays.
```bash
python -m src.scripts.run_pipeline
```

## Core Standards
- **Timing**: Omission-Local alignment (0ms = Omission Onset at 1031ms from P1).
- **LFP**: Trial-wise STFT (98% overlap), linear power, Relative Power (dB) normalization to [-250, -50]ms baseline.
- **SFC**: Phase-Locking Value (PLV) using Mean Resultant Vector; Subsampling corrected to equate spike counts.
- **Filtering**: Units must pass Functional SNR > 1.0 and minimum firing rate (0.5 Hz) for spectral inclusion.
- **Plotting**: Interactive HTML (Kaleido-Free) with native 'Download to SVG' button.

## Figure Mapping
1. Theory Schematic
2. Experimental Design & CSD
3. Omission-Local PSTHs (Population)
4. State-Space Manifolds (PCA)
5. Time-Frequency Spectrograms (TFR)
6. Band-Specific Power Dynamics (±SEM)
7. Spike-Field Coupling (PLV Spectrum)
8. Spectral Harmony (Cross-Area Power Corr)
9. Individual SFC (Unit-specific PLV)
10. SFC Delta (Omission - Stimulus PLV)
11. Laminar Routing (Beta/Gamma depth profiles)
