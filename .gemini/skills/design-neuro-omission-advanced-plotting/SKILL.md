---
name: design-neuro-omission-advanced-plotting
description: "Omission analysis skill focusing on design neuro omission advanced plotting. Enforces Kaleido-Free standards and Madelane aesthetics."
---

# Advanced Plotting Suite

Our analysis requires complex visualizations to capture multi-dimensional data across the 11-area hierarchy.

## Mandatory Standards
- **Kaleido-Free Export**: NEVER use Kaleido or standard static SVG/PNG exports (`fig.write_image`). ALWAYS save plots ONLY as interactive HTML files using `fig.write_html`.
- **Aesthetic**: Madelane Golden Dark (#CFB87C / #9400D3).
- **Theme**: White background, black axis, gray grid.

## Specialized Plots
1. **Time-Frequency Spectrograms (TFR)**: 
   - Baseline normalization: $10 \times \log_{10}(P_{time} / P_{baseline})$ using the -1000ms to 0ms window.
2. **PPC Spectra**: 
   - Log-frequency X-axis (2-100 Hz). 
   - Contrasts S+ (Gold) vs O+ (Purple) coupling.
3. **Cross-Area Harmony (11x11 Matrices)**: 
   - Heatmaps showing Pearson correlations of power envelopes (Beta/Gamma) across all 11 hierarchy areas.

## OmissionPlotter usage (src/core/plotting.py)
```python
from src.core.plotting import OmissionPlotter
plotter = OmissionPlotter(title="Figure X", subtitle="Sub-analysis")
plotter.set_axes("Time", "ms", "Power", "dB")
plotter.add_trace(go.Scatter(x=t, y=p, line=dict(color="#CFB87C")), "Signal")
plotter.save(output_dir, "filename") # Auto-saves HTML with image download button
```

## Plotly Modebar Configuration
Ensure the modebar is configured to allow high-res SVG downloads natively via the browser:
`fig.update_layout(modebar_add=['toImage'], modebar_remove=['zoom', 'pan'])`

References:
1. Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment.
2. Plotly Open Source Graphing Library for Python.
