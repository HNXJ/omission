---
name: analysis-neuro-omission-functional-connectivity
description: Quantifies the synchronization and coordination between brain areas using Spectral Harmony (Power Envelope Correlations) and Pairwise Phase Consistency (PPC).
---
# skill: analysis-neuro-omission-functional-connectivity

## When to Use
Use this skill to map the functional network architecture during omission tasks. It is specifically used for:
- Building "Spectral Harmony" matrices (11x11 regional correlations).
- Identifying frequency-specific hubs of coordination (Gamma vs. Beta).
- Measuring Spike-Field Coupling using bias-free PPC.

## What is Input
- **Power Envelopes**: Time-resolved power for specific bands (Delta through High-Gamma).
- **Spike Trains & LFP**: For phase-locking analysis.
- **Regional Mask**: Grouping of electrodes into the 11 target brain areas.

## What is Output
- **Connectivity Matrices**: 11x11 Pearson correlation matrices of band power envelopes.
- **PPC Spectra**: Phase-consistency values across the 1-100Hz range.
- **Figures**: Heatmaps of regional coordination and line plots of phase-locking (Fig 8).

## Algorithm / Methodology
1. **Envelope Extraction**: Computes the Hilbert transform of band-passed LFP signals to get the instantaneous power envelope.
2. **Spectral Harmony**: Performs pairwise Pearson correlations between the envelopes of all 11 brain regions.
3. **PPC Calculation**: For every spike-LFP pair, it calculates the average cosine of the phase difference across trials ($PPC = \frac{2}{N(N-1)} \sum \sum cos(\theta_i - \theta_j)$).
4. **Hierarchy Mapping**: Analyzes how connectivity patterns shift from bottom-up (Stimulus) to top-down (Omission).

## Placeholder Example
```python
import numpy as np
from src.analysis.connectivity import compute_spectral_harmony

# 1. Prepare envelope matrix (11 areas x Time)
envelopes = np.random.rand(11, 1000) 

# 2. Compute Harmony
harmony_matrix = np.corrcoef(envelopes)

# 3. Verify diagonal is 1.0
assert np.allclose(np.diag(harmony_matrix), 1.0)
print("Spectral Harmony Matrix computed successfully.")
```

## Relevant Context / Files
- [analysis-lfp-pipeline](file:///D:/drive/omission/.gemini/skills/analysis-lfp-pipeline/skill.md) — For band definitions and preprocessing.
- [src/analysis/connectivity.py](file:///D:/drive/omission/src/analysis/connectivity.py) — Core implementation.
