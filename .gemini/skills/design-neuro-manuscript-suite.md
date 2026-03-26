---
name: design-neuro-manuscript-suite
description: "Workflow for publication-quality figure drafting and manuscript synthesis."
version: 1.0
---

## ## Context
Standardizes the process of transforming raw analysis into high-fidelity figures and structured manuscript content.

## ## Rules
- **Figure-First**: Always develop the figure and its caption before drafting the results section.
- **Palette**: Madelane Golden Dark (#CFB87C, #000000, #8F00FF).
- **Labels**: High-fidelity axis labels (ms, dB, DVA).
- **Structure**: Part 01 (Numbered Figures 01-20), Part 00 (Oculomotor/Unnumbered).
- **Writing**: Use imperative "Rules" for technical descriptions. Avoid conversational filler.
- **Consistency**: Ensure terminology (e.g., "Ghost Signal," "Precision Scaling") is consistent across all sections.

## ## Examples
```python
# Figure Export Standard
fig.write_html("figures/part01/FIG_06A_V1_PFC_CCG.html")
# Caption Logic
# Caption should contain: Figure Number, Title, Metric, Result, Statistical Significance.
```

# # Keywords:
# Manuscript Drafting, Figure-First, Publication Quality, Plotly Export, Caption Drafting, Golden Dark.
