---
name: hardware-neuro-omission-lab-infrastructure
---
# hardware-neuro-omission-lab-infrastructure

## Purpose
Physical recording environment spec: DVA calibration, photodiode timing corrections, eye-tracking hardware, electrode channel maps.

## Key Constants
| Parameter | Value | Formula |
|-----------|-------|---------|
| Subject distance | 57 cm | — |
| DVA conversion | 1 cm = 1° at 57cm | `θ = 2 * arctan(w / 2d)` |
| Photodiode offset | ~8ms fixed | Cross-correlate strobe vs frame flip |
| Channels/probe | 128 | Neuropixels standard |

## Example
```python
px_per_cm = 1920 / 52  # screen width in cm
dva = px / px_per_cm  # simplified at 57cm
print(f"""[result] {px}px = {dva:.2f} DVA""")
```

## Files
- [timing_checks.py](file:///D:/drive/omission/src/calibration/timing_checks.py) — Photodiode validation
