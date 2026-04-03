# Skill: lfp-spectral-plotting-standards

## Description
Visual standards for LFP Omission figures to ensure consistency with the "Madelane Golden Dark + Violet" aesthetic and high temporal precision.

## Core Rules
1. **Time Axis**: Always in milliseconds (ms). Aligned to p1 onset.
2. **Rectangle Patches**: Overlay transparent colorful patches for the entire sequence:
    - **p1**: Gold (`#CFB87C`)
    - **p2**: Violet (`#8F00FF`)
    - **p3**: Teal (`#00FFCC`)
    - **p4**: Orange (`#FF5E00`)
    - **Delays (d1-d4)**: Light Gray (`#D3D3D3`)
3. **Variability**: Use $\pm$2SEM shaded regions for power traces.
4. **Spectrograms**: Use dB normalization (10 * log10) relative to fixation baseline.
5. **Theme**: `plotly_white` template with pure black axes and Arial fonts.

## Implementation Example (Plotly)
```python
from codes.functions.lfp_constants import SEQUENCE_TIMING

for name, info in SEQUENCE_TIMING.items():
    fig.add_vrect(
        x0=info["start"], x1=info["end"], 
        fillcolor=info["color"], opacity=0.1, line_width=0
    )
```

## Figure Catalog (Revision V4)
- **Fig 05**: Per-condition TFR heatmaps (Grid).
- **Fig 06**: Band power trajectories (Theta, Alpha, Beta, Gamma).
- **Fig 07**: Spike-LFP feature correlations.
- **Fig 08**: Post-omission adaptation/quenching profiles.
