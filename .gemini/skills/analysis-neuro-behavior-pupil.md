---
name: analysis-neuro-behavior-pupil
description: "Oculomotor precision analysis (DVA) and pupil dynamics from raw MonkeyLogic sources."
version: 1.0
---

## ## Context
Quantifies the behavioral fingerprints of Active Inference during sequential visual omission.

## ## Rules
- **Eye Source**: Always use raw `.mat` BHV files (`bhvUni.AnalogData.Eye`).
- **Units**: Degrees of Visual Angle (DVA).
- **Alignment**: Code 101 (P1 Onset).
- **Metrics**: 
    - **Precision**: XY Variance within 1531ms omission window.
    - **Saccades**: Velocity threshold > 30°/s.
    - **Jitter**: High-frequency micro-oscillations.
- **Pupil**: Analyze baseline-normalized pupil dilation (Arousal/Surprise).
- **Inference**: Test for precision-scaling (quenching) after omission.

## ## Examples
```python
# Eye Precision Metric
total_var = np.var(eye_x) + np.var(eye_y)
# Velocity Thresholding
vel = np.sqrt(np.gradient(x)**2 + np.gradient(y)**2) * FS
```

# # Keywords:
# Eye Precision, DVA, Saccades, Microsaccades, Pupil Dilation, Oculomotor, Jitter, Active Inference.
