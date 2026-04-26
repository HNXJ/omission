---
name: science-neuro-omission-surprise-latencies
---
# science-neuro-omission-surprise-latencies

## Purpose
Quantifies temporal onset of surprise signals: sliding-window t-tests, persistence criterion, Z-thresholding, hierarchical comparison.

## Input
| Name | Type | Description |
|------|------|-------------|
| omit_psth | ndarray(T,) | 1ms binned PSTH for omission condition |
| std_psth | ndarray(T,) | 1ms binned PSTH for standard condition |
| baseline_win | tuple | Pre-event window for noise estimation |
| consecutive_bins | int | Persistence requirement (default: 20) |

## Output
| Name | Type | Description |
|------|------|-------------|
| onset_ms | int | First significant divergence timepoint |
| peak_ms | int | Maximum transient amplitude |
| hierarchy_order | list[str] | Areas sorted by detection speed |

## Expected Latencies
| Tier | Onset (ms) |
|------|-----------|
| FEF/PFC | 15-45 |
| V4/MT | 60-100 |
| V1 | 100-150 |

## Example
```python
def detect_onset(omit, std, n_consec=20, z_thresh=3.0):
    diff = omit - std
    baseline_sd = np.std(diff[:200])
    z = diff / (baseline_sd + 1e-9)
    # Find first of n_consec consecutive bins above threshold
    for i in range(len(z) - n_consec):
        if all(z[i:i+n_consec] > z_thresh):
            return i
    return None
print(f"""[result] PFC onset: {detect_onset(pfc_omit, pfc_std)}ms""")
```

## Files
- [latencies.py](file:///D:/drive/omission/src/analysis/latencies.py) — Onset detection
