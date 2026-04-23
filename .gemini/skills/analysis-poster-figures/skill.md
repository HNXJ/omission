---
name: analysis-poster-figures
---
# analysis-poster-figures

## Purpose
Conference poster plotting functions (SFN, Cosyne). Multi-panel layouts, condition color coding, shaded omission windows, SEM overlays.

## Input
| Name | Type | Description |
|------|------|-------------|
| traces | dict | Mean/SEM arrays keyed by `(area, condition, band)` |
| timing | dict | Event onset/offset indices for shaded rectangles |
| palette | dict | `{gold: '#CFB87C', violet: '#8F00FF', pink: '#FF1493'}` |

## Output
| Name | Type | Description |
|------|------|-------------|
| figure | go.Figure | Multi-panel Plotly figure |
| html_path | str | Saved interactive HTML |

## Example
```python
from src.figures.poster_figures import plot_band_power_hierarchy
fig = plot_band_power_hierarchy(traces=data, band='Beta', areas=['V1','PFC'], conditions=['RRRR','RXRR'])
fig.write_html("outputs/posters/beta_hierarchy.html")
print(f"""[result] Poster figure exported""")
```

## Files
- [poster_figures.py](file:///D:/drive/omission/src/figures/poster_figures.py) — Implementation
