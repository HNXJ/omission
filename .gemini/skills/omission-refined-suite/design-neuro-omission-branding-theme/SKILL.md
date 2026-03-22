# Visual Identity: Vanderbilt Golden Dark

Our project utilizes a high-contrast, professional aesthetic designed for scientific clarity and visual impact.

Color Palette:
- Primary: Vanderbilt Gold (#CFB87C). Used for highlights, data points of interest, and brand elements.
- Background: Pure Black (#000000). Provides maximum contrast and a modern 'lab' feel.
- Neutral: Slate Gray (#708090). Used for secondary axes and grid lines.

Plotly Configuration:
Interactive reports use a dark template.
```python
import plotly.io as pio
pio.templates.default = 'plotly_dark'
brand_colors = ['#CFB87C', '#FFFFFF', '#708090']
```

Design Principles:
1. Clarity: No chartjunk. Axes must be clearly labeled with units (ms, Hz, DVA).
2. Interactivity: All population manifolds and PSTHs should be exportable as HTML with hover details.
3. Consistency: Use the same color for Area V1 across all figures to aid cross-referencing.

Aesthetic Motivation:
The 'Madelane Golden Dark' aesthetic reflects the prestige of Vanderbilt University while maintaining the technical edge of modern neuroscience.

References:
1. Tufte, E. R. (2001). The Visual Display of Quantitative Information. Graphics Press.
2. Rougier, N. P., et al. (2014). Ten Simple Rules for Better Figures. PLOS Computational Biology.
