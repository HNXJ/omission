---
name: science-neuro-omission-spectral-fingerprints
---
# science-neuro-omission-spectral-fingerprints

## Purpose
Dissociates FF (Gamma >40Hz) and FB (Beta 15-30Hz) spectral channels during omissions. Detects Gamma quenching and Surprise Beta transients.

## Band Definitions
| Band | Range | Interpretation |
|------|-------|----------------|
| Gamma | 40-80 Hz | Bottom-up sensory drive; vanishes during omissions |
| Beta | 15-30 Hz | Top-down priors; surges in PFC during surprise |
| Alpha | 8-12 Hz | Inhibition / gain modulation |

## Input
| Name | Type | Description |
|------|------|-------------|
| lfp_raw | ndarray(T,) | Condition-aligned voltage (1kHz) |
| laminar_depth | list[int] | Channel→layer mapping |

## Output
| Name | Type | Description |
|------|------|-------------|
| power_spectra | dict | Per-band average power |
| contrast_map | ndarray(F, T) | Omission - Standard power difference |

## Example
```python
from scipy.signal import spectrogram
f, t, Sxx = spectrogram(lfp, fs=1000)
gamma = np.mean(Sxx[(f>=40)&(f<=80),:], axis=0)
beta = np.mean(Sxx[(f>=15)&(f<=30),:], axis=0)
print(f"""[result] Gamma mean={gamma.mean():.4f}, Beta mean={beta.mean():.4f}""")
```

## Files
- [wavelet_transform.py](file:///D:/drive/omission/src/spectral/wavelet_transform.py) — Decomposition
