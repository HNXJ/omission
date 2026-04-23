---
name: analysis-mmff
---
# analysis-mmff

## Purpose
Mean-Matched Fano Factor (MMFF) computation and visualization. Controls for firing-rate confounds in variability analysis. Absorbs `science-neuro-omission-variability-quenching`.

## Input
| Name | Type | Description |
|------|------|-------------|
| spike_data | ndarray(trials, units, T) | Binned spike counts |
| nwb_path | str | For unit-to-area mapping |
| win_size | int | Sliding window (default: 150ms) |
| step | int | Step size (default: 5ms) |
| sigma | float | Gaussian smoothing (default: 5.0) |

## Output
| Name | Type | Description |
|------|------|-------------|
| mmff_traces | dict | `{area: {condition: ndarray(T,)}}` time-resolved MMFF |
| html_figure | str | Interactive Plotly HTML with SEM shading |

## Key Formula
- **Fano Factor**: `FF = σ² / μ` (FF<1 = regular, FF>1 = bursty)
- **Mean-Matching**: Equalizes FR distributions across time bins via subsampling before computing FF
- **Quenching**: Stimulus/surprise collapses high-variance spontaneous state

## Example
```python
from src.analysis.mmff_pipeline import compute_mmff, plot_mmff
mmff_data = compute_mmff(spike_path='spikes.npy', nwb_path='session.nwb', win_size=150, step=5)
fig = plot_mmff(mmff_data, area='V1')
fig.write_html('outputs/v1_mmff.html')
print(f"""[result] MMFF computed for {len(mmff_data)} areas""")
```

## Files
- [omission_hierarchy_utils.py](file:///D:/drive/omission/codes/functions/omission_hierarchy_utils.py) — Core functions
- [compute_mean_matched_fano.py](file:///D:/drive/omission/codes/scripts/compute_mean_matched_fano.py) — Orchestrator
