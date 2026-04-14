---
name: analysis-neuro-omission-oculomotor-suite
description: "Omission analysis skill focusing on analysis neuro omission oculomotor suite."
---

# Oculomotor Analysis Suite

Eye movements are a direct readout of attention and internal state. Our suite provides a full pipeline for analyzing saccades, microsaccades, and pupillometry in the context of visual omissions.

Calibration:
Visual stimuli are projected 57cm from the eyes. We calibrate eye signals into Degrees of Visual Angle (DVA). 1 degree = screen_dist * tan(1 deg). At 57cm, 1 degree is approximately 1cm on the screen.

Metrics:
1. Saccades: Velocity > 30 DVA/s, Amplitude > 1.5°.
2. Microsaccades: Small (<1.5°) movements during fixation.
3. Directionality: We use rose plots to analyze whether eye movements are biased toward or away from the stimulus orientation (45° vs 135°).

Validation Protocols:
- Photodiode Sync: Aligning eye traces to the physical stimulus onset.
- Fixation Stability: Ensuring TrialError == 0 (Fixation maintained within 1.5°).

Technical Implementation:
```python
import numpy as np
def detect_saccades(eye_x, eye_y, fs=1000, thresh=30):
    vx = np.gradient(eye_x) * fs
    vy = np.gradient(eye_y) * fs
    vel = np.sqrt(vx**2 + vy**2)
    saccade_indices = np.where(vel > thresh)[0]
    return saccade_indices
```

References:
1. Engbert, R., & Kliegl, R. (2003). Microsaccades uncover the orientation of covert attention. Vision Research.
2. Martinez-Conde, S., et al. (2004). The role of fixational eye movements in visual perception. Nature Reviews Neuroscience.
