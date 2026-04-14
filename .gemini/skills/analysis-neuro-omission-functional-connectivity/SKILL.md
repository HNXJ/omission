---
name: analysis-neuro-omission-functional-connectivity
description: "Omission analysis skill focusing on analysis neuro omission functional connectivity."
---

# Functional Connectivity: Coherence & PLV

Functional connectivity measures the synchronization between different brain areas, revealing the network-level coordination during omissions.

Metrics:
1. Coherence: Frequency-domain correlation between two LFP signals. Indicates consistent phase and amplitude relationships.
2. Phase-Locking Value (PLV): Measures the consistency of the phase difference between signals, independent of amplitude.

Observations:
During omissions, we observe an increase in V1-PFC coherence in the Gamma band (40-60Hz). This is paradoxical because Gamma is usually bottom-up. However, this 'Omission Gamma' may represent the high-frequency matching process between the top-down prediction and the (null) bottom-up input.

Technical Pipeline:
- Segment LFP into omission windows.
- Compute Cross-Spectral Density (CSD).
- Normalize CSD to get Coherence.

Code Snippet:
```python
from scipy.signal import coherence
def get_coherence(sig1, sig2, fs=1000):
    f, Cxy = coherence(sig1, sig2, fs=fs, nperseg=256)
    return f, Cxy
```

References:
1. Fries, P. (2015). Rhythms for Cognition: Communication through Coherence. Neuron.
2. Bastos, A. M., & Schoffelen, J. M. (2016). A Tutorial Review of Functional Connectivity Analysis Methods and Their Interpretational Pitfalls. Frontiers in Systems Neuroscience.
