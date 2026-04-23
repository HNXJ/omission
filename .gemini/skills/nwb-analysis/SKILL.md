---
name: nwb-analysis
---
# nwb-analysis

## Purpose
Primary NWB data pipeline: spike/LFP alignment, MMFF calculation (Churchland 2010), 48-factor manifold extraction, probe-local mapping rules. Absorbs `neuro-analysis` population analysis.

## Mandatory Rules
- Alignment: Code 101.0 (p1 onset), window: -1000 to +5000ms
- Probe mapping: `probe_id = peak_channel_id // 128`
- Area normalization: DP→V4, V3→split V3d/V3a at 50%
- Loading: `mmap_mode='r'` always
- Stable-Plus filter: FR>1Hz, SNR>0.8, 100% trial presence

## Input
| Name | Type | Description |
|------|------|-------------|
| nwb_files | list[str] | NWB session paths |
| timing_codes | dict | Event markers (Code 101.0 = p1 onset) |
| processing_config | dict | `{window: 100ms, step: 5ms, sigma: 50ms}` |

## Output
| Name | Type | Description |
|------|------|-------------|
| aligned_tensors | ndarray(T, N, S) | Trials × Neurons × Time |
| mmff_traces | dict | Per-area Fano Factor curves |
| unit_labels | dict | S+/O+ classification |

## Example
```python
aligned = nwb_loader.get_aligned_window(event='p2', pre_ms=500, post_ms=1000)
ff_trace = mmff.compute(aligned, window=100, step=5)
smoothed = gaussian_filter1d(ff_trace, sigma=2)
print(f"""[result] MMFF trace shape: {smoothed.shape}""")
```

## Files
- [nwb_loader.py](file:///D:/drive/omission/src/data/nwb_loader.py) — Canonical loader
