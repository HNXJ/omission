---
name: analysis-mmff-compute
description: Mean-Matched Fano Factor (MMFF) computation core. Maps units to areas, collects sliding-window spike statistics, applies mean-matching, and smooths traces.
cross-ref: analysis-mmff-plot (visualization of computed traces)
---

# skill: analysis-mmff-compute

## purpose
Computes the MMFF — a firing-rate-normalized variability metric — across brain areas and conditions.

## core functions

### `get_unit_to_area_map(nwb_path)`
- Reads NWB electrode metadata.
- Returns `dict[(probe_id, local_unit_idx)] → area_label`.

### `collect_spike_stats(spk_file, u_map, time_bins, win_size)`
- Loads `.npy` spike arrays (`(n_trials, n_units, T)`).
- Sliding window of `WIN_SIZE=150ms`, step `STEP=5ms`.
- Accumulates per-window mean `m` and variance `v` lists by area.

### `apply_mean_matching(stats_dict, hist_bins)`
- Equalizes mean firing rate distributions across time bins.
- Uses global histogram as reference; subsamples to min density ratio.
- Returns matched `(ms, vs)` for Fano Factor: `FF = var/mean`.

### `smooth_trace(trace, sigma=5.0)`
- Gaussian smoothing via `scipy.ndimage.gaussian_filter1d`.
- NaN-safe: interpolate → smooth → re-apply NaN mask.

## output
- `checkpoints/area_mmff_traces.json`
- Structure: `{area: {condition: [float, ...]}}` over time bins.

## parameters
| Param | Value | Notes |
|---|---|---|
| WIN_SIZE | 150ms | Spike count window |
| STEP | 5ms | Sliding step |
| AREA_ORDER | 11 areas | V1→PFC canonical order |
| sigma | 5.0 | Gaussian smoothing |

## mandatory
- `np.nan_to_num` on all spike arrays before stat collection.
- Skip time bins with <10 units for MMFF stability.
- Never save if all values NaN — log to `context/queue/`.


---

---
name: analysis-mmff-plot
description: Visualization of Mean-Matched Fano Factor traces across areas and conditions. Plotly standards for the quenching and variability figures.
cross-ref: analysis-mmff-compute (trace computation)
---

# skill: analysis-mmff-plot

## purpose
Renders MMFF traces from `checkpoints/area_mmff_traces.json` into publication-quality Plotly figures.

## figure targets
- **Fig Variability Hierarchy**: MMFF traces per area, all conditions, ±2SEM shading.
- **Fig Quenching Summary**: MMFF at post-omission stimulus (p3/p4) vs baseline.
- **Fig MMFF Hierarchy**: Sorted bar plot — areas ranked by quenching magnitude.

## plotly standards
- **Theme**: `plotly_white`.
- **Colors**: One color per condition (RRRR=Gold, RXRR=Violet, RRXR=Teal, RRRX=Orange).
- **Variability**: ±2SEM as `go.Scatter` with `fill='tonexty'`, `opacity=0.2`.
- **Patch**: Pink rectangle (#FF1493, α=0.2) over omission window (d1-p2-d2 or d2-p3-d3).
- **X-axis**: Always ms aligned to p1=0ms.
- **Export**: `.html` + `.svg` for every figure.

## quick ref
```python
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=t_ms, y=trace_mean, name=area,
                         line=dict(color=color)))
fig.add_trace(go.Scatter(x=t_ms, y=trace_mean+2*sem, fill=None, ...))
fig.add_trace(go.Scatter(x=t_ms, y=trace_mean-2*sem, fill='tonexty',
                         fillcolor='rgba(r,g,b,0.2)', line=dict(width=0)))
fig.update_layout(template='plotly_white')
fig.write_html('output/fig_mmff.html')
fig.write_image('output/fig_mmff.svg')
```


---

## omission_hierarchy_utils — core functions
| Function | Signature | Purpose |
|---|---|---|
| `get_unit_to_area_map(nwb_path)` | `str → dict` | Maps `(probe_id, local_idx)` → area label from NWB electrode metadata |
| `extract_unit_traces(session_id, conds, sigma)` | `str, list, float → dict` | Extracts Gaussian-smoothed (sigma=20ms) firing rate + variance traces per unit |
| `baseline_correct(traces, baseline_window)` | `array, tuple → array` | Subtracts mean fixation-window firing rate (default 0–1000ms window) |
| `compute_area_mmff(all_unit_stats, areas, conds, win_size, step)` | `dict → dict` | MMFF across areas/conditions with sliding window (WIN=150ms, STEP=5ms) |

## compute_mean_matched_fano — core functions
| Function | Purpose |
|---|---|
| `get_unit_to_area_map(nwb_path)` | Same as above — canonical version in `omission_hierarchy_utils` |
| `compute_mmff()` | Top-level orchestrator: reads NWB + NPY → runs mean-matching → saves JSON |

## neuro_variability_suite — core functions
| Function | Signature | Purpose |
|---|---|---|
| `apply_post_hoc_smoothing(trace, sigma)` | `array, float → array` | NaN-safe 1D Gaussian smoothing (sigma=2.0 default); interpolates before smooth, re-applies NaN mask |

## canonical workflow
```python
from codes.functions.omission_hierarchy_utils import (
    get_unit_to_area_map, extract_unit_traces,
    baseline_correct, compute_area_mmff
)
u_map  = get_unit_to_area_map("session.nwb")
traces = extract_unit_traces("230629", sigma=20)
traces = baseline_correct(traces)
mmff   = compute_area_mmff(traces)
```
