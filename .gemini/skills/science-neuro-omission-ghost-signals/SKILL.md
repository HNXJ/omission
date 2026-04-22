---
name: science-neuro-omission-ghost-signals
description: Analysis framework for quantifying "Neural Ghosts" — the persistence of stimulus-specific representations during physical absence.
---
# skill: science-neuro-omission-ghost-signals

## When to Use
Use this skill when analyzing the content of neural activity during omission windows. It is mandatory for:
- Detecting stimulus-specific persistence (Identity A vs. B) during a gray-screen omission.
- Quantifying the "Blackboard Effect" where V1 represents top-down priors.
- Correlating omission-window activity trajectories with stimulus-evoked trajectories.
- Dissociating passive decay from active top-down maintenance.

## What is Input
- **Identity-Conditioned PSTHs**: Per-unit firing rates for expected-A vs. expected-B omissions.
- **Stimulus Templates**: The "clean" neural response to actual stimulus presentations.
- **Population Vectors**: Multi-unit activity states across the 11-area hierarchy.

## What is Output
- **Ghost Scores**: Correlation coefficients between omission activity and stimulus-evoked activity.
- **Trajectory Maps**: PCA/UMAP embeddings showing how omission states overlap with stimulus states.
- **Persistence Latencies**: Duration for which the "Ghost" signal remains significant post-omission.

## Algorithm / Methodology
1. **PSTH Matching**: Calculate the Pearson correlation between the omission window and the corresponding stimulus window.
2. **Identity Decoding**: Train a classifier (e.g., SVM) on stimulus identity and test it on omission identity.
3. **Blackboard Hypothesis**: High-order feedback (PFC/FEF) targets V1 deep layers to "paint" the expectation.
4. **Surprise Divergence**: Identify the timepoint where the "Ghost" (persistence) transitions into "Surprise" (prediction error).

## Placeholder Example
```python
import numpy as np

def calculate_ghost_correlation(omit_activity, stim_template):
    """
    Computes the 'Neural Ghost' score.
    Higher values imply stronger contextual persistence.
    """
    # Pearson correlation between expected-A omission and actual-A stimulus
    return np.corrcoef(omit_activity, stim_template)[0, 1]

# Example: Ghost score for a V1 deep-layer unit
score = calculate_ghost_correlation(v1_unit_omit_A, v1_unit_stim_A)
```

## Relevant Context / Files
- [omission-factors](file:///D:/drive/omission/.gemini/skills/omission-factors/skill.md) — For the feature vectors used in ghost scoring.
- [src/analysis/contextual_persistence.py](file:///D:/drive/omission/src/analysis/contextual_persistence.py) — The canonical implementation.
