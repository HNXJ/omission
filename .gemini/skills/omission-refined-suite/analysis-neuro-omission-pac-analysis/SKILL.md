# Phase-Amplitude Coupling (PAC)

Phase-Amplitude Coupling (PAC) describes how the phase of a low-frequency oscillation (e.g., Theta 4-8Hz) modulates the amplitude of a high-frequency oscillation (e.g., Gamma 40-100Hz). This is thought to be a mechanism for organizing information flow across different scales.

Methodology (Tort et al., 2010):
We use the Modulation Index (MI) to quantify PAC. The process involves:
1. Filtering the signal into Theta and Gamma bands.
2. Extracting the phase of Theta (Hilbert transform) and the amplitude envelope of Gamma.
3. Calculating the distribution of Gamma amplitude across Theta phase bins (0 to 360°).
4. Quantifying the deviation from a uniform distribution using KL-divergence.

Application:
During omission detection, Theta-Gamma coupling in the PFC increases significantly. The Theta phase may provide the temporal framework for the discrete updates of the internal generative model.

Code Example:
```python
import numpy as np
def calculate_mi(phase, amplitude, n_bins=18):
    bins = np.linspace(-np.pi, np.pi, n_bins+1)
    mean_amp = []
    for i in range(n_bins):
        mask = (phase >= bins[i]) & (phase < bins[i+1])
        if np.any(mask):
            mean_amp.append(np.mean(amplitude[mask]))
        else:
            mean_amp.append(0)
    p = np.array(mean_amp) / (np.sum(mean_amp) + 1e-12)
    p = p + 1e-12
    h = -np.sum(p * np.log(p))
    mi = (np.log(n_bins) - h) / np.log(n_bins)
    return mi
```

References:
1. Tort, A. B. L., et al. (2010). Measuring phase-amplitude coupling between neuronal oscillations of different frequencies. Journal of Neurophysiology.
2. Canolty, R. T., & Knight, R. T. (2010). The functional role of cross-frequency coupling. Trends in Cognitive Sciences.
