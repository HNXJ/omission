# PFC as a Surprise Detection Hub

The Prefrontal Cortex (PFC) and Frontal Eye Fields (FEF) serve as primary hubs for the detection of prediction errors. In our sequential task, a prediction error (surprise) occurs when the expected stimulus is omitted.

The Oddball Effect:
The 'Oddball' effect refers to the enhanced neural response to rare or unexpected stimuli. In our design, P4 in RRRR is a standard event, while P4 in AAAX is an omission (surprise). We contrast the magnitude of the surprise transient across different positions in the sequence (P2 vs P3 vs P4).

Observations:
1. Magnitude: Omission transients in PFC are often 2-3x larger than the baseline firing rate.
2. Timing: The response onset is extremely rapid (~20ms), suggesting an anticipatory or very fast generative process.
3. Scaling: The surprise signal scales with the strength of the expectation. A violation of a long sequence (P4) often triggers a stronger response than an early violation (P2).

Active Inference Interpretation:
The PFC response is a physical manifestation of the update to the internal generative model. It represents the divergence between the predicted state and the observed state (Null).

Technical Analysis:
```python
import numpy as np
def quantify_surprise_transient(psth_omit, psth_standard):
    # Difference in peak firing rate within 0-200ms
    peak_omit = np.max(psth_omit[0:200])
    peak_std = np.max(psth_standard[0:200])
    return (peak_omit - peak_std) / (peak_std + 1.0)
```

References:
1. Garrido, M. I., et al. (2009). The mismatch negativity: A review of underlying mechanisms. Clinical Neurophysiology.
2. Stefanics, G., et al. (2014). Visual mismatch negativity: A predictive coding view. Frontiers in Human Neuroscience.
