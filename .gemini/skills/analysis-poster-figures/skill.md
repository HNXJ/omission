---
name: analysis-poster-figures
description: Specialized plotting functions for high-impact posters (SFN, Cosyne). Focuses on multi-panel layouts, condition-specific color coding, and publication-ready aesthetics.
---
# skill: analysis-poster-figures

## When to Use
Use this skill when preparing presentation materials for conferences or publications. It is tailored for:
- Generating "Hierarchy" plots showing LFP band-power (Beta/Gamma) across 11 brain areas.
- Creating "Dissociation" heatmaps that highlight the beta-gamma flip during omission.
- Visualizing "Neuron Group Traces" (Excited, Inhibited, Omission-Selective) with SEM shading.
- Producing "Spectral Network" diagrams where edge weights represent inter-area coherence.

## What is Input
- **Trace Dictionaries**: Mean and SEM arrays keyed by `(area, condition, band)`.
- **Timing Metadata**: Event onset/offset indices for plotting shaded rectangles.
- **Color Palette**: Standard project tokens (Gold=#CFB87C, Violet=#8F00FF, Pink=#FF1493).

## What is Output
- **SVG/HTML Figures**: Publication-quality vector graphics and interactive viewers.
- **Panel Grids**: Standardized 1xN or NxM layouts for multi-area comparison.
- **Annotated Plots**: Figures with explicit "Omission" window shading and P1-P4 markers.

## Algorithm / Methodology
1. **Grid Allocation**: Automatically calculates subplot counts based on the `AREA_ORDER` (V1 -> PFC).
2. **Shading Protocol**: Applies a translucent pink rectangle (`#FF1493`, alpha=0.2) over the condition-specific omission window.
3. **Band Filtering**: Aggregates power traces into specific bands: Theta (4-8Hz), Alpha (8-14Hz), Beta (15-30Hz), Gamma (35-100Hz).
4. **SEM Overlay**: Uses Plotly's `fill='tonexty'` to render confidence intervals without obscuring mean traces.
5. **Aesthetic Normalization**: Enforces `plotly_white` theme, Arial fonts, and consistent axis scaling across all panels.

## Placeholder Example
```python
from src.figures.poster_figures import plot_band_power_hierarchy

# 1. Generate 11-area Beta power comparison
fig = plot_band_power_hierarchy(
    traces=data_dict, 
    band='Beta', 
    areas=['V1', 'V4', 'FEF', 'PFC'],
    conditions=['RRRR', 'RXRR']
)

# 2. Save for poster
fig.write_image("outputs/posters/beta_hierarchy.svg")
```

## Relevant Context / Files
- [analysis-omission-suite](file:///D:/drive/omission/.gemini/skills/analysis-omission-suite/skill.md) — For manuscript-level figure standards.
- [src/figures/poster_figures.py](file:///D:/drive/omission/src/figures/poster_figures.py) — Implementation of these plotting functions.
