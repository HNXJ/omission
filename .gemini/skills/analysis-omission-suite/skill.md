---
name: analysis-omission-suite
description: High-level orchestration suite for generating the canonical 8-figure manuscript. Enforces aesthetic standards, plotting protocols, and pipeline modularity.
---
# skill: analysis-omission-suite

## When to Use
Use this skill when executing the final visualization and manuscript generation phase. It is the master guide for:
- Generating the 8 core figures (PSTH, Surprise, TFR, SFC, etc.) for the Omission project.
- Ensuring all plots follow the "Madelane Golden Dark" aesthetic.
- Standardizing HTML-based interactive exports to avoid Kaleido dependencies.
- Orchestrating multi-area comparisons (V1, V4, LIP, FEF, etc.) in a unified layout.

## What is Input
- **Processed Data**: Finalized `.npy` arrays and `.csv` factor matrices.
- **Plotting Config**: Aesthetic tokens (colors, fonts, margins) from `OmissionPlotter`.
- **Layout Templates**: Figure-specific dimensions and sub-plot ratios.

## What is Output
- **Interactive HTMLs**: High-fidelity Plotly figures in `outputs/oglo-8figs/`.
- **README Summaries**: Per-figure documentation explaining the "Results" and "Interpretations".
- **Pipeline Logs**: Detailed execution traces of the 15-step LFP-NWB pipeline.

## Algorithm / Methodology
1. **Bootstrap**: Initializes the `OmissionPlotter` with project-wide color schemes (#CFB87C / #9400D3).
2. **Data Loading**: Ingests session-aggregated data using `mmap_mode='r'` to handle multi-gigabyte arrays.
3. **Layer Filtering**: Isolates Superficial vs. Deep layer responses based on the standardized layer CSV.
4. **Spectral Analysis**: Computes dB-relative power and Spike-Field Coupling (SFC) for the specified areas.
5. **Layout Assembly**: Constructs complex multi-panel figures with explicit height/width constraints for dashboard compatibility.

## Placeholder Example
```python
from src.figures.orchestrator import generate_canonical_suite

# 1. Execute the 8-figure pipeline
generate_canonical_suite(output_dir="outputs/oglo-8figs/")

# 2. View results
# Open outputs/oglo-8figs/f001_psth.html in browser
```

## Relevant Context / Files
- [analysis-neuro-omission-poster-figures](file:///D:/drive/omission/.gemini/skills/analysis-neuro-omission-poster-figures/skill.md) — For specific conference-ready formatting.
- [src/core/plotting.py](file:///D:/drive/omission/src/core/plotting.py) — The base plotter implementation.
