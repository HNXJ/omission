---
name: design-neuro-omission-advanced-plotting
description: Technical specification for publication-quality neurophysiology visualizations using the Plotly 'Kaleido-Free' standard.
---
# skill: design-neuro-omission-advanced-plotting

## When to Use
Use this skill for all final figure generation tasks. It is the gold standard for:
- Creating interactive HTML figures for the Omission Dashboard.
- Implementing the "Madelane Golden Dark" aesthetic (#CFB87C / #9400D3).
- Ensuring that plots support native SVG downloads without requiring the Kaleido library.
- Building complex multi-panel figures (TFRs, PPC Spectra, CKA Matrices).

## What is Input
- **Processed Tensors**: `(time, freq, power)` for spectrograms or `(area, area)` for connectivity.
- **Labels**: Stimulus identities (S+, S-, O+, O-).
- **Layout Configs**: Titles, axis limits, and colorbar scales.

## What is Output
- **Interactive HTML Files**: Standalone `.html` files containing the full Plotly object.
- **Sidecar Metadata**: JSON files describing the data source and processing steps for the dashboard.

## Algorithm / Methodology
1. **Interactive Rendering**: Uses `plotly.graph_objects` for fine-grained control over traces.
2. **Kaleido-Free Export**: Bypasses `fig.write_image` by embedding a custom image download button in the Plotly modebar.
3. **Madelane Styling**: 
   - Gold (#CFB87C): Target Stimulus (S+) or Feedforward Gamma.
   - Purple (#9400D3): Omission (O+) or Feedback Beta.
   - Background: White; Grids: Subtle Gray.
4. **Resizing Protocol**: Standardizes all figure containers to 600px height with overflow-y scroll enabled in the dashboard.
5. **Trace Smoothing**: Applies bicubic interpolation (`zsmooth='best'`) for heatmaps to ensure "publication-ready" visual clarity.

## Placeholder Example
```python
import plotly.graph_objects as go

# 1. Create the figure with Madelane colors
fig = go.Figure()
fig.add_trace(go.Scatter(x=time, y=gamma, name="S+ Gamma", line=dict(color="#CFB87C")))
fig.add_trace(go.Scatter(x=time, y=beta, name="O+ Beta", line=dict(color="#9400D3")))

# 2. Configure for Kaleido-Free download
fig.update_layout(modebar_add=['toImage'])
fig.write_html("output/figure_madelane.html", include_plotlyjs='cdn')
```

## Relevant Context / Files
- [design-neuro-omission-branding-theme](file:///D:/drive/omission/.gemini/skills/design-neuro-omission-branding-theme/skill.md) — For color palette details.
- [src/core/plotting_engine.py](file:///D:/drive/omission/src/core/plotting_engine.py) — The standardized plotting implementation.
