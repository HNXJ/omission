# Skill: nwb-lfp-modular-pipeline

## Description
A modular, high-performance LFP analysis pipeline for Sequential Visual Omission tasks. Designed for consistency across large-scale NWB datasets.

## Architecture
- **Entrypoints (`scripts/`)**:
    - `run_lfp_omission_pipeline.py`: Orchestrates loading, preprocessing, TFR, and initial plotting.
    - `generate_lfp_figure_templates.py`: Creates blank placeholders for the core figure suite.
- **Utilities (`functions/`)**:
    - `lfp_io`: NWB/NPY loading with mandatory `np.nan_to_num` sanitation.
    - `lfp_events`: Canonical timeline reconstruction aligned to p1 onset (0ms).
    - `lfp_preproc`: Bipolar referencing, baseline normalization (% change), and epoch extraction.
    - `lfp_tfr`: Hanning-windowed spectrograms with 98% overlap and band-power collapsing.
    - `lfp_connectivity`: Pairwise coherence and spectral Granger causality.
    - `lfp_plotting`: Standardized Plotly visualizations with sequence rectangle patches.

## Usage
```python
from codes.functions.lfp_io import load_session
from codes.functions.lfp_events import build_event_table
from codes.functions.lfp_preproc import apply_bipolar_ref

session = load_session(Path("session.nwb"))
events = build_event_table(session)
lfp_bip = apply_bipolar_ref(session["lfp"])
```

## Mandatory Standards
1. **Timing**: Aligned to Presentation-1 onset (Sample 1000 = 0ms).
2. **Sanitation**: Always use `np.nan_to_num` on LFP data.
3. **Reproducibility**: Save `.metadata.json` sidecars for every derived array.
