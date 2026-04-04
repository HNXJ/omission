# Visual Identity: Vanderbilt Golden Dark + Violet

Our project utilizes a high-fidelity, professional aesthetic designed for scientific clarity, visual impact, and hierarchical organization.

## 🎨 Color Palette
- **Primary (Gold)**: Vanderbilt Gold (`#CFB87C`). Used for primary data traces, highlights, and branding.
- **Background (Black)**: Pure Black (`#000000`). Provides maximum contrast and a modern 'lab' feel.
- **Secondary (Violet)**: Electric Violet (`#8F00FF`). Used for 'Surprise' signals, high-order areas (PFC/FEF), and secondary highlights.
- **Neutral (Slate)**: Slate Gray (`#708090`). Used for secondary axes, grid lines, and baseline data.

## 📊 Plotly & Matplotlib Configuration
Interactive reports and static figures must adhere to this theme.

```python
import plotly.io as pio
import matplotlib.pyplot as plt

# Plotly Theme
pio.templates.default = 'plotly_dark'
brand_colors = ['#CFB87C', '#8F00FF', '#FFFFFF', '#708090']

# Matplotlib Style
plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#000000'
plt.rcParams['figure.facecolor'] = '#000000'
plt.rcParams['axes.edgecolor'] = '#708090'
plt.rcParams['text.color'] = '#FFFFFF'
```

## 📐 Design Principles
1. **Hierarchy**: Use Gold for sensory/low-order areas (V1) and Violet for executive/high-order areas (PFC).
2. **Clarity**: No 'chartjunk'. Axes must be clearly labeled with units (ms, Hz, DVA).
3. **Interactivity**: All population manifolds and PSTHs should be exportable as HTML with hover details using Plotly.
4. **Consistency**: Use the same color mappings across all figures to aid cross-referencing.

## 🏺 Aesthetic Motivation
The **'Madelane Golden Dark + Violet'** aesthetic merges the prestige of Vanderbilt University with the dynamic energy of neural surprise signaling, ensuring every figure is publication-ready and visually striking.
