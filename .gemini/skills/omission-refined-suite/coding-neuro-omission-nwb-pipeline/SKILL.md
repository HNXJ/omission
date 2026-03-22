# NWB Loading and Alignment Pipeline

Our neurophysiology pipeline standardizes data access from NWB (.npy) files. Consistency in alignment and windowing is critical for cross-session comparisons.

Standard Parameters:
- Alignment Reference: Code 101.0 (Onset of Presentation 1).
- Window: 6000ms total.
- Buffer: 1000ms pre-stimulus (relative to Code 101.0).
- Sampling: 1000Hz (1ms bins).

File Structure:
Data is typically stored as `ses-YYYYMMDD-units-probeX-spk-CONDITION.npy`. These files are pre-filtered for Correct Trials (TrialError == 0).

Technical Implementation:
```python
import numpy as np
import os

def load_nwb_signal(session, condition, area_units):
    # area_units: dict mapping areas to unit indices
    path = f'data/ses{session}-units-spk-{condition}.npy'
    data = np.load(path) # Shape: (trials, units, 6000)
    
    subset = {}
    for area, units in area_units.items():
        subset[area] = data[:, units, :]
    return subset

# Example: Accessing P2 onset (Sample 1531)
# P1=1000, D1=531ms -> P2=1531
```

Validation:
We always check for a 40-60ms lag in V1 firing rates relative to Sample 1000 (Photodiode onset) to ensure synchronization integrity.

References:
1. Teeters, J. L., et al. (2015). Neurodata Without Borders: An Open Format for Sharing Neurophysiology Data. Neuron.
2. Rübel, O., et al. (2022). The Neurodata Without Borders ecosystem for neurophysiology. eLife.
