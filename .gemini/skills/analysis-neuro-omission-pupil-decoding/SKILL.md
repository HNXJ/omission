---
name: analysis-neuro-omission-pupil-decoding
description: "Omission analysis skill focusing on analysis neuro omission pupil decoding."
---

# Pupil Decoding Methodology

Pupil diameter is a sensitive index of arousal, cognitive load, and surprise. We extract identity (A vs B) and omission (X) information from pupillometry signals.

Temporal Dynamics:
The pupil response is slow compared to neural signals, with peak dilation occurring 400-800ms after the event. In our task, stimuli are presented at 2Hz (every 500ms). This requires careful deconvolution or window-based decoding to separate the effects of sequential presentations.

Methodology:
1. Signal Conditioning: Remove blinks, Z-score within trial, and baseline-correct to the pre-P1 window.
2. Feature Extraction: Mean diameter, peak velocity of dilation, and area under the curve.
3. Decoding: Use SVM to classify A vs B vs R based on the temporal profile of the pupil.

Findings:
We found that the pupil dilates significantly more during omissions (surprise) than during standard presentations. Interestingly, the pupil also carries stimulus identity information, even when the subject is not required to perform any action other than fixation.

Technical Snippet:
```python
import numpy as np
def process_pupil(pupil_data):
    # Z-score and baseline subtraction
    z_pupil = (pupil_data - np.mean(pupil_data)) / np.std(pupil_data)
    baseline = np.mean(z_pupil[0:100])
    return z_pupil - baseline
```

References:
1. Joshi, S., et al. (2016). Relationships between Pupil Diameter and Neuronal Activity in the Locus Coeruleus, Colliculi, and Cingulate Cortex. Neuron.
2. Preuschoff, K., et al. (2011). Pupil dilation signals surprise: Evidence for noradrenergic modulation of decision making. Frontiers in Neuroscience.
