---
name: coding-neuro-omission-signal-conditioning
description: "Omission analysis skill focusing on coding neuro omission signal conditioning."
---

# Signal Conditioning & Preprocessing

Standardized signal conditioning ensures that neural data is comparable across sessions and units.

Procedures:
1. Spike Smoothing: Convert binary spike trains into continuous Peristimulus Time Histograms (PSTH) using a Gaussian kernel (sigma = 10ms or 20ms).
2. Z-Scoring: Normalize firing rates to have mean=0 and std=1, typically using the pre-stimulus baseline (Sample 0-1000).
3. LFP Filtering: 
   - Broad-band: 1-300Hz.
   - Notch Filter: 60Hz (to remove line noise).
   - Band-specific: Alpha (8-12Hz), Beta (15-30Hz), Gamma (40-100Hz).
4. MUAe Extraction: Rectify and low-pass filter the high-frequency signal (>1000Hz).

Technical Implementation:
```python
from scipy.ndimage import gaussian_filter1d
import numpy as np

def get_psth(spikes, sigma=20):
    # spikes: (trials, time)
    psth = gaussian_filter1d(spikes.astype(float), sigma=sigma, axis=1)
    return psth * 1000 # convert to Hz if bin=1ms

def z_score_signal(signal, baseline_window=(0, 1000)):
    mu = np.mean(signal[:, baseline_window[0]:baseline_window[1]])
    sd = np.std(signal[:, baseline_window[0]:baseline_window[1]])
    return (signal - mu) / (sd + 1e-9)
```

References:
1. Dayan, P., & Abbott, L. F. (2001). Theoretical Neuroscience: Computational and Mathematical Modeling of Neural Systems. MIT Press.
2. Pesaran, B., et al. (2018). Investigating Large-Scale Brain Dynamics Using Field Potentials, Spikes, and Spacing. Annual Review of Neuroscience.
