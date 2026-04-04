---
name: analysis-poster-figures
description: Exact replication functions for every data figure in Poster 01 (Neural Dynamics/Spectral Omission) and Poster 02 (Neuronal Oscillations/Predictive Routing). All outputs are Plotly figures using the Madelane palette and plotly_white theme.
source: codes/functions/poster_figures.py
cross-ref: analysis-poster-figure-pipeline (data prep workflow)
---

# skill: analysis-poster-figures

## function → poster figure mapping

| Function | Poster | Section | What it makes |
|---|---|---|---|
| `plot_band_power_hierarchy(traces, sems, time_ms, ...)` | 01+02 | Main LFP figure | N_areas × 1 subplot grid; one band-power trace per condition per area; ±2SEM shading; pink omission rectangle |
| `plot_mua_tfr_panel(mua_traces, tfr_data, time_ms, ...)` | 01 | Section 4 | TFR heatmap + MUA trace per area per condition; confirms no V1/MT spiking change |
| `plot_spectral_corr_matrices(corr_stim, corr_omit, areas)` | 01 | Section 6 top | 1×2 heatmap: 11×11 inter-area Pearson-r in stimulus vs omission window |
| `plot_r2_change_bars(r2_change, areas)` | 01 | Section 6 bar | ΔR² per area; FEF/PFC highlighted as most stable spectral nodes |
| `plot_gamma_beta_dissociation(gamma_corr, beta_corr, areas)` | 01 | Section 6 mid | Side-by-side gamma vs beta correlation heatmaps during omission |
| `plot_spectral_network(adj_matrix, areas, ...)` | 01+02 | Network diagrams | Node-edge graph; edges weighted by inter-area coherence; beta=Violet, gamma=Gold |
| `plot_neuron_group_traces(group_traces, sems, time_ms, ...)` | 02 | Section 5 top | 3-row traces: N=2071 excited, N=1382 inhibited, N=20 omission-selective |
| `plot_omission_fraction_bars(fractions, areas)` | 02 | Section 5 bar | Grouped bars showing % of neurons per group per area; omission neurons in PFC/FEF |
| `plot_spectral_harmony_matrices(corr_stim, corr_omit, areas)` | 02 | Section 6 | 2×4 heatmaps: Theta/Alpha/Beta/Gamma × Stimulus/Omission; shows beta-gamma flip |
| `plot_beta_gamma_shift_bars(beta_corr, gamma_corr, ...)` | 02 | Section 6 bar | Grouped bars: beta vs gamma mean |r| in stimulus vs omission windows |

## visual standards (all figures)
- **Theme**: `plotly_white`, Arial font, black axes
- **Palette**: Gold=`#CFB87C`, Violet=`#8F00FF`, Pink=`#FF1493`, Teal=`#00FFCC`, Orange=`#FF5E00`
- **Condition colors**: RRRR=Gold, RXRR=Violet, RRXR=Teal, RRRX=Orange
- **Omission patch**: Pink `#FF1493` αα=0.22 over the specific omission window
- **Event patches**: SEQUENCE_TIMING from `lfp_constants.py` (p1=Gold, p2=Violet, p3=Teal, p4=Orange, delays=Gray)
- **SEM**: ±2SEM on all band-power and spiking traces
- **Export**: `.html` (interactive) AND `.svg` (vector) to `output/`

## key constants (poster_figures.py)
```python
AREA_ORDER = ["V1","V2","V4","MT","MST","TEO","FST","V3A","V3D","FEF","PFC"]
OMISSION_WINDOWS = {
    "RXRR": (531, 1562),   # omission at p2
    "RRXR": (1562, 2593),  # omission at p3
    "RRRX": (2593, 3624),  # omission at p4
}
```

## quick start — main figure (both posters)
```python
from codes.functions.poster_figures import plot_band_power_hierarchy, AREA_ORDER
fig = plot_band_power_hierarchy(
    traces=traces,       # {cond: {area: {'Beta': mean_array}}}
    sems=sems,           # {cond: {area: {'Beta': sem_array}}}
    time_ms=time_ms,
    areas=AREA_ORDER,
    conditions=['RRRR','RXRR','RRXR','RRRX'],
    band='Beta',
    omission_cond='RXRR',
    x_range=(-1000, 1500),
)
fig.write_html('output/fig-band-power-hierarchy.html')
fig.write_image('output/fig-band-power-hierarchy.svg')
```
